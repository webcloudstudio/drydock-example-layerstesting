"""The importable entry point for the ``ledger`` command."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from ledger_app.config import database_dsn
from ledger_app.errors import NotFoundError, RejectedError, UsageError
from ledger_app.services import dispatch
from persistence import PersistenceError

from .parser import build_parser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse, dispatch, and translate expected application outcomes to exit codes."""

    try:
        args = build_parser().parse_args(list(argv) if argv is not None else None)
        return dispatch(args, database_dsn())
    except SystemExit as error:
        # argparse uses SystemExit for both successful help and usage errors.  The
        # importable entry point returns that code so tests need not spawn a process.
        return int(error.code) if isinstance(error.code, int) else 2
    except UsageError as error:
        print(error, file=sys.stderr)
        return 2
    except RejectedError as error:
        print(error, file=sys.stderr)
        return 3
    except NotFoundError as error:
        print(error, file=sys.stderr)
        return 4
    except OSError as error:
        print(error, file=sys.stderr)
        return 1
    except PersistenceError as error:
        print(error, file=sys.stderr)
        return 1


__all__ = ["main"]
