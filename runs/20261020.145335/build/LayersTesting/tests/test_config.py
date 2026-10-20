"""Database target resolution: DATABASE_URL, then DATABASE_PATH, then data/app.db."""

from pathlib import Path

import pytest

from config import DEFAULT_DATABASE_PATH, resolve_database_target
from persistence.testing import db_session


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_PATH", raising=False)


def test_default_target_is_data_app_db() -> None:
    assert resolve_database_target() == "data/app.db"
    assert DEFAULT_DATABASE_PATH == "data/app.db"


def test_database_path_overrides_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_PATH", "scratch.db")
    assert resolve_database_target() == "scratch.db"


def test_database_url_overrides_database_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_PATH", "scratch.db")
    monkeypatch.setenv("DATABASE_URL", "sqlite://scratch.db")
    assert resolve_database_target() == "sqlite://scratch.db"


def test_database_url_overrides_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://ledger@localhost/ledger")
    assert resolve_database_target() == "postgresql://ledger@localhost/ledger"


def test_postgres_scheme_is_returned_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgres://ledger@localhost/ledger")
    assert resolve_database_target() == "postgres://ledger@localhost/ledger"


def test_empty_database_url_falls_through_to_database_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("DATABASE_PATH", "scratch.db")
    assert resolve_database_target() == "scratch.db"


def test_empty_database_path_falls_through_to_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_PATH", "")
    assert resolve_database_target() == "data/app.db"


def test_value_is_returned_without_path_normalisation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_PATH", "./nested/../ledger.db")
    assert resolve_database_target() == "./nested/../ledger.db"


def test_resolution_opens_no_connection(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    target = tmp_path / "never-created.db"
    monkeypatch.setenv("DATABASE_PATH", str(target))
    assert resolve_database_target() == str(target)
    assert not target.exists()


def test_resolved_target_opens_store_with_empty_accounts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    target = str(tmp_path / "ledger.db")
    monkeypatch.setenv("DATABASE_PATH", target)
    resolved = resolve_database_target()
    assert resolved == target
    with db_session(resolved) as db:
        assert db.accounts.list() == []


def test_resolved_target_round_trips_an_account(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    target = str(tmp_path / "ledger.db")
    monkeypatch.setenv("DATABASE_PATH", target)
    with db_session(resolve_database_target()) as db:
        db.accounts.create(account="CASH9", name="Event Float")
        row = db.accounts.get(account="CASH9")
        assert (row.account, row.name) == ("CASH9", "Event Float")
