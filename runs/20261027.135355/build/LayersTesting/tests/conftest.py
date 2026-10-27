"""Fixtures shared by the command tests: a fresh, initialised ledger store per test under ``tmp_path``.

CLI writes commit to their own connection, so these tests point ``DATABASE_URL`` at a private file.
That keeps ``data/app.db`` out of reach of anything a command does.
"""

import pytest

from cli.testing import cli_runner
from persistence import open_database


@pytest.fixture
def ledger_store(tmp_path, monkeypatch):
    """Point the ledger at an empty, initialised store and return its path."""
    path = tmp_path / "ledger.db"
    monkeypatch.setenv("DATABASE_URL", str(path))
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    code, _, err = cli_runner("init")
    assert code == 0, err
    return path


@pytest.fixture
def store_open():
    """Open the store at a path for read-back through the persistence interface."""

    def opener(path):
        return open_database(str(path))

    return opener
