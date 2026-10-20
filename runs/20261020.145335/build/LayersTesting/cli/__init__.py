"""Command-line entry point. ``main`` returns an exit status; it never exits the process."""

from __future__ import annotations

import sys

from cli import commands
from cli.parser import UsageError, build_parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
    except UsageError as exc:
        # A usage error is one diagnostic line on standard error, with exit status 2.
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except SystemExit as exc:
        # argparse exits 0 after printing --help to standard output.
        return int(exc.code or 0)
    return commands.dispatch(args)
