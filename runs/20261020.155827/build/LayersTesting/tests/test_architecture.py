from pathlib import Path
import os
import importlib


def test_architecture_entry_points_exist():
    assert Path("ledger").is_file()
    assert callable(importlib.import_module("cli").main)
    assert callable(importlib.import_module("persistence").open_database)


def test_launcher_is_executable():
    assert os.access("ledger", os.X_OK)


def test_configuration_precedence():
    from config import settings_from_environment

    assert settings_from_environment({}).database_dsn == "data/app.db"
    assert settings_from_environment({"DATABASE_PATH": "path.db"}).database_dsn == "path.db"
    assert settings_from_environment({"DATABASE_URL": "sqlite:///url.db", "DATABASE_PATH": "path.db"}).database_dsn == "sqlite:///url.db"


def test_transaction_rolls_back_rejected_change():
    from persistence import open_database
    from services import create_account, create_category, record_transaction

    db = open_database(":memory:")
    create_account(db, "CASH", "Cash")
    create_category(db, "OPENING", "Opening")
    try:
        record_transaction(db, 1, "2026-01-01", "CASH", "OPENING", -1)
    except ValueError:
        pass
    assert db.connect().execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 0
