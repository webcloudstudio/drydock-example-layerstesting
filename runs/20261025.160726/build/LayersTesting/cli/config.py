"""Database location: DATABASE_URL, then DATABASE_PATH, then data/app.db under the application root."""

from collections.abc import Mapping
from pathlib import Path

from cli.database import DEFAULT_DSN, resolve_database_dsn

APP_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE_PATH = APP_ROOT / "data" / "app.db"


def resolve_dsn(environ: Mapping[str, str]) -> str:
    """Return the configured store location as written. An empty value counts as unset.

    Precedence lives in ``cli.database.resolve_database_dsn``; only the unset default is anchored
    to the application root here so the launcher works from any directory.
    """
    dsn = resolve_database_dsn(environ)
    return str(DEFAULT_DATABASE_PATH) if dsn == DEFAULT_DSN else dsn
