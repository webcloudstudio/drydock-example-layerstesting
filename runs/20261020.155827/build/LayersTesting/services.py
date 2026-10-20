"""Transactional ledger use cases."""
from __future__ import annotations
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from persistence import Database
from persistence.schema import Account, Category, Transaction
from validation import validate_code, validate_date
from validation import validate_label


class InputFileError(RuntimeError):
    """The requested input file could not be read as an input resource."""

def _ready(db: Database) -> None:
    """Support direct service use with an uninitialized test store."""
    db.execute_script((Path(__file__).resolve().parent / "schema.sql").read_text(encoding="utf-8"))

def cents(value: str) -> int:
    try: amount = Decimal(value)
    except (InvalidOperation, TypeError): raise ValueError("invalid amount") from None
    if not amount.is_finite() or amount.as_tuple().exponent < -2: raise ValueError("invalid amount")
    return int(amount * 100)

def create_account(db: Database, code: str, name: str) -> Account:
    _ready(db)
    with db.transaction(): return db.accounts.create(account=validate_code(code), name=name)

def update_account(db: Database, code: str, name: str) -> None:
    _ready(db)
    with db.transaction():
        if not db.accounts.update(account=validate_code(code), name=name): raise LookupError("account not found")

def delete_account(db: Database, code: str) -> None:
    _ready(db)
    with db.transaction():
        if not any(row.account == code for row in db.accounts.list()): raise LookupError("account not found")
        db.accounts.delete(account=validate_code(code))

def create_category(db: Database, code: str, description: str) -> Category:
    _ready(db)
    with db.transaction(): return db.categories.create(category=validate_code(code), description=description)

def create_transaction(db: Database, txn_id: int, txn_date: str, account: str, category: str, amount: int, memo: str = "") -> Transaction:
    _ready(db)
    validate_date(txn_date); validate_code(account); validate_code(category)
    with db.transaction():
        balance = sum(row.amount for row in db.transactions.list() if row.account == account)
        if balance + amount < 0: raise ValueError("account balance cannot be negative")
        return db.transactions.create(txn_id=txn_id, date=txn_date, account=account, category=category, amount=amount, memo=memo)

def update_transaction(db: Database, txn_id: int, amount: int) -> Transaction:
    _ready(db)
    with db.transaction():
        row = next((item for item in db.transactions.list() if item.txn_id == txn_id), None)
        if row is None: raise LookupError("transaction not found")
        balance = sum(item.amount for item in db.transactions.list() if item.account == row.account) - row.amount
        if balance + amount < 0: raise ValueError("account balance cannot be negative")
        db.transactions.update(txn_id=txn_id, amount=amount)
        return next(item for item in db.transactions.list() if item.txn_id == txn_id)

def delete_transaction(db: Database, txn_id: int) -> None:
    _ready(db)
    with db.transaction():
        row = next((item for item in db.transactions.list() if item.txn_id == txn_id), None)
        if row is None: raise LookupError("transaction not found")
        if sum(item.amount for item in db.transactions.list() if item.account == row.account) - row.amount < 0: raise ValueError("account balance cannot be negative")
        db.transactions.delete(txn_id=txn_id)

