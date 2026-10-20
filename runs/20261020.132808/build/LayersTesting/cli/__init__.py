"""Command-line entry point for the ``ledger`` program.

``main`` parses ``argv``, dispatches the command, and returns an exit code. It never calls
``sys.exit``; the ``ledger`` launcher and ``python -m cli`` are the only callers that do.
"""

from __future__ import annotations

from cli import commands
from cli.parser import build_parser


def main(argv: list[str] | None = None) -> int:
    """Run one ``ledger`` command and return its exit code (0 success, 1 failure, 2 usage)."""
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exc:  # argparse exits on usage errors and --help; return its code instead
        return int(exc.code or 0)
    return commands.dispatch(args)
