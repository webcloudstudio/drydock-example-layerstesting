"""Argument parsing for the ledger command; no command behavior lives here."""

from __future__ import annotations

import argparse


def _arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("arguments", nargs="+", help="command arguments")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ledger", description="Cash ledger")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="initialize the ledger database")
    init.set_defaults(operation=None)

    commands.add_parser("count", help="count rows in ledger tables")

    load = commands.add_parser("load", help="load ledger data from files")
    _arguments(load)

    transfer = commands.add_parser("transfer", help="transfer cash between accounts")
    _arguments(transfer)

    account = commands.add_parser("account", help="manage accounts")
    account_commands = account.add_subparsers(dest="operation", required=True)
    for name, help_text in (
        ("add", "add an account"),
        ("get", "retrieve an account"),
        ("rename", "rename an account"),
        ("delete", "delete an account"),
    ):
        child = account_commands.add_parser(name, help=help_text)
        _arguments(child)

    txn = commands.add_parser("txn", help="manage transactions")
    txn_commands = txn.add_subparsers(dest="operation", required=True)
    for name, help_text in (
        ("post", "post a transaction"),
        ("get", "retrieve a transaction"),
        ("amend", "amend a transaction"),
        ("delete", "delete a transaction"),
    ):
        child = txn_commands.add_parser(name, help=help_text)
        _arguments(child)

    report = commands.add_parser("report", help="produce ledger reports")
    report_commands = report.add_subparsers(dest="operation", required=True)
    for name, help_text in (
        ("balances", "report account balances"),
        ("categories", "report category totals"),
        ("monthly", "report monthly totals"),
    ):
        report_commands.add_parser(name, help=help_text)

    return parser
