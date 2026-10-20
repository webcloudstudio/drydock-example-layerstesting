"""Command behavior for the ``ledger`` program. One function per command, plain arguments."""

from __future__ import annotations

import argparse
import sys


def dispatch(args: argparse.Namespace) -> int:
    """Route a parsed command to its handler. No handlers are registered in this build block."""
    print(f"error: unknown command {args.command!r}", file=sys.stderr)
    return 2
