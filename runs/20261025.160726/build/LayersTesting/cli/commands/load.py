"""``ledger load``: read one CSV file whole, validate every row, then store every row or none.

Every check runs before the first write. The persistence package offers no multi-statement
transaction to application code, so the all-or-nothing guarantee rests on that ordering.
"""

import csv

from cli.context import open_store
from cli.core import (
    balance_guard,
    parse_amount,
    validate_code,
    validate_date,
    validate_memo,
    validate_name,
)
from cli.errors import OperationalError, Rejected
from cli.registry import register
from cli.views import (
    ACCOUNT_COLUMNS,
    CATEGORY_COLUMNS,
    LOADED_HEADER,
    TXN_COLUMNS,
    Txn,
    load_txn_id,
)


def load_accounts(args: list[str]) -> list[list[str]]:
    (path,) = args
    body = _read(path, ACCOUNT_COLUMNS)
    for code, name in body:
        validate_code(code)
        validate_name(name)
    with open_store() as db:
        stored = {account.account for account in db.accounts.list()}
        _reject_repeats([code for code, _ in body], stored)
        for code, name in body:
            db.accounts.create(account=code, name=name)
    return [LOADED_HEADER, ["accounts", str(len(body))]]


def load_categories(args: list[str]) -> list[list[str]]:
    (path,) = args
    body = _read(path, CATEGORY_COLUMNS)
    for code, description in body:
        validate_code(code)
        validate_name(description)
    with open_store() as db:
        stored = {category.category for category in db.categories.list()}
        _reject_repeats([code for code, _ in body], stored)
        for code, description in body:
            db.categories.create(category=code, description=description)
    return [LOADED_HEADER, ["categories", str(len(body))]]


def load_transactions(args: list[str]) -> list[list[str]]:
    (path,) = args
    txns = [_parse_txn(row) for row in _read(path, TXN_COLUMNS)]
    with open_store() as db:
        accounts = {account.account for account in db.accounts.list()}
        categories = {category.category for category in db.categories.list()}
        for txn in txns:
            if txn.account not in accounts:
                raise Rejected(f"unknown account {txn.account}")
            if txn.category not in categories:
                raise Rejected(f"unknown category {txn.category}")
        stored = {txn.txn_id for txn in db.transactions.list()}
        _reject_repeats([txn.txn_id for txn in txns], stored)
        deltas: dict[str, int] = {}
        for txn in txns:
            deltas[txn.account] = deltas.get(txn.account, 0) + txn.amount
        balance_guard(db, deltas)
        for txn in txns:
            db.transactions.create(**txn._asdict())
    return [LOADED_HEADER, ["transactions", str(len(txns))]]


def _parse_txn(row: list[str]) -> Txn:
    txn_id, day, account, category, amount, memo = row
    return Txn(
        txn_id=load_txn_id(txn_id),
        date=validate_date(day),
        account=validate_code(account),
        category=validate_code(category),
        amount=parse_amount(amount),
        memo=validate_memo(memo),
    )


def _read(path: str, columns: list[str]) -> list[list[str]]:
    """Return the body rows of ``path`` once its header and field counts check out."""
    try:
        with open(path, newline="", encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise OperationalError(f"cannot read {path}: {exc}") from exc
    if not rows or rows[0] != columns:
        raise Rejected(f"header must be {','.join(columns)}")
    body = rows[1:]
    for number, row in enumerate(body, start=2):
        if len(row) != len(columns):
            raise Rejected(f"line {number} must have {len(columns)} fields")
    return body


def _reject_repeats(keys: list, stored: set) -> None:
    """Refuse a key that repeats inside the file or is already stored."""
    seen: set = set()
    for key in keys:
        if key in seen:
            raise Rejected(f"{key} repeats in the file")
        if key in stored:
            raise Rejected(f"{key} is already stored")
        seen.add(key)


register(("load", "accounts"), load_accounts, (1, 1))
register(("load", "categories"), load_categories, (1, 1))
register(("load", "transactions"), load_transactions, (1, 1))
