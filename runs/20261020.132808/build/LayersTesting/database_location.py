"""Database location: the one place that reads ``DATABASE_URL`` and ``DATABASE_PATH``.

``resolve_database_location`` returns the location string that callers pass to ``open_database``.
It never opens a connection.
"""

from __future__ import annotations

import os

__all__ = ["DatabaseLocationError", "resolve_database_location"]

DEFAULT_LOCATION = "data/app.db"
SQLITE_PREFIX = "sqlite://"
POSTGRES_PREFIXES = ("postgres://", "postgresql://")


class DatabaseLocationError(ValueError):
    """The configured database location names an engine this build does not provide."""


def resolve_database_location() -> str:
    """Return the database location: ``DATABASE_URL``, then ``DATABASE_PATH``, then ``data/app.db``.

    An empty variable counts as unset. A ``sqlite://`` prefix is removed. A PostgreSQL DSN raises
    ``DatabaseLocationError`` because this build has no PostgreSQL backend.
    """
    value = os.environ.get("DATABASE_URL") or os.environ.get("DATABASE_PATH") or DEFAULT_LOCATION
    if value.startswith(POSTGRES_PREFIXES):
        raise DatabaseLocationError("this build has no PostgreSQL backend")
    if value.startswith(SQLITE_PREFIX):
        return value[len(SQLITE_PREFIX):]
    return value
