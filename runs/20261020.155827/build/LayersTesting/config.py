"""Application configuration boundary."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_dsn: str


def settings_from_environment(environ: dict[str, str] | None = None) -> Settings:
    """Resolve the database location using the documented precedence."""
    values = os.environ if environ is None else environ
    dsn = values.get("DATABASE_URL") or values.get("DATABASE_PATH") or "data/app.db"
    return Settings(database_dsn=dsn)
