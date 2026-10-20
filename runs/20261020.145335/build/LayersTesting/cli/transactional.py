"""Run one command as one database transaction: commit on success, roll back on any failure."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from persistence import Database

__all__ = ["run_command"]

T = TypeVar("T")


class _HeldCommit:
    """Forwards every call to the real connection except ``commit``, which waits for the command.

    The shipped persistence library commits after each write. Holding those commits here lets
    ``run_command`` decide the outcome of the whole command rather than of each statement.
    """

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def commit(self) -> None:
        """Held until ``run_command`` finishes the command."""

    def rollback(self) -> None:
        self._connection.rollback()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._connection, name)


def run_command(db: Database, command: Callable[[Database], T]) -> T:
    """Call ``command(db)`` inside one transaction and return what it returns.

    When ``command`` returns normally the transaction commits. When it raises, the transaction
    rolls back and the exception propagates unchanged. Every table written inside the command is
    covered, and no application-level lock is taken.
    """
    driver = db.driver
    connection = driver.connect()
    # An instance attribute shadows the driver's ``connect`` method, for this command only.
    driver.connect = lambda: _HeldCommit(connection)
    try:
        result = command(db)
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
    finally:
        del driver.connect
    return result
