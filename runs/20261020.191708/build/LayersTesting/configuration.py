"""Runtime configuration resolution for database access."""

from __future__ import annotations

import os
from pathlib import Path


def database_dsn(environ: dict[str, str] | None = None) -> str:
    """Resolve database configuration by the application contract's precedence."""
    values = os.environ if environ is None else environ
    return values.get("DATABASE_URL") or values.get("DATABASE_PATH") or "data/app.db"


def database_path(environ: dict[str, str] | None = None) -> Path:
    """Return the configured SQLite path when the selected DSN is a filesystem path."""
    return Path(database_dsn(environ))
