"""Service boundary for validation, workflows, and report calculations.

Concrete workflows belong here and receive a database opened by the shipped
``persistence`` package.  This module deliberately contains no database-driver
imports or direct engine access.
"""

from __future__ import annotations

from argparse import Namespace
import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re
import sys
from typing import Callable

from persistence import open_database

from .errors import NotFoundError, RejectedError, UsageError


CommandHandler = Callable[..., int]

_TABLES = ("accounts", "categories", "transactions")
_CODE = re.compile(r"[A-Z0-9]{1,12}\Z")
_AMOUNT = re.compile(r"^[+-]?\d+(?:\.\d{1,2})?\Z")
_HEADERS = {
    "accounts": ("account", "name"),
    "categories": ("category", "description"),
    "transactions": ("txn_id", "date", "account", "category", "amount", "memo"),
}


def _schema_path() -> Path:
    return Path(__file__).resolve().parent.parent / "schema.sql"


def initialize_schema(database_dsn: str) -> int:
    """Reset the declared schema through the shipped persistence boundary."""

    drop_statements = """
    DROP TABLE IF EXISTS "transactions";
    DROP TABLE IF EXISTS "categories";
    DROP TABLE IF EXISTS "accounts";
    """
    with open_database(database_dsn) as database:
        database.execute_script(drop_statements + _schema_path().read_text(encoding="utf-8"))
    return 0


def count_rows(database_dsn: str) -> int:
    """Print live row counts in the documented table order."""

    with open_database(database_dsn) as database:
        counts = {
            "accounts": len(database.accounts.list()),
            "categories": len(database.categories.list()),
            "transactions": len(database.transactions.list()),
        }
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(("table", "rows"))
    for table in _TABLES:
        writer.writerow((table, counts[table]))
    return 0


def _text(value: str, maximum: int, label: str, *, empty: bool = False) -> str:
    if (not empty and not 1 <= len(value) <= maximum) or (empty and len(value) > maximum):
        raise RejectedError(f"invalid {label}")
    return value


def _code(value: str, label: str) -> str:
    if not _CODE.fullmatch(value):
        raise RejectedError(f"invalid {label}")
    return value


def _cents(value: str) -> int:
    if not _AMOUNT.fullmatch(value):
        raise RejectedError("invalid amount")
    try:
        amount = Decimal(value)
    except InvalidOperation as error:
        raise RejectedError("invalid amount") from error
    return int(amount * 100)


def _formatted_cents(amount: int) -> str:
    sign = "-" if amount < 0 else ""
    absolute = abs(amount)
    return f"{sign}{absolute // 100}.{absolute % 100:02d}"


def _date(value: str) -> str:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise RejectedError("invalid date") from error
    if parsed.isoformat() != value:
        raise RejectedError("invalid date")
    return value


def _arguments(args: Namespace, count: int, label: str) -> list[str]:
    if len(args.arguments) != count:
        raise UsageError(f"{label} requires {count} arguments")
    return args.arguments


def _print_row(values: tuple[object, ...]) -> None:
    csv.writer(sys.stdout, lineterminator="\n").writerow(values)


def _account_report_row(database, account: str, name: str) -> None:
    rows = [row for row in database.transactions.list() if row.account == account]
    _print_row((account, name, len(rows), _formatted_cents(sum(row.amount for row in rows))))


def _txn_report_header() -> None:
    _print_row(("txn_id", "date", "account", "category", "amount", "memo"))


def _txn_report_row(row) -> None:
    _print_row((row.txn_id, row.date, row.account, row.category,
                _formatted_cents(row.amount), row.memo))


