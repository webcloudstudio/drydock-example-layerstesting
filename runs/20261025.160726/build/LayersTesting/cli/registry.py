"""The command table. Command modules call ``register`` on import; nothing else edits it."""

from collections.abc import Callable

from cli.errors import UsageError

Handler = Callable[[list[str]], list[list[str]] | None]

_COMMANDS: dict[tuple[str, ...], tuple[Handler, tuple[int, int]]] = {}


def register(words: tuple[str, ...], handler: Handler, nargs: tuple[int, int]) -> None:
    """Add a command. ``words`` is its name, ``nargs`` is the (min, max) argument count after it."""
    if not words:
        raise ValueError("a command needs at least one word")
    if words in _COMMANDS:
        raise ValueError(f"command already registered: {' '.join(words)}")
    low, high = nargs
    if low < 0 or high < low:
        raise ValueError(f"invalid argument count {nargs!r} for {' '.join(words)}")
    _COMMANDS[tuple(words)] = (handler, (low, high))


def lookup(argv: list[str]) -> tuple[Handler, list[str]]:
    """Return the handler for the longest registered word prefix of ``argv`` and its arguments."""
    for size in range(len(argv), 0, -1):
        entry = _COMMANDS.get(tuple(argv[:size]))
        if entry is not None:
            handler, (low, high) = entry
            args = argv[size:]
            if not low <= len(args) <= high:
                raise UsageError(f"{' '.join(argv[:size])}: expects {_count(low, high)} argument(s)")
            return handler, args
    if not argv:
        raise UsageError("no command given")
    raise UsageError(f"unknown command: {' '.join(argv)}")


def _count(low: int, high: int) -> str:
    return str(low) if low == high else f"{low} to {high}"
