"""The executable command boundary for ledger."""
from __future__ import annotations
import csv
import sys
from pathlib import Path
from config import settings_from_environment
from persistence import PersistenceError, open_database
from services import InputFileError, cents, count_rows, create_account, create_transaction, delete_account, delete_transaction, initialize, load_csv, update_account, update_transaction
import reports

ROOT = Path(__file__).resolve().parent

def money(value: int) -> str:
    sign = "-" if value < 0 else ""; value = abs(value)
    return f"{sign}{value // 100}.{value % 100:02d}"

def emit(rows: list[tuple[object, ...]]) -> None:
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerows(rows)

def usage() -> int:
    print("usage: ledger init|count|load|account|txn|transfer|report", file=sys.stderr); return 2

def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args: return usage()
    command = args[0]
    try:
        db = open_database(settings_from_environment().database_dsn)
        try:
            if command == "init" and len(args) == 1:
                db.execute_script((ROOT / "schema.sql").read_text(encoding="utf-8")); initialize(db); return 0
            db.execute_script((ROOT / "schema.sql").read_text(encoding="utf-8"))
            if command == "count" and len(args) == 1:
                emit([("table", "rows"), *count_rows(db)]); return 0
            if command == "load" and len(args) == 3 and args[1] in ("accounts", "categories", "transactions"):
                emit([("table", "loaded"), (args[1], load_csv(db, args[1], args[2]))]); return 0
            if command == "account" and len(args) >= 3:
                action, code = args[1], args[2]
                if action == "add" and len(args) == 4: create_account(db, code, args[3]); emit([("account", "name", "transactions", "balance"), (code, args[3], 0, money(0))]); return 0
                if action == "get" and len(args) == 3:
                    row = next((x for x in db.accounts.list() if x.account == code), None)
                    if row is None: return 4
                    data = next(x for x in reports.balances(db) if x[0] == code); emit([("account", "name", "transactions", "balance"), (data[0], row.name, data[2], money(data[3]))]); return 0
                if action == "rename" and len(args) == 4:
                    update_account(db, code, args[3]); row = next(x for x in reports.balances(db) if x[0] == code)
                    emit([("account", "name", "transactions", "balance"), (row[0], args[3], row[2], money(row[3]))]); return 0
                if action == "delete" and len(args) == 3: delete_account(db, code); emit([("deleted",), (code,)]); return 0
            if command == "txn" and len(args) >= 3:
                action = args[1]; txn_id = int(args[2]) if action in ("get", "amend", "delete") else None
                if action == "post" and len(args) >= 6:
                    row = create_transaction(db, max([x.txn_id for x in db.transactions.list()] or [0]) + 1, args[5], args[2], args[1], 0) if False else None
                    account, category, amount, date = args[2], args[3], cents(args[4]), args[5]
                    new_id = max([x.txn_id for x in db.transactions.list()] or [0]) + 1; row = create_transaction(db, new_id, date, account, category, amount, " ".join(args[6:]))
                    emit([("txn_id", "date", "account", "category", "amount", "memo"), (row.txn_id, row.date, row.account, row.category, money(row.amount), row.memo)]); return 0
                if action == "get" and len(args) == 3:
                    row = next((x for x in db.transactions.list() if x.txn_id == txn_id), None)
                    if row is None: return 4
                    emit([("txn_id", "date", "account", "category", "amount", "memo"), (row.txn_id, row.date, row.account, row.category, money(row.amount), row.memo)]); return 0
                if action == "amend" and len(args) == 4:
                    row = update_transaction(db, txn_id, cents(args[3])); emit([("txn_id", "date", "account", "category", "amount", "memo"), (row.txn_id, row.date, row.account, row.category, money(row.amount), row.memo)]); return 0
                if action == "delete" and len(args) == 3: delete_transaction(db, txn_id); emit([("deleted",), (txn_id,)]); return 0
            if command == "transfer" and len(args) == 5:
                source, target, amount, date = args[1], args[2], cents(args[3]), args[4]
                next_id = max([x.txn_id for x in db.transactions.list()] or [0]) + 1
                with db.transaction():
                    first = create_transaction(db, next_id, date, source, "TRANSFER", -amount, f"transfer to {target}")
                    second = create_transaction(db, next_id + 1, date, target, "TRANSFER", amount, f"transfer from {source}")
                emit([("txn_id", "date", "account", "category", "amount", "memo"), (first.txn_id, date, source, "TRANSFER", money(-amount), first.memo), (second.txn_id, date, target, "TRANSFER", money(amount), second.memo)]); return 0
            if command == "report" and len(args) == 2 and args[1] in ("balances", "categories", "monthly"):
                if args[1] == "balances":
                    rows = reports.balances(db); emit([("account", "name", "transactions", "balance"), *[(a,n,t,money(b)) for a,n,t,b in rows], ("TOTAL", "", sum(x[2] for x in rows), money(sum(x[3] for x in rows)))])
                elif args[1] == "categories":
                    rows = reports.categories(db); emit([("category", "description", "transactions", "inflow", "outflow", "net"), *[(a,b,c,money(d),money(e),money(f)) for a,b,c,d,e,f in rows], ("TOTAL", "", sum(x[2] for x in rows), money(sum(x[3] for x in rows)), money(sum(x[4] for x in rows)), money(sum(x[5] for x in rows)))])
                else:
                    rows = reports.monthly(db); emit([("month", "transactions", "inflow", "outflow", "net"), *[(a,b,money(c),money(d),money(e)) for a,b,c,d,e in rows], ("TOTAL", sum(x[1] for x in rows), money(sum(x[2] for x in rows)), money(sum(x[3] for x in rows)), money(sum(x[4] for x in rows)))])
                return 0
            return usage()
        finally: db.close()
    except InputFileError as exc:
        print(f"error: {exc}", file=sys.stderr); return 1
    except LookupError as exc:
        print(f"error: {exc}", file=sys.stderr); return 4
    except (ValueError, PersistenceError, OSError, KeyError, IndexError, OverflowError) as exc:
        print(f"error: {exc}", file=sys.stderr); return 3
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr); return 1

if __name__ == "__main__": sys.exit(main())
