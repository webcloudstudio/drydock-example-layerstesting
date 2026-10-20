"""Runtime configuration boundary for the ledger application."""

from __future__ import annotations

import os


DEFAULT_DATABASE_DSN = "data/app.db"


def database_dsn() -> str:
    """Return the configured database location using the documented precedence."""

    return (
        os.environ.get("DATABASE_URL")
        or os.environ.get("DATABASE_PATH")
        or DEFAULT_DATABASE_DSN
    )

