"""Public command-line boundary for the ledger."""

from __future__ import annotations

import argparse
import csv
import sys
from io import StringIO

from services import (
    OperationalError,
    ValidationError,
    add_account,
    counts,
    initialize,
    load_reference,
    load_transactions,
    post_transaction,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ledger", add_help=False)
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("init")
    subparsers.add_parser("count")
    account = subparsers.add_parser("account")
    account_subparsers = account.add_subparsers(dest="account_command")
    account_add = account_subparsers.add_parser("add")
    account_add.add_argument("account")
    account_add.add_argument("name")
    load = subparsers.add_parser("load")
    load_subparsers = load.add_subparsers(dest="load_table")
    for table in ("accounts", "categories"):
        loader = load_subparsers.add_parser(table)
        loader.add_argument("filename")
    transaction_loader = load_subparsers.add_parser("transactions")
    transaction_loader.add_argument("filename")
    txn = subparsers.add_parser("txn")
    txn_subparsers = txn.add_subparsers(dest="txn_command")
    txn_post = txn_subparsers.add_parser("post")
    txn_post.add_argument("account")
    txn_post.add_argument("category")
    txn_post.add_argument("amount")
    txn_post.add_argument("date")
    txn_post.add_argument("memo", nargs="?", default="")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    try:
        if args.command == "init":
            initialize()
            return 0
        if args.command == "count":
            values = counts()
            writer = csv.writer(sys.stdout, lineterminator="\n")
            writer.writerow(("table", "rows"))
            for table in ("accounts", "categories", "transactions"):
                writer.writerow((table, values[table]))
            return 0
        if args.command == "account" and args.account_command == "add":
            add_account(args.account, args.name)
            return 0
        if args.command == "load" and args.load_table in ("accounts", "categories"):
            loaded = load_reference(args.load_table, args.filename)
            writer = csv.writer(sys.stdout, lineterminator="\n")
            writer.writerow(("table", "loaded"))
            writer.writerow((args.load_table, loaded))
            return 0
        if args.command == "load" and args.load_table == "transactions":
            loaded = load_transactions(args.filename)
            writer = csv.writer(sys.stdout, lineterminator="\n")
            writer.writerow(("table", "loaded"))
            writer.writerow(("transactions", loaded))
            return 0
        if args.command == "txn" and args.txn_command == "post":
            post_transaction(args.account, args.category, args.amount, args.date, args.memo)
            return 0
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    except OperationalError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # expected operational failures stay off stdout
        print(f"error: {exc}", file=sys.stderr)
        return 3
    parser.print_usage(sys.stderr)
    return 2


def cli_runner(*argv: str, environ: dict[str, str] | None = None) -> tuple[int, str, str]:
    """Run the public command boundary while collecting its two streams."""
    old_environ = dict(__import__("os").environ)
    if environ is not None:
        __import__("os").environ.clear()
        __import__("os").environ.update(environ)
    stdout, stderr = sys.stdout, sys.stderr
    out, err = StringIO(), StringIO()
    sys.stdout, sys.stderr = out, err
    try:
        code = main(list(argv))
    finally:
        sys.stdout, sys.stderr = stdout, stderr
        __import__("os").environ.clear()
        __import__("os").environ.update(old_environ)
    return code, out.getvalue(), err.getvalue()