def account_command(args: Namespace, database_dsn: str) -> int:
    operation = args.operation
    with open_database(database_dsn) as database:
        if operation == "add":
            account, name = _arguments(args, 2, "account add")
            account = _code(account, "account")
            name = _text(name, 40, "name")
            if database.accounts.get(account=account) is not None:
                raise RejectedError("duplicate account")
            database.accounts.create(account=account, name=name)
            _print_row(("account", "name", "transactions", "balance"))
            _account_report_row(database, account, name)
            return 0
        if operation == "get":
            (account,) = _arguments(args, 1, "account get")
            row = database.accounts.get(account=_code(account, "account"))
            if row is None:
                raise NotFoundError("account not found")
            _print_row(("account", "name", "transactions", "balance"))
            _account_report_row(database, row.account, row.name)
            return 0
        if operation == "rename":
            account, name = _arguments(args, 2, "account rename")
            account = _code(account, "account")
            name = _text(name, 40, "name")
            if database.accounts.get(account=account) is None:
                raise NotFoundError("account not found")
            database.accounts.update(account=account, name=name)
            _print_row(("account", "name", "transactions", "balance"))
            _account_report_row(database, account, name)
            return 0
        if operation == "delete":
            (account,) = _arguments(args, 1, "account delete")
            account = _code(account, "account")
            row = database.accounts.get(account=account)
            if row is None:
                raise NotFoundError("account not found")
            if any(row.account == account for row in database.transactions.list()):
                raise RejectedError("account has transactions")
            database.accounts.delete(account=account)
            _print_row(("deleted",))
            _print_row((account,))
            return 0
    raise UsageError(f"unknown account operation: {operation}")


def transaction_command(args: Namespace, database_dsn: str) -> int:
    operation = args.operation
    with open_database(database_dsn) as database:
        if operation == "post":
            if len(args.arguments) not in (4, 5):
                raise UsageError("txn post requires 4 or 5 arguments")
            account, category, amount_text, date_text = args.arguments[:4]
            memo = args.arguments[4] if len(args.arguments) == 5 else ""
            account = _code(account, "account")
            category = _code(category, "category")
            amount = _cents(amount_text)
            date_text = _date(date_text)
            memo = _text(memo, 60, "memo", empty=True)
            if database.accounts.get(account=account) is None:
                raise RejectedError("unknown account")
            if database.categories.get(category=category) is None:
                raise RejectedError("unknown category")
            balance = sum(row.amount for row in database.transactions.list() if row.account == account)
            if balance + amount < 0:
                raise RejectedError("negative balance")
            transactions = database.transactions.list()
            txn_id = max((row.txn_id for row in transactions), default=0) + 1
            row = database.transactions.create(
                txn_id=txn_id, date=date_text, account=account, category=category,
                amount=amount, memo=memo,
            )
            _txn_report_header()
            _txn_report_row(row)
            return 0
        if operation == "get":
            (txn_text,) = _arguments(args, 1, "txn get")
            try:
                txn_id = int(txn_text)
            except ValueError as error:
                raise RejectedError("invalid transaction id") from error
            row = database.transactions.get(txn_id=txn_id)
            if row is None:
                raise NotFoundError("transaction not found")
            _txn_report_header()
            _txn_report_row(row)
            return 0
        if operation == "amend":
            txn_text, amount_text = _arguments(args, 2, "txn amend")
            try:
                txn_id = int(txn_text)
            except ValueError as error:
                raise RejectedError("invalid transaction id") from error
            amount = _cents(amount_text)
            row = database.transactions.get(txn_id=txn_id)
            if row is None:
                raise NotFoundError("transaction not found")
            balance = sum(item.amount for item in database.transactions.list() if item.account == row.account)
            if balance - row.amount + amount < 0:
                raise RejectedError("negative balance")
            database.transactions.update(txn_id=txn_id, amount=amount)
            updated = database.transactions.get(txn_id=txn_id)
            _txn_report_header()
            _txn_report_row(updated)
            return 0
        if operation == "delete":
            (txn_text,) = _arguments(args, 1, "txn delete")
            try:
                txn_id = int(txn_text)
            except ValueError as error:
                raise RejectedError("invalid transaction id") from error
            row = database.transactions.get(txn_id=txn_id)
            if row is None:
                raise NotFoundError("transaction not found")
            balance = sum(item.amount for item in database.transactions.list() if item.account == row.account)
            if balance - row.amount < 0:
                raise RejectedError("negative balance")
            database.transactions.delete(txn_id=txn_id)
            _print_row(("deleted",))
            _print_row((txn_id,))
            return 0
    raise UsageError(f"unknown transaction operation: {operation}")


