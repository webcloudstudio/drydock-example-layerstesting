"""Open the ledger's store. The only place the database location is resolved."""

from __future__ import annotations

import os

from persistence import Database, open_database

DEFAULT_DATABASE_PATH = "data/app.db"


def database_location() -> str:
    """``DATABASE_URL``, then ``DATABASE_PATH``, then ``data/app.db``. Empty values count as unset."""
    return (
        os.environ.get("DATABASE_URL")
        or os.environ.get("DATABASE_PATH")
        or DEFAULT_DATABASE_PATH
    )


def open_ledger() -> Database:
    """Open the configured store through the shipped persistence library."""
    return open_database(database_location())
