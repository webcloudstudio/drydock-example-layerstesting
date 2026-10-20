"""Database selection: ``resolve_dsn`` chooses the location, ``open_database`` selects the engine.

Every case passes an explicit environment mapping, so the host's own ``DATABASE_URL`` never leaks
into a result. Round-trip cases act through the public surface and read the row back.
"""

import pytest

from config import DEFAULT_DATABASE_PATH, resolve_dsn
from persistence import PersistenceError, open_database
from persistence.schema import AccountRow
from persistence.testing import SCHEMA_PATH


def test_database_url_wins_over_database_path(tmp_path):
    url = str(tmp_path / "url.db")
    path = str(tmp_path / "path.db")
    assert resolve_dsn({"DATABASE_URL": url, "DATABASE_PATH": path}) == url


def test_database_path_is_used_when_url_is_unset(tmp_path):
    path = str(tmp_path / "path.db")
    assert resolve_dsn({"DATABASE_PATH": path}) == path


def test_database_path_is_used_when_url_is_empty(tmp_path):
    path = str(tmp_path / "path.db")
    assert resolve_dsn({"DATABASE_URL": "", "DATABASE_PATH": path}) == path


def test_database_url_is_used_when_path_is_empty(tmp_path):
    url = str(tmp_path / "url.db")
    assert resolve_dsn({"DATABASE_URL": url, "DATABASE_PATH": ""}) == url


def test_database_url_with_postgres_scheme_is_returned_unchanged():
    dsn = "postgresql://127.0.0.1:1/ledger"
    assert resolve_dsn({"DATABASE_URL": dsn}) == dsn


def test_postgres_short_scheme_is_returned_unchanged():
    dsn = "postgres://127.0.0.1:1/ledger"
    assert resolve_dsn({"DATABASE_URL": dsn}) == dsn


def test_database_path_is_returned_unchanged_without_normalization():
    relative = "./nested/../data/app.db"
    assert resolve_dsn({"DATABASE_PATH": relative}) == relative


def test_sqlite_prefixed_url_is_returned_unchanged():
    dsn = "sqlite:///tmp/ledger.db"
    assert resolve_dsn({"DATABASE_URL": dsn}) == dsn


def test_neither_variable_set_resolves_to_default_path():
    assert resolve_dsn({}) == "data/app.db"
    assert DEFAULT_DATABASE_PATH == "data/app.db"


def test_both_variables_empty_resolves_to_default_path():
    assert resolve_dsn({"DATABASE_URL": "", "DATABASE_PATH": ""}) == "data/app.db"


def test_unrelated_variables_do_not_affect_resolution():
    assert resolve_dsn({"HOME": "/home/x", "DATABASE_HOST": "elsewhere"}) == "data/app.db"


def test_resolved_path_round_trips_a_row_through_open_database(tmp_path):
    path = str(tmp_path / "path.db")
    dsn = resolve_dsn({"DATABASE_PATH": path})
    with open_database(dsn) as db:
        db.execute_script(SCHEMA_PATH.read_text(encoding="utf-8"))
        db.accounts.create(account="CASH", name="Cash on hand")
    with open_database(dsn) as reopened:
        assert reopened.accounts.get(account="CASH") == AccountRow(
            account="CASH", name="Cash on hand"
        )


def test_sqlite_prefixed_url_round_trips_a_row_through_open_database(tmp_path):
    path = tmp_path / "url.db"
    dsn = resolve_dsn({"DATABASE_URL": f"sqlite://{path}"})
    with open_database(dsn) as db:
        db.execute_script(SCHEMA_PATH.read_text(encoding="utf-8"))
        db.accounts.create(account="BANK1", name="Checking")
    with open_database(dsn) as reopened:
        assert reopened.accounts.get(account="BANK1").name == "Checking"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "Blocker: shipped persistence/db.py Database.run() calls driver.connect() outside its "
        "try block, so a refused PostgreSQL connection escapes as psycopg.OperationalError "
        "instead of PersistenceError. The shipped library must be fixed in Drydock, not here."
    ),
)
def test_unreachable_postgres_raises_persistence_error():
    dsn = resolve_dsn({"DATABASE_URL": "postgresql://127.0.0.1:1/ledger"})
    try:
        db = open_database(dsn)
        db.accounts.list()
    except PersistenceError as error:
        failure = error
    except Exception:  # noqa: BLE001 - the raw driver error is the defect under test
        failure = None
    else:
        failure = None
    assert isinstance(failure, PersistenceError)
