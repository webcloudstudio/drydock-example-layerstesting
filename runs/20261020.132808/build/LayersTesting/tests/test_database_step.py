"""Database step: the generated persistence package and schema.sql, exercised through its public API.

Each test acts on a store and reads the result back through ``db``. Stores are fresh per test:
either a temporary SQLite store from ``db_session()`` or a file under ``tmp_path``.
"""

from pathlib import Path

import pytest

from persistence import PersistenceError, UnknownOperation, open_database
from persistence.schema import SCHEMA
from persistence.testing import db_session

SCHEMA_SQL = Path(__file__).resolve().parents[1] / "schema.sql"


def _seed(db) -> None:
    db.accounts.create(account="CASH", name="Cash on hand")
    db.categories.create(category="FOOD", description="Groceries")


# --- schema.sql and the declaration ---------------------------------------------------


def test_schema_sql_applies_to_a_fresh_store_and_the_tables_accept_rows():
    with db_session() as db:
        _seed(db)
        db.transactions.create(
            txn_id=1, date="2026-10-01", account="CASH", category="FOOD", amount=-1250, memo="milk"
        )
        assert db.transactions.get(txn_id=1).amount == -1250


def test_schema_sql_applied_twice_is_harmless():
    with db_session() as db:
        db.execute_script(SCHEMA_SQL.read_text(encoding="utf-8"))
        _seed(db)
        assert db.accounts.get(account="CASH").name == "Cash on hand"


def test_declared_tables_are_exposed_as_attributes():
    with db_session() as db:
        assert {"accounts", "categories", "transactions"} <= {t.name for t in SCHEMA.tables}
        for table in ("accounts", "categories", "transactions"):
            assert hasattr(db, table)


def test_declared_transaction_columns_match_the_schema_order():
    transactions = next(t for t in SCHEMA.tables if t.name == "transactions")
    assert transactions.columns == ("txn_id", "date", "account", "category", "amount", "memo")
    assert transactions.primary_key == "txn_id"


# --- accounts -------------------------------------------------------------------------


def test_account_create_then_get_round_trips_the_row():
    with db_session() as db:
        db.accounts.create(account="BANK", name="Checking")
        row = db.accounts.get(account="BANK")
        assert (row.account, row.name) == ("BANK", "Checking")


def test_account_get_of_an_absent_key_returns_none():
    with db_session() as db:
        assert db.accounts.get(account="NOPE") is None


def test_account_list_of_an_empty_store_is_empty():
    with db_session() as db:
        assert db.accounts.list() == []


def test_account_list_returns_every_row():
    with db_session() as db:
        _seed(db)
        db.accounts.create(account="BANK", name="Checking")
        assert sorted(row.account for row in db.accounts.list()) == ["BANK", "CASH"]


def test_account_update_changes_only_the_name():
    with db_session() as db:
        _seed(db)
        db.accounts.update(account="CASH", name="Wallet")
        assert db.accounts.get(account="CASH").name == "Wallet"


def test_account_update_of_an_absent_key_changes_nothing():
    with db_session() as db:
        _seed(db)
        assert db.accounts.update(account="NOPE", name="Ghost") == 0
        assert [row.account for row in db.accounts.list()] == ["CASH"]


def test_account_delete_removes_the_row_and_reports_the_count():
    with db_session() as db:
        _seed(db)
        assert db.accounts.delete(account="CASH") == 1
        assert db.accounts.get(account="CASH") is None


def test_account_delete_of_an_absent_key_reports_zero_rows():
    with db_session() as db:
        assert db.accounts.delete(account="NOPE") == 0


def test_account_create_with_a_duplicate_key_raises_persistence_error():
    with db_session() as db:
        _seed(db)
        with pytest.raises(PersistenceError):
            db.accounts.create(account="CASH", name="Again")


# --- categories -----------------------------------------------------------------------


def test_category_create_then_get_round_trips_the_row():
    with db_session() as db:
        db.categories.create(category="RENT", description="Housing")
        row = db.categories.get(category="RENT")
        assert (row.category, row.description) == ("RENT", "Housing")


def test_category_list_returns_every_row():
    with db_session() as db:
        _seed(db)
        assert [row.category for row in db.categories.list()] == ["FOOD"]


def test_category_get_of_an_absent_key_returns_none():
    with db_session() as db:
        assert db.categories.get(category="NOPE") is None


# --- transactions ---------------------------------------------------------------------


