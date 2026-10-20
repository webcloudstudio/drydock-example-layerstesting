"""Command dispatch. Behavior for each command is added as its block is built; none is registered yet."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable

# Maps a leaf route (for example "txn get") to its handler. Each handler takes the parsed Namespace.
HANDLERS: dict[str, Callable[[argparse.Namespace], int]] = {}


def dispatch(args: argparse.Namespace) -> int:
    handler = HANDLERS.get(args.route)
    if handler is None:
        # Recognized by the parser, but its behavior belongs to a block not yet built.
        print(f"error: command {args.route!r} is not implemented yet", file=sys.stderr)
        return 1
    return handler(args)
