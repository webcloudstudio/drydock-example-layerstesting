"""Runtime configuration: where the ledger database lives."""

import os

DEFAULT_DATABASE_PATH = "data/app.db"
SQLITE_URL_PREFIX = "sqlite://"


def _non_empty(name: str) -> str | None:
    """Return the environment variable's value, or None when unset or empty."""
    value = os.environ.get(name)
    return value if value else None


def database_path() -> str:
    """Resolve the database location.

    Precedence: ``DATABASE_URL`` (with an optional leading ``sqlite://`` removed),
    then ``DATABASE_PATH``, then ``data/app.db``. Unset or empty values are skipped.
    """
    url = _non_empty("DATABASE_URL")
    if url is not None:
        return url.removeprefix(SQLITE_URL_PREFIX)
    path = _non_empty("DATABASE_PATH")
    if path is not None:
        return path
    return DEFAULT_DATABASE_PATH
