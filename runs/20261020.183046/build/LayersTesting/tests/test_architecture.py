from __future__ import annotations

import os

from ledger_app.config import database_dsn
from ledger_app.errors import NotFoundError, RejectedError, UsageError


def test_database_source_precedence() -> None:
    saved = {key: os.environ.get(key) for key in ("DATABASE_URL", "DATABASE_PATH")}
    try:
        os.environ["DATABASE_URL"] = "sqlite://url.db"
        os.environ["DATABASE_PATH"] = "path.db"
        assert database_dsn() == "sqlite://url.db"

        del os.environ["DATABASE_URL"]
        assert database_dsn() == "path.db"

        del os.environ["DATABASE_PATH"]
        assert database_dsn() == "data/app.db"
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_error_types_are_distinct_exception_boundaries() -> None:
    assert issubclass(UsageError, Exception)
    assert issubclass(RejectedError, Exception)
    assert issubclass(NotFoundError, Exception)
    assert len({UsageError, RejectedError, NotFoundError}) == 3

