"""The ledger command line: parse, dispatch, and map the outcome to an exit code."""

from __future__ import annotations

import sys

from persistence import PersistenceError

from cli import commands  # noqa: F401  (importing registers every command module)
from cli.database import open_ledger
from cli.errors import LedgerError
from cli.output import write_rows
from cli.registry import resolve


def main(argv: list[str] | None = None) -> int:
    """Run one ledger command and return its exit code. Standard output carries only the rows.

    The handler runs to completion before anything is written, so a failing command writes nothing
    to standard output. Diagnostics go to standard error as one line.
    """
    words = list(sys.argv[1:] if argv is None else argv)
    try:
        command, args = resolve(words)
        with open_ledger() as db:
            rows = command.handler(db, args)
    except LedgerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code
    except PersistenceError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    write_rows(rows)
    return 0
