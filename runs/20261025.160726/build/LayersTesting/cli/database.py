"""Database resolution: which store a command opens, and which engine serves it.

The precedence is DATABASE_URL, then DATABASE_PATH, then ``data/app.db``. The resolver is pure: it
reads only the mapping it is given and never a file, so it can be tested without a store.
"""

from collections.abc import Mapping

DEFAULT_DSN = "data/app.db"
POSTGRES_PREFIXES = ("postgres://", "postgresql://")


def resolve_database_dsn(environ: Mapping[str, str]) -> str:
    """Return the configured store location unchanged. An empty value counts as unset."""
    return environ.get("DATABASE_URL") or environ.get("DATABASE_PATH") or DEFAULT_DSN


def database_engine(dsn: str) -> str:
    """Return ``postgres`` for a PostgreSQL DSN and ``sqlite`` for anything else.

    The scheme is compared case-insensitively, as ``persistence.open_database`` compares it.
    """
    if dsn.lower().startswith(POSTGRES_PREFIXES):
        return "postgres"
    return "sqlite"
