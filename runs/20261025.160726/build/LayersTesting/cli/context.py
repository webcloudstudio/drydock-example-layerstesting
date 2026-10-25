"""Opens the declared store for a command. The only caller of ``persistence.open_database``."""

import os
from pathlib import Path

from persistence import Database, open_database

from cli.config import resolve_dsn
from cli.database import database_engine

SQLITE_PREFIX = "sqlite://"


def open_store() -> Database:
    """Open the store named by the environment, creating a missing SQLite parent directory first."""
    dsn = resolve_dsn(os.environ)
    if database_engine(dsn) == "sqlite":
        Path(_sqlite_path(dsn)).parent.mkdir(parents=True, exist_ok=True)
    return open_database(dsn)


def _sqlite_path(dsn: str) -> str:
    """Return the file path a SQLite DSN names, with any ``sqlite://`` prefix removed."""
    if dsn.startswith(SQLITE_PREFIX):
        return dsn[len(SQLITE_PREFIX):]
    return dsn
