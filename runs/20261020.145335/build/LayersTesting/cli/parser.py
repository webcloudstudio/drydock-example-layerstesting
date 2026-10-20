"""Argument parser construction. No behavior lives here."""

from __future__ import annotations

import argparse

TABLES = ("accounts", "categories", "transactions")
REPORTS = ("balances", "categories", "monthly")


class UsageError(Exception):
    """A command line the parser rejects. ``main`` reports it as one stderr line and exits 2."""


class _Parser(argparse.ArgumentParser):
    """Raises ``UsageError`` instead of printing usage and exiting, so each usage error is one line."""

    def error(self, message: str) -> None:
        raise UsageError(message)


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="ledger", description="Command-line cash ledger.")
    commands = parser.add_subparsers(dest="command", required=True, metavar="<command>")

    commands.add_parser("init", help="Create the database schema.").set_defaults(route="init")
    commands.add_parser("count", help="Count stored rows in each table.").set_defaults(route="count")

    load = commands.add_parser("load", help="Load a seed CSV file into a table.")
    load.add_argument("table", choices=TABLES, help="Table to load: accounts, categories, or transactions.")
    load.add_argument("file", help="Path of the CSV file to load.")
    load.set_defaults(route="load")

    account = commands.add_parser("account", help="Manage accounts.")
    account_verbs = account.add_subparsers(dest="verb", required=True, metavar="<verb>")
    account_verbs.add_parser("add", help="Add an account.").set_defaults(route="account add")
    account_verbs.add_parser("get", help="Show an account.").set_defaults(route="account get")
    account_verbs.add_parser("rename", help="Rename an account.").set_defaults(route="account rename")
    account_verbs.add_parser("delete", help="Delete an account.").set_defaults(route="account delete")

    txn = commands.add_parser("txn", help="Manage cash transactions.")
    txn_verbs = txn.add_subparsers(dest="verb", required=True, metavar="<verb>")
    txn_verbs.add_parser("post", help="Post a transaction.").set_defaults(route="txn post")
    get = txn_verbs.add_parser("get", help="Show a transaction.")
    get.add_argument("txn_id", type=int, help="Transaction number.")
    get.set_defaults(route="txn get")
    txn_verbs.add_parser("amend", help="Amend a transaction.").set_defaults(route="txn amend")
    txn_verbs.add_parser("delete", help="Delete a transaction.").set_defaults(route="txn delete")

    commands.add_parser("transfer", help="Move cash between two accounts.").set_defaults(route="transfer")

    report = commands.add_parser("report", help="Print a report.")
    report_names = report.add_subparsers(dest="name", required=True, metavar="<report>")
    for name in REPORTS:
        report_names.add_parser(name, help=f"Print the {name} report.").set_defaults(route=f"report {name}")

    return parser
