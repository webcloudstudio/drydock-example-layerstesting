"""All-or-nothing writes for commands that store more than one row.

The persistence layer commits each declared operation on its own, so this module cannot open one
database transaction around several writes. Callers therefore run every check before the first
write. Each step then inserts one row; when a later insert fails, the rows already inserted are
deleted again, newest first, and the failure is reported as ``Operational``.
"""

from collections.abc import Callable, Sequence

from ledger_core.errors import Operational
from persistence import PersistenceError

Step = tuple[Callable[[], object], Callable[[], object]]


def run_all(steps: Sequence[Step]) -> None:
    """Run each ``(insert, undo)`` pair in order. On failure, undo the completed inserts and raise."""
    completed: list[Callable[[], object]] = []
    for insert, undo in steps:
        try:
            insert()
        except PersistenceError as exc:
            for undo_done in reversed(completed):
                undo_done()
            raise Operational(f"write failed and was rolled back: {exc}") from exc
        completed.append(undo)