def load_csv(db: Database, table: str, filename: str) -> int:
    _ready(db)
    headers = {
        "accounts": ("account", "name"),
        "categories": ("category", "description"),
        "transactions": ("txn_id", "date", "account", "category", "amount", "memo"),
    }
    if table not in headers:
        raise ValueError("invalid table")
    try:
        with Path(filename).open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle, strict=True)
            actual_header = next(reader, None)
            if actual_header != list(headers[table]):
                raise ValueError("invalid CSV header")
            rows = []
            for values in reader:
                if len(values) != len(headers[table]):
                    raise ValueError("invalid CSV row")
                rows.append(dict(zip(headers[table], values, strict=True)))
    except (OSError, UnicodeError) as exc:
        raise InputFileError("unable to read input file") from exc
    except csv.Error as exc:
        raise ValueError("invalid CSV") from exc

    if table == "accounts":
        for row in rows:
            validate_code(row["account"])
            validate_label(row["name"])
        keys = [row["account"] for row in rows]
        if len(keys) != len(set(keys)) or any(existing.account in set(keys) for existing in db.accounts.list()):
            raise ValueError("duplicate account")
    elif table == "categories":
        for row in rows:
            validate_code(row["category"])
            validate_label(row["description"])
        keys = [row["category"] for row in rows]
        if len(keys) != len(set(keys)) or any(existing.category in set(keys) for existing in db.categories.list()):
            raise ValueError("duplicate category")

    if table == "transactions":
        account_codes = {account.account for account in db.accounts.list()}
        category_codes = {category.category for category in db.categories.list()}
        existing_ids = {transaction.txn_id for transaction in db.transactions.list()}
        batch_ids: set[int] = set()
        balances = {
            account: sum(transaction.amount for transaction in db.transactions.list() if transaction.account == account)
            for account in account_codes
        }
        validated_transactions: list[dict[str, object]] = []

        for row in rows:
            try:
                txn_id = int(row["txn_id"])
            except (TypeError, ValueError):
                raise ValueError("invalid transaction id") from None
            if txn_id <= 0 or txn_id in existing_ids or txn_id in batch_ids:
                raise ValueError("duplicate transaction id")
            batch_ids.add(txn_id)

            txn_date = validate_date(row["date"])
            account = validate_code(row["account"])
            category = validate_code(row["category"])
            if account not in account_codes:
                raise ValueError("unknown account")
            if category not in category_codes:
                raise ValueError("unknown category")
            amount = cents(row["amount"])
            if balances[account] + amount < 0:
                raise ValueError("account balance cannot be negative")
            balances[account] += amount
            validated_transactions.append({
                "txn_id": txn_id,
                "date": txn_date,
                "account": account,
                "category": category,
                "amount": amount,
                "memo": row["memo"],
            })

        rows = validated_transactions

    with db.transaction():
        if table == "accounts":
            for row in rows: db.accounts.create(account=validate_code(row["account"]), name=row["name"])
        elif table == "categories":
            for row in rows: db.categories.create(category=validate_code(row["category"]), description=row["description"])
        elif table == "transactions":
            for row in rows:
                db.transactions.create(
                    txn_id=row["txn_id"],
                    date=row["date"],
                    account=row["account"],
                    category=row["category"],
                    amount=row["amount"],
                    memo=row["memo"],
                )
        else:
            for row in rows:
                amount = cents(row["amount"]); balance = sum(item.amount for item in db.transactions.list() if item.account == row["account"])
                if balance + amount < 0: raise ValueError("account balance cannot be negative")
                db.transactions.create(txn_id=int(row["txn_id"]), date=validate_date(row["date"]), account=validate_code(row["account"]), category=validate_code(row["category"]), amount=amount, memo=row["memo"])
    return len(rows)

def initialize(db: Database) -> None:
    """Atomically remove every ledger row, leaving the declared schema empty."""
    _ready(db)
    with db.transaction():
        for row in db.transactions.list(): db.transactions.delete(txn_id=row.txn_id)
        for row in db.accounts.list(): db.accounts.delete(account=row.account)
        for row in db.categories.list(): db.categories.delete(category=row.category)


def count_rows(db: Database) -> list[tuple[str, int]]:
    """Return declared ledger tables and their current row counts in report order."""
    _ready(db)
    return [(name, len(getattr(db, name).list())) for name in ("accounts", "categories", "transactions")]

def record_transaction(db: Database, txn_id: int, txn_date: str, account: str, category: str, amount_cents: int, memo: str = "") -> Transaction:
    return create_transaction(db, txn_id, txn_date, account, category, amount_cents, memo)
