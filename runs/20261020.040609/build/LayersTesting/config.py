"""Database location resolution for the ledger.

``resolve_dsn`` is the only code that reads ``DATABASE_URL`` and ``DATABASE_PATH``. The value it
returns is handed to ``persistence.open_database``, which selects the engine from the DSN's scheme.
"""

from __future__ import annotations

from collections.abc import Mapping

__all__ = ["DEFAULT_DATABASE_PATH", "resolve_dsn"]

DEFAULT_DATABASE_PATH = "data/app.db"


def resolve_dsn(environ: Mapping[str, str]) -> str:
    """Return ``DATABASE_URL``, else ``DATABASE_PATH``, else ``data/app.db``, unchanged.

    A variable counts as unset when it is absent or empty. No normalization is applied.
    """
    for name in ("DATABASE_URL", "DATABASE_PATH"):
        value = environ.get(name)
        if value:
            return value
    return DEFAULT_DATABASE_PATH
