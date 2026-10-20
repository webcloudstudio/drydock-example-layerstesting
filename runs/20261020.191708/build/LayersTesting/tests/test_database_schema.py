from dataclasses import fields

import pytest

from persistence import PersistenceError
from persistence.schema import AccountRow, CategoryRow, TransactionRow
from persistence.testing import db_session


def test_schema_creates_all_tables_and_starts_empty():
    with db_session() as db:
        assert db.accounts.get(account="MISSING") is None
        assert db.transactions.get(txn_id=1) is None


def test_declared_create_operations_round_trip_rows():
    with db_session() as db:
        account = db.accounts.create(account="CASH", name="Cash")
        category = db.categories.create(category="SALES", description="Sales")
        transaction = db.transactions.create(
            txn_id=1,
            date="2026-01-01",
            account="CASH",
            category="SALES",
            amount=125,
            memo="opening",
        )

        assert account == AccountRow(account="CASH", name="Cash")
        assert category == CategoryRow(category="SALES", description="Sales")
        assert transaction == TransactionRow(
            txn_id=1,
            date="2026-01-01",
            account="CASH",
            category="SALES",
            amount=125,
            memo="opening",
        )


def test_transaction_foreign_keys_reject_unknown_account_and_category():
    with db_session() as db:
        with pytest.raises(PersistenceError):
            db.transactions.create(
                txn_id=1,
                date="2026-01-01",
                account="MISSING",
                category="MISSING",
                amount=1,
                memo="invalid",
            )
        assert db.transactions.get(txn_id=1) is None


def test_schema_can_be_applied_twice_without_duplicate_objects():
    with db_session() as db:
        db.execute_script('''
            CREATE TABLE IF NOT EXISTS "accounts" ("account" VARCHAR(12) PRIMARY KEY NOT NULL, "name" VARCHAR(40) NOT NULL);
            CREATE TABLE IF NOT EXISTS "categories" ("category" VARCHAR(12) PRIMARY KEY NOT NULL, "description" VARCHAR(40) NOT NULL);
            CREATE TABLE IF NOT EXISTS "transactions" ("txn_id" INTEGER PRIMARY KEY NOT NULL, "date" VARCHAR(10) NOT NULL, "account" VARCHAR(12) NOT NULL REFERENCES "accounts"("account"), "category" VARCHAR(12) NOT NULL REFERENCES "categories"("category"), "amount" INTEGER NOT NULL, "memo" VARCHAR(60) NOT NULL);
        ''')
        assert db.accounts.get(account="MISSING") is None
        assert db.transactions.get(txn_id=1) is None


def test_generated_rows_expose_typed_fields():
    assert [field.name for field in fields(TransactionRow)] == [
        "txn_id", "date", "account", "category", "amount", "memo"
    ]
