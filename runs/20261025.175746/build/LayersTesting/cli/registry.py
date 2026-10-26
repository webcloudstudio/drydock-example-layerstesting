"""The command table. Each command module registers its handlers here at import time."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from cli.errors import Usage

Handler = Callable[[object, list[str]], list[list[str]]]


@dataclass(frozen=True)
class Command:
    """One registered command: the words that name it, its argument bounds, and its handler."""

    path: tuple[str, ...]
    min_args: int
    max_args: int
    handler: Handler


COMMANDS: dict[tuple[str, ...], Command] = {}


def register(path: Sequence[str], min_args: int, max_args: int, handler: Handler) -> None:
    """Register ``handler`` for the command words ``path``.

    ``handler(db, args)`` returns the header row followed by the data rows. Registering the same
    path twice is a programming error and raises ``ValueError``.
    """
    key = tuple(path)
    if not key:
        raise ValueError("a command path needs at least one word")
    if key in COMMANDS:
        raise ValueError(f"command {' '.join(key)!r} is already registered")
    COMMANDS[key] = Command(key, min_args, max_args, handler)


def resolve(argv: Sequence[str]) -> tuple[Command, list[str]]:
    """Find the command named by the leading words of ``argv`` and check its argument count.

    Raises ``Usage`` for no command, an unknown command, or a wrong argument count. Nothing is
    opened or written here.
    """
    matches = [command for key, command in COMMANDS.items() if tuple(argv[: len(key)]) == key]
    if not matches:
        raise Usage("unknown command: " + (" ".join(argv) if argv else "(none)"))
    command = max(matches, key=lambda item: len(item.path))
    args = list(argv[len(command.path) :])
    if not command.min_args <= len(args) <= command.max_args:
        raise Usage(f"{' '.join(command.path)} takes {command.min_args} to {command.max_args} arguments")
    return command, args
