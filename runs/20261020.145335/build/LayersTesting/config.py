"""Database target resolution. Reads the environment only; never opens a connection."""

from __future__ import annotations

import os

DEFAULT_DATABASE_PATH = "data/app.db"


def resolve_database_target() -> str:
    """Return ``DATABASE_URL``, then ``DATABASE_PATH``, then ``data/app.db``, unchanged."""
    for name in ("DATABASE_URL", "DATABASE_PATH"):
        value = os.environ.get(name)
        if value:
            return value
    return DEFAULT_DATABASE_PATH
