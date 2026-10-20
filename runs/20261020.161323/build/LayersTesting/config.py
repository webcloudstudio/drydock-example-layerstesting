"""Typed application configuration and database-location resolution."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """The process configuration consumed by application callers."""

    database_url: str

    @classmethod
    def load(cls, environ: dict[str, str] | None = None) -> "Config":
        values = os.environ if environ is None else environ
        return cls(
            database_url=(
                values.get("DATABASE_URL")
                or values.get("DATABASE_PATH")
                or "data/app.db"
            )
        )


def database_dsn(environ: dict[str, str] | None = None) -> str:
    return Config.load(environ).database_url


def database_path(environ: dict[str, str] | None = None) -> Path:
    dsn = database_dsn(environ)
    if dsn.startswith("sqlite:///"):
        return Path(dsn.removeprefix("sqlite:///"))
    if dsn.startswith("sqlite://"):
        return Path(dsn.removeprefix("sqlite://"))
    return Path(dsn)

