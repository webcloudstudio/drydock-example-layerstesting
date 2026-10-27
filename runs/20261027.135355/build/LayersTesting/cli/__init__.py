"""Command-line entry point for the ledger.

``main`` resolves the command words, checks the argument count, opens the database, calls the
handler, and turns the result into CSV on stdout or one diagnostic line on stderr. It returns the
exit code and never calls ``sys.exit``; the ``ledger`` launcher is the only caller that does.
"""

import sys
from pathlib import Path

from cli import registry
from ledger_core.config import database_path
from ledger_core.errors import LedgerError, Operational
from persistence import Database, open_database

EXIT_OK = 0
EXIT_OPERATIONAL = 1
EXIT_USAGE = 2
POSTGRES_PREFIXES = ("postgres://", "postgresql://")


def _usage_error(message: str) -> int:
    print(f"usage: {message}", file=sys.stderr)
    return EXIT_USAGE


def _open_store(location: str) -> Database:
    """Open the declared store. A SQLite file whose directory is absent is refused, not created.

    The shipped SQLite driver creates a missing parent directory on connect, which would turn a
    mistyped location into a new, empty store. The ledger's store is provisioned in advance.
    """
    if not location.startswith(POSTGRES_PREFIXES):
        parent = Path(location).parent
        if not parent.is_dir():
            raise Operational(f"database directory does not exist: {parent}")
    return open_database(location)


def _match(argv: list[str]) -> tuple[tuple[str, ...], registry.Command] | None:
    """Return the longest command-word prefix of ``argv`` that is registered, with its command."""
    for length in range(len(argv), 0, -1):
        words = tuple(argv[:length])
        if words in registry.COMMANDS:
            return words, registry.COMMANDS[words]
    return None


def _format(rows: list[list[str]]) -> str:
    """Render rows as unquoted CSV with ``\\n`` line endings."""
    return "".join(",".join(str(value) for value in row) + "\n" for row in rows)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    registry.load()

    matched = _match(argv)
    if matched is None:
        return _usage_error(f"unknown command {' '.join(argv)!r}" if argv else "no command given")
    words, command = matched

    args = argv[len(words):]
    if len(args) < command.min_args or (command.max_args is not None and len(args) > command.max_args):
        return _usage_error(f"wrong number of arguments for {' '.join(words)!r}")

    try:
        database = _open_store(database_path())
    except Exception as exc:
        print(f"error: cannot open database: {exc}", file=sys.stderr)
        return EXIT_OPERATIONAL

    try:
        rows = command.handler(database, args)
    except LedgerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_OPERATIONAL
    finally:
        database.close()

    sys.stdout.write(_format(rows))
    return EXIT_OK
