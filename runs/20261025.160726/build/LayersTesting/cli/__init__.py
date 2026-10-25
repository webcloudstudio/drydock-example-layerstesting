"""Command-line entry point: dispatch, exit-code mapping, CSV output, and the diagnostic line."""

import importlib
import pkgutil
import sys

from persistence import PersistenceError

from cli import commands
from cli.errors import LedgerError
from cli.registry import lookup


def main(argv: list[str] | None = None) -> int:
    """Run one command and return its exit code. ``None`` means ``sys.argv[1:]``."""
    if argv is None:
        argv = sys.argv[1:]
    try:
        _load_commands()
        handler, args = lookup(list(argv))
        rows = handler(args)
        _write_rows(rows or [])
    except LedgerError as exc:
        _diagnose(exc.message)
        return exc.code
    except PersistenceError as exc:
        _diagnose(str(exc))
        return 1
    except Exception as exc:  # any unexpected failure is operational, never a traceback
        _diagnose(f"{type(exc).__name__}: {exc}")
        return 1
    return 0


def _load_commands() -> None:
    """Import every command module so each one registers its handlers."""
    for module in pkgutil.iter_modules(commands.__path__):
        importlib.import_module(f"{commands.__name__}.{module.name}")


def _write_rows(rows: list[list[str]]) -> None:
    """Write the completed result as unquoted CSV with LF endings."""
    out = sys.stdout
    for row in rows:
        out.write(",".join(str(field) for field in row) + "\n")


def _diagnose(message: str) -> None:
    """Write exactly one diagnostic line to standard error."""
    text = " ".join(message.split()) or "failed"
    print(f"error: {text}", file=sys.stderr)
