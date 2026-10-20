"""Ledger command services; persistence details remain behind ``persistence``."""

from __future__ import annotations

import csv
from pathlib import Path
from collections import defaultdict

from config import database_dsn
from persistence import open_database
from validation import ValidationError, amount_cents, code, ledger_date, memo, name as validate_name


class OperationalError(RuntimeError):
    """A command could not access or read an external input."""


def initialize(environ: dict[str, str] | None = None) -> None:
    db = open_database(database_dsn(environ))
    try:
        db.initialize(drop_existing=True)
    finally:
        db.close()


def counts(environ: dict[str, str] | None = None) -> dict[str, int]:
    db = open_database(database_dsn(environ))
    try:
        db.initialize()
        return db.counts()
    finally:
        db.close()


def add_account(account: str, name: str, environ: dict[str, str] | None = None) -> None:
    """Create an account through the declared persistence operation."""
    account = code(account, label="account")
    name = validate_name(name)
    db = open_database(database_dsn(environ))
    try:
        db.initialize()
        db.accounts.create(account=account, name=name)
    finally:
        db.close()


def load_reference(
    table: str, filename: str, environ: dict[str, str] | None = None
) -> int:
    """Validate a complete reference CSV before inserting its rows."""
    expected = {
        "accounts": ("account", "name"),
        "categories": ("category", "description"),
    }.get(table)
    if expected is None:
        raise ValidationError("invalid reference table")

    rows: list[tuple[str, str]] = []
    keys: set[str] = set()
    try:
        with Path(filename).open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle, strict=True)
            header = next(reader, None)
            if header != list(expected):
                raise ValidationError("invalid CSV header")
            for fields in reader:
                if len(fields) != 2:
                    raise ValidationError("invalid CSV row")
                key = code(fields[0], label=expected[0])
                text = validate_name(fields[1])
                if key in keys:
                    raise ValidationError("duplicate reference key")
                keys.add(key)
                rows.append((key, text))
    except FileNotFoundError as exc:
        raise OperationalError("reference file is unreadable") from exc
    except (OSError, UnicodeError, csv.Error) as exc:
        raise OperationalError("reference file is unreadable") from exc

    db = open_database(database_dsn(environ))
    try:
        db.initialize()
        for key, _ in rows:
            existing = (
                db.accounts.get(account=key)
                if table == "accounts"
                else db.categories.get(category=key)
            )
            if existing is not None:
                raise ValidationError("duplicate reference key")
        for key, text in rows:
            if table == "accounts":
                db.accounts.create(account=key, name=text)
            else:
                db.categories.create(category=key, description=text)
    finally:
        db.close()
    return len(rows)


def post_transaction(
    account: str,
    category: str,
    amount: str,
    transaction_date: str,
    transaction_memo: str = "",
    environ: dict[str, str] | None = None,
) -> object:
    """Validate a transaction completely before issuing its persistence write."""
    account = code(account, label="account")
    category = code(category, label="category")
    cents = amount_cents(amount)
    transaction_date = ledger_date(transaction_date)
    transaction_memo = memo(transaction_memo)

    db = open_database(database_dsn(environ))
    try:
        db.initialize()
        if db.accounts.get(account=account) is None:
            raise ValidationError("unknown account")
        # Category lookup is a declared operation when the category service is present.  Older
        # generated schemas may not expose it yet; either way an unavailable reference is rejected
        # before the transaction create is reached.
        try:
            category_row = db.categories.get(category=category)
        except Exception as exc:  # persistence translates undeclared lookups at this boundary
            raise ValidationError("unknown category") from exc
        if category_row is None:
            raise ValidationError("unknown category")
        return db.transactions.create(
            date=transaction_date,
            account=account,
            category=category,
            amount=cents,
            memo=transaction_memo,
        )
    finally:
        db.close()


def load_transactions(
    filename: str, environ: dict[str, str] | None = None
) -> int:
    """Validate and load a complete transaction CSV batch."""
    rows: list[tuple[int, str, str, str, int, str]] = []
    identifiers: set[int] = set()
    try:
        with Path(filename).open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle, strict=True)
            header = next(reader, None)
            if header != ["txn_id", "date", "account", "category", "amount", "memo"]:
                raise ValidationError("invalid CSV header")
            for fields in reader:
                if len(fields) != 6:
                    raise ValidationError("invalid CSV row")
                try:
                    transaction_id = int(fields[0])
                except (TypeError, ValueError):
                    raise ValidationError("invalid transaction id") from None
                if transaction_id <= 0 or str(transaction_id) != fields[0]:
                    raise ValidationError("invalid transaction id")
                if transaction_id in identifiers:
                    raise ValidationError("duplicate transaction id")
                identifiers.add(transaction_id)
                rows.append(
                    (
                        transaction_id,
                        ledger_date(fields[1]),
                        code(fields[2], label="account"),
                        code(fields[3], label="category"),
                        amount_cents(fields[4]),
                        memo(fields[5]),
                    )
                )
    except FileNotFoundError as exc:
        raise OperationalError("transaction file is unreadable") from exc
    except (OSError, UnicodeError, csv.Error) as exc:
        raise OperationalError("transaction file is unreadable") from exc

    db = open_database(database_dsn(environ))
    try:
        db.initialize()
        for transaction_id, *_ in rows:
            if db.transactions.get(txn_id=transaction_id) is not None:
                raise ValidationError("duplicate transaction id")
        for _, _, account, category, _, _ in rows:
            if db.accounts.get(account=account) is None:
                raise ValidationError("unknown account")
            if db.categories.get(category=category) is None:
                raise ValidationError("unknown category")

        balances: defaultdict[str, int] = defaultdict(int)
        existing_count = db.counts()["transactions"]
        for transaction_id in range(1, existing_count + 1):
            existing = db.transactions.get(txn_id=transaction_id)
            if existing is not None:
                balances[existing.account] += existing.amount

        for _, _, account, _, cents, _ in rows:
            balances[account] += cents
        for balance in balances.values():
            if balance < 0:
                raise ValidationError("negative account balance")

        for transaction_id, transaction_date, account, category, cents, transaction_memo in rows:
            db.transactions.create(
                txn_id=transaction_id,
                date=transaction_date,
                account=account,
                category=category,
                amount=cents,
                memo=transaction_memo,
            )
    finally:
        db.close()
    return len(rows)

