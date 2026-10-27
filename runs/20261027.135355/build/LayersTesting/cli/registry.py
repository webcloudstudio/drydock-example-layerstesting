"""Command registry: maps command words to handlers, filled from the modules in ``cli/commands/``."""

import importlib
import pkgutil
from collections.abc import Callable
from typing import Any, NamedTuple

from cli import commands


class Command(NamedTuple):
    """One registered command. ``max_args`` is ``None`` when the argument count is unbounded."""

    handler: Callable[[Any, list[str]], list[list[str]]]
    min_args: int
    max_args: int | None


#: Command words, such as ``("account", "add")``, mapped to their command.
COMMANDS: dict[tuple[str, ...], Command] = {}


def load() -> None:
    """Import every module in ``cli/commands/`` and add its ``COMMANDS``. Idempotent; never removes."""
    for module_info in pkgutil.iter_modules(commands.__path__):
        module = importlib.import_module(f"{commands.__name__}.{module_info.name}")
        COMMANDS.update(getattr(module, "COMMANDS", {}))
