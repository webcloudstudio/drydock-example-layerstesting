from pathlib import Path

import pytest

from config import Config, database_dsn, database_path
from persistence import PersistenceError
from persistence.testing import db_session


def test_database_configuration_precedence_and_defaults() -> None:
    assert Config.load({}).database_url == "data/app.db"
    assert database_dsn({"DATABASE_PATH": "fallback.db"}) == "fallback.db"
    assert database_dsn({"DATABASE_URL": "postgresql://db/ledger", "DATABASE_PATH": "ignored.db"}) == "postgresql://db/ledger"
    assert database_path({"DATABASE_PATH": "sqlite://var/ledger.db"}) == Path("var/ledger.db")


def test_declared_tables_round_trip_through_persistence_boundary() -> None:
    with db_session() as db:
        account = db.accounts.create(account="CASH", name="Cash")

        assert account.account == "CASH"
        assert db.accounts.get(account="CASH") == account


def test_undeclared_operations_are_rejected_by_the_boundary() -> None:
    with db_session() as db:
        with pytest.raises(PersistenceError):
            db.categories.update(category="SALES", description="Sales")
