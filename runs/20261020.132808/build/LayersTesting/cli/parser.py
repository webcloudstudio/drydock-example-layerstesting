"""Argument parser for the ``ledger`` command line. Builds the argparse tree; holds no behavior."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    """Return the ``ledger`` parser. Commands are added by the dispatch feature, not here."""
    parser = argparse.ArgumentParser(prog="ledger", description="Command-line cash ledger.")
    parser.add_subparsers(dest="command", metavar="<command>", required=True)
    return parser