def balance_report(database_dsn: str) -> int:
    with open_database(database_dsn) as database:
        transactions = database.transactions.list()
        aggregates: dict[str, tuple[int, int]] = {}
        for row in transactions:
            count, amount = aggregates.get(row.account, (0, 0))
            aggregates[row.account] = (count + 1, amount + row.amount)
        _print_row(("account", "name", "transactions", "balance"))
        total_count = total_amount = 0
        for account in sorted(database.accounts.list(), key=lambda item: item.account):
            count, amount = aggregates.get(account.account, (0, 0))
            _print_row((account.account, account.name, count, _formatted_cents(amount)))
            total_count += count
            total_amount += amount
        _print_row(("TOTAL", "", total_count, _formatted_cents(total_amount)))
    return 0


def category_report(database_dsn: str) -> int:
    with open_database(database_dsn) as database:
        categories = {row.category: row.description for row in database.categories.list()}
        grouped: dict[str, list] = {key: [] for key in categories}
        for row in database.transactions.list():
            grouped.setdefault(row.category, []).append(row)
        _print_row(("category", "description", "transactions", "inflow", "outflow", "net"))
        total_count = total_in = total_out = 0
        for category in sorted(grouped):
            rows = grouped[category]
            inflow = sum(row.amount for row in rows if row.amount > 0)
            outflow = sum(-row.amount for row in rows if row.amount < 0)
            _print_row((category, categories.get(category, ""), len(rows),
                        _formatted_cents(inflow), _formatted_cents(outflow),
                        _formatted_cents(inflow - outflow)))
            total_count += len(rows)
            total_in += inflow
            total_out += outflow
        _print_row(("TOTAL", "", total_count, _formatted_cents(total_in),
                    _formatted_cents(total_out), _formatted_cents(total_in - total_out)))
    return 0


def monthly_report(database_dsn: str) -> int:
    with open_database(database_dsn) as database:
        grouped: dict[str, list] = {}
        for row in database.transactions.list():
            grouped.setdefault(row.date[:7], []).append(row)
        _print_row(("month", "transactions", "inflow", "outflow", "net"))
        total_count = total_in = total_out = 0
        for month in sorted(grouped):
            rows = grouped[month]
            inflow = sum(row.amount for row in rows if row.amount > 0)
            outflow = sum(-row.amount for row in rows if row.amount < 0)
            _print_row((month, len(rows), _formatted_cents(inflow), _formatted_cents(outflow),
                        _formatted_cents(inflow - outflow)))
            total_count += len(rows)
            total_in += inflow
            total_out += outflow
        _print_row(("TOTAL", total_count, _formatted_cents(total_in), _formatted_cents(total_out),
                    _formatted_cents(total_in - total_out)))
    return 0


def transfer_command(args: Namespace, database_dsn: str) -> int:
    source, target, amount_text, date_text = _arguments(args, 4, "transfer")
    source = _code(source, "account")
    target = _code(target, "account")
    amount = _cents(amount_text)
    if amount <= 0:
        raise RejectedError("invalid amount")
    date_text = _date(date_text)
    with open_database(database_dsn) as database:
        if database.accounts.get(account=source) is None or database.accounts.get(account=target) is None:
            raise RejectedError("unknown account")
        categories = {row.category for row in database.categories.list()}
        if "TRANSFER" not in categories:
            raise RejectedError("unknown category")
        balance = sum(row.amount for row in database.transactions.list() if row.account == source)
        if balance - amount < 0:
            raise RejectedError("negative balance")
        next_id = max((row.txn_id for row in database.transactions.list()), default=0) + 1
        first = database.transactions.create(txn_id=next_id, date=date_text, account=source,
                                              category="TRANSFER", amount=-amount,
                                              memo=f"transfer to {target}")
        second = database.transactions.create(txn_id=next_id + 1, date=date_text, account=target,
                                               category="TRANSFER", amount=amount,
                                               memo=f"transfer from {source}")
    _txn_report_header()
    _txn_report_row(first)
    _txn_report_row(second)
    return 0