def test_transaction_create_stores_integer_cents_exactly():
    with db_session() as db:
        _seed(db)
        db.transactions.create(
            txn_id=7, date="2026-10-02", account="CASH", category="FOOD", amount=12345, memo="x"
        )
        assert db.transactions.get(txn_id=7).amount == 12345


def test_transaction_list_of_an_empty_store_is_empty():
    with db_session() as db:
        assert db.transactions.list() == []


def test_transaction_list_returns_every_row():
    with db_session() as db:
        _seed(db)
        for txn_id in (1, 2, 3):
            db.transactions.create(
                txn_id=txn_id, date="2026-10-03", account="CASH", category="FOOD",
                amount=100 * txn_id, memo="",
            )
        assert sorted(row.txn_id for row in db.transactions.list()) == [1, 2, 3]


def test_transaction_memo_at_its_declared_maximum_round_trips():
    with db_session() as db:
        _seed(db)
        memo = "m" * 60
        db.transactions.create(
            txn_id=9, date="2026-10-04", account="CASH", category="FOOD", amount=1, memo=memo
        )
        assert db.transactions.get(txn_id=9).memo == memo


def test_transaction_memo_may_be_empty():
    with db_session() as db:
        _seed(db)
        db.transactions.create(
            txn_id=10, date="2026-10-04", account="CASH", category="FOOD", amount=1, memo=""
        )
        assert db.transactions.get(txn_id=10).memo == ""


def test_transaction_amend_changes_only_the_amount():
    with db_session() as db:
        _seed(db)
        db.transactions.create(
            txn_id=4, date="2026-10-05", account="CASH", category="FOOD", amount=500, memo="keep"
        )
        db.transactions.update(txn_id=4, amount=-75)
        row = db.transactions.get(txn_id=4)
        assert (row.amount, row.memo, row.date) == (-75, "keep", "2026-10-05")


def test_transaction_delete_removes_the_row():
    with db_session() as db:
        _seed(db)
        db.transactions.create(
            txn_id=5, date="2026-10-06", account="CASH", category="FOOD", amount=1, memo=""
        )
        assert db.transactions.delete(txn_id=5) == 1
        assert db.transactions.get(txn_id=5) is None


def test_transaction_referencing_an_unknown_account_is_refused():
    with db_session() as db:
        _seed(db)
        with pytest.raises(PersistenceError):
            db.transactions.create(
                txn_id=6, date="2026-10-07", account="GHOST", category="FOOD", amount=1, memo=""
            )


def test_transaction_referencing_an_unknown_category_is_refused():
    with db_session() as db:
        _seed(db)
        with pytest.raises(PersistenceError):
            db.transactions.create(
                txn_id=6, date="2026-10-07", account="CASH", category="GHOST", amount=1, memo=""
            )


def test_transaction_with_a_duplicate_id_is_refused():
    with db_session() as db:
        _seed(db)
        row = {
            "txn_id": 8, "date": "2026-10-08", "account": "CASH",
            "category": "FOOD", "amount": 1, "memo": "",
        }
        db.transactions.create(**row)
        with pytest.raises(PersistenceError):
            db.transactions.create(**row)


# --- declared surface -----------------------------------------------------------------


def test_undeclared_verb_raises_unknown_operation():
    with db_session() as db, pytest.raises(UnknownOperation):
        db.accounts.upsert(account="CASH", name="Cash")


def test_undeclared_argument_is_refused_before_reaching_the_store():
    with db_session() as db, pytest.raises(PersistenceError):
        db.accounts.create(account="CASH", name="Cash", balance=5)


# --- durability across sessions -------------------------------------------------------


def test_rows_persist_when_the_store_is_reopened(tmp_path):
    path = tmp_path / "ledger.db"
    first = open_database(str(path))
    try:
        first.execute_script(SCHEMA_SQL.read_text(encoding="utf-8"))
        first.accounts.create(account="CASH", name="Cash")
    finally:
        first.close()

    second = open_database(str(path))
    try:
        assert second.accounts.get(account="CASH").name == "Cash"
    finally:
        second.close()


def test_open_database_accepts_a_sqlite_url(tmp_path):
    database = open_database(f"sqlite:///{tmp_path / 'url.db'}")
    try:
        database.execute_script(SCHEMA_SQL.read_text(encoding="utf-8"))
        database.accounts.create(account="URL", name="Via URL")
        assert database.accounts.get(account="URL").name == "Via URL"
    finally:
        database.close()
