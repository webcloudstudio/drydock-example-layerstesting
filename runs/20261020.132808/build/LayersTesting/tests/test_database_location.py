"""Database location: resolution order, the sqlite:// prefix, and PostgreSQL rejection.

Each test sets its own environment through monkeypatch, which restores it afterwards, and reads
the resolved location back through the public function.
"""

import pytest

from database_location import DatabaseLocationError, resolve_database_location


@pytest.fixture
def clean_env(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    return monkeypatch


# --- defaults and fallback order ------------------------------------------------------


def test_neither_variable_set_resolves_to_the_default_file(clean_env):
    assert resolve_database_location() == "data/app.db"


def test_database_path_alone_is_used(clean_env, tmp_path):
    path = str(tmp_path / "ledger.db")
    clean_env.setenv("DATABASE_PATH", path)
    assert resolve_database_location() == path


def test_database_url_takes_precedence_over_database_path(clean_env, tmp_path):
    url = str(tmp_path / "primary.db")
    clean_env.setenv("DATABASE_URL", url)
    clean_env.setenv("DATABASE_PATH", str(tmp_path / "secondary.db"))
    assert resolve_database_location() == url


def test_database_url_alone_is_used(clean_env, tmp_path):
    url = str(tmp_path / "only.db")
    clean_env.setenv("DATABASE_URL", url)
    assert resolve_database_location() == url


def test_empty_database_url_falls_through_to_database_path(clean_env, tmp_path):
    path = str(tmp_path / "fallback.db")
    clean_env.setenv("DATABASE_URL", "")
    clean_env.setenv("DATABASE_PATH", path)
    assert resolve_database_location() == path


def test_empty_database_url_and_path_fall_through_to_the_default(clean_env):
    clean_env.setenv("DATABASE_URL", "")
    clean_env.setenv("DATABASE_PATH", "")
    assert resolve_database_location() == "data/app.db"


def test_resolution_does_not_create_the_database_file(clean_env, tmp_path):
    path = tmp_path / "never_created.db"
    clean_env.setenv("DATABASE_PATH", str(path))
    resolve_database_location()
    assert not path.exists()


# --- sqlite:// prefix -----------------------------------------------------------------


def test_sqlite_prefix_is_removed_from_database_url(clean_env, tmp_path):
    path = str(tmp_path / "prefixed.db")
    clean_env.setenv("DATABASE_URL", "sqlite://" + path)
    assert resolve_database_location() == path


def test_sqlite_prefix_with_a_relative_path_leaves_the_relative_path(clean_env):
    clean_env.setenv("DATABASE_URL", "sqlite://data/app.db")
    assert resolve_database_location() == "data/app.db"


def test_value_without_a_prefix_is_returned_unchanged(clean_env):
    clean_env.setenv("DATABASE_PATH", "relative/ledger.db")
    assert resolve_database_location() == "relative/ledger.db"


# --- PostgreSQL rejection -------------------------------------------------------------


@pytest.mark.parametrize(
    "dsn",
    ["postgres://ledger@localhost/ledger", "postgresql://ledger@localhost/ledger"],
)
def test_postgres_dsn_in_database_url_is_rejected(clean_env, dsn):
    clean_env.setenv("DATABASE_URL", dsn)
    with pytest.raises(DatabaseLocationError):
        resolve_database_location()


def test_postgres_dsn_in_database_path_is_rejected(clean_env):
    clean_env.setenv("DATABASE_PATH", "postgres://ledger@localhost/ledger")
    with pytest.raises(DatabaseLocationError):
        resolve_database_location()


def test_postgres_dsn_is_rejected_even_when_database_path_is_also_set(clean_env, tmp_path):
    clean_env.setenv("DATABASE_URL", "postgresql://ledger@localhost/ledger")
    clean_env.setenv("DATABASE_PATH", str(tmp_path / "ignored.db"))
    with pytest.raises(DatabaseLocationError):
        resolve_database_location()
