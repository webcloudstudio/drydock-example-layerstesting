"""Database location precedence: DATABASE_URL, then DATABASE_PATH, then the default."""

import pytest

from ledger_core.config import database_path


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    """Start every test with neither variable set so the inherited store cannot leak in."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_PATH", raising=False)


def test_default_path_when_no_variable_is_set():
    assert database_path() == "data/app.db"


def test_database_url_is_used_alone(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "plain.db")
    assert database_path() == "plain.db"


def test_database_url_sqlite_prefix_is_removed(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://primary.db")
    assert database_path() == "primary.db"


def test_database_url_wins_over_database_path(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://primary.db")
    monkeypatch.setenv("DATABASE_PATH", "fallback.db")
    assert database_path() == "primary.db"


def test_empty_database_url_falls_through_to_database_path(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("DATABASE_PATH", "fallback.db")
    assert database_path() == "fallback.db"


def test_database_path_alone_is_used(monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", "fallback.db")
    assert database_path() == "fallback.db"


def test_empty_database_path_falls_through_to_default(monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", "")
    assert database_path() == "data/app.db"


def test_empty_url_and_path_fall_through_to_default(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("DATABASE_PATH", "")
    assert database_path() == "data/app.db"

