"""Shared pytest fixtures for the LayersTesting project.

The fixtures import their providers lazily. The persistence and CLI packages are generated and
added by later build steps, so this module must import cleanly before they exist.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def db_session() -> Iterator[Any]:
    """Yield the provisioned application database, rolled back by the shipped fixture."""
    from persistence.testing import db_session as shipped_db_session

    with shipped_db_session() as db:
        yield db


@pytest.fixture
def scratch_db(tmp_path, monkeypatch) -> Iterator[Any]:
    """A throwaway store under ``tmp_path``, selected through ``DATABASE_PATH`` for the CLI.

    The configured application store is never touched. Commands run in-process open their own
    connection, so they cannot share the rollback fixture; this store is the criterion-owned record.
    """
    from persistence import open_database

    monkeypatch.delenv("DATABASE_URL", raising=False)
    path = tmp_path / "scratch.db"
    monkeypatch.setenv("DATABASE_PATH", str(path))
    db = open_database(str(path))
    db.execute_script((Path(__file__).resolve().parent.parent / "schema.sql").read_text(encoding="utf-8"))
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def cli_runner() -> Callable[..., tuple[int, str, str]]:
    """Return a callable that runs the CLI in-process and returns (exit_code, stdout, stderr)."""
    from cli import testing

    return testing.cli_runner