def _load_rows(table: str, path: str) -> list[dict[str, object]]:
    if table not in _HEADERS:
        raise UsageError(f"unknown load table: {table}")
    try:
        with open(path, newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            header = next(reader, None)
            if header != list(_HEADERS[table]):
                raise RejectedError("invalid CSV header")
            rows: list[dict[str, object]] = []
            seen: set[object] = set()
            for values in reader:
                if len(values) != len(header):
                    raise RejectedError("invalid CSV row")
                if table == "accounts":
                    key = _code(values[0], "account")
                    if key in seen:
                        raise RejectedError("duplicate key")
                    seen.add(key)
                    rows.append({"account": key, "name": _text(values[1], 40, "name")})
                elif table == "categories":
                    key = _code(values[0], "category")
                    if key in seen:
                        raise RejectedError("duplicate key")
                    seen.add(key)
                    rows.append({"category": key, "description": _text(values[1], 40, "description")})
                else:
                    try:
                        txn_id = int(values[0])
                    except ValueError as error:
                        raise RejectedError("invalid transaction id") from error
                    if txn_id in seen:
                        raise RejectedError("duplicate key")
                    seen.add(txn_id)
                    try:
                        parsed_date = date.fromisoformat(values[1])
                    except ValueError as error:
                        raise RejectedError("invalid date") from error
                    if parsed_date.isoformat() != values[1]:
                        raise RejectedError("invalid date")
                    rows.append({
                        "txn_id": txn_id,
                        "date": values[1],
                        "account": _code(values[2], "account"),
                        "category": _code(values[3], "category"),
                        "amount": _cents(values[4]),
                        "memo": _text(values[5], 60, "memo", empty=True),
                    })
    except FileNotFoundError as error:
        raise UsageError(f"CSV file not found: {path}") from error
    except UnicodeDecodeError as error:
        raise RejectedError("invalid CSV encoding") from error
    return rows


def load_table(table: str, path: str, database_dsn: str) -> int:
    rows = _load_rows(table, path)
    with open_database(database_dsn) as database:
        if table == "accounts":
            existing = {row.account for row in database.accounts.list()}
            if any(row["account"] in existing for row in rows):
                raise RejectedError("duplicate key")
            for row in rows:
                database.accounts.create(**row)
        elif table == "categories":
            existing = {row.category for row in database.categories.list()}
            if any(row["category"] in existing for row in rows):
                raise RejectedError("duplicate key")
            for row in rows:
                database.categories.create(**row)
        else:
            accounts = {row.account for row in database.accounts.list()}
            categories = {row.category for row in database.categories.list()}
            existing_ids = {row.txn_id for row in database.transactions.list()}
            if any(row["account"] not in accounts or row["category"] not in categories for row in rows):
                raise RejectedError("unknown transaction reference")
            if any(row["txn_id"] in existing_ids for row in rows):
                raise RejectedError("duplicate key")
            balances = {account: 0 for account in accounts}
            for row in database.transactions.list():
                balances[row.account] += row.amount
            for row in rows:
                balances[row["account"]] += row["amount"]
            if any(balance < 0 for balance in balances.values()):
                raise RejectedError("negative balance")
            for row in rows:
                database.transactions.create(**row)
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(("table", "loaded"))
    writer.writerow((table, len(rows)))
    return 0


def handlers(database_dsn: str) -> dict[str, CommandHandler]:
    """Return command handlers for the CLI.

    The service implementation is supplied by later ledger capability blocks;
    keeping the lookup here makes the CLI independent of persistence details.
    """

    return {
        "init": lambda _args: initialize_schema(database_dsn),
        "count": lambda _args: count_rows(database_dsn),
        "load": lambda args: _dispatch_load(args, database_dsn),
        "transfer": lambda args: transfer_command(args, database_dsn),
        "account": lambda args: account_command(args, database_dsn),
        "txn": lambda args: transaction_command(args, database_dsn),
        "report": lambda args: {
            "balances": balance_report,
            "categories": category_report,
            "monthly": monthly_report,
        }.get(args.operation, lambda _dsn: (_ for _ in ()).throw(
            UsageError(f"unknown report operation: {args.operation}")))(database_dsn),
    }


def _dispatch_load(args: Namespace, database_dsn: str) -> int:
    if len(args.arguments) != 2:
        raise UsageError("load requires a table and CSV path")
    return load_table(args.arguments[0], args.arguments[1], database_dsn)


def dispatch(args: Namespace, database_dsn: str) -> int:
    """Dispatch a validated command through the service boundary."""

    command_handler = handlers(database_dsn).get(args.command)
    if command_handler is None:
        raise UsageError(f"unknown command: {args.command}")
    return command_handler(args)

