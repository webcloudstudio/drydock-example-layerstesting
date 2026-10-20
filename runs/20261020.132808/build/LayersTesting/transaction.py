"""Command transaction: each ledger command runs inside exactly one database transaction.

``run_command`` calls the command once against a view of the store, commits when the command
returns, and rolls back every write when it raises. The shipped ``Database`` commits after each
write, so the command's view defers that commit to ``run_command``. The command body never commits
or rolls back its own work.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from persistence import Database, PersistenceError
from persistence.schema import SCHEMA

__all__ = ["run_command"]

T = TypeVar("T")


class _DeferredCommit:
    """A connection whose ``commit`` is deferred to the enclosing command. Everything else passes through."""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def commit(self) -> None:
        """Deferred: ``run_command`` commits once, when the command returns."""

    def __getattr__(self, name: str) -> Any:
        return getattr(self._connection, name)


class _CommandDriver:
    """The store's driver for one command: the same connection, with commit deferred."""

    def __init__(self, driver: Any) -> None:
        self._driver = driver
        self.raw = driver.connect()
        self.connection = _DeferredCommit(self.raw)

    def connect(self) -> _DeferredCommit:
        return self.connection

    def __getattr__(self, name: str) -> Any:
        return getattr(self._driver, name)


def run_command(db: Database, command: Callable[[Database], T]) -> T:
    """Run ``command`` in one transaction on ``db`` and return what it returned.

    Commits when ``command`` returns. When ``command`` raises, or the commit fails, every write made
    through the transaction is rolled back and the exception propagates unchanged.
    """
    try:
        driver = _CommandDriver(db.driver)
    except PersistenceError:
        raise
    except Exception as exc:
        raise PersistenceError(f"transaction could not open: {exc}") from exc

    # The store is already open and the driver is supplied, so the DSN argument is not read.
    scoped = Database("", SCHEMA, driver=driver)
    connection = driver.raw
    try:
        result = command(scoped)
        _commit(connection)
    except BaseException:
        connection.rollback()
        raise
    return result


def _commit(connection: Any) -> None:
    """Commit the command's transaction on the real connection, translating a failure."""
    try:
        connection.commit()
    except Exception as exc:
        raise PersistenceError(f"transaction commit failed: {exc}") from exc
