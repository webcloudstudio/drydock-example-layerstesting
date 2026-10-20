"""The declared persistence contract for accounts, categories, and transactions.

Every case acts through the generated ``db.<table>.<verb>`` surface on a fresh temporary store
built from ``schema.sql``, then reads the state back through the same surface.
"""

import pytest

from persistence import PersistenceError, UnknownOperation
from persistence.schema import AccountRow
from persistence.testing import db_session


def _txn(db, txn_id=1, account="CASH", category="FOOD", amount=-1999, memo="lunch", date="2026-10-01"):
    db.transactions.create(
        txn_id=txn_id, date=date, account=account, category=category, amount=amount, memo=memo
    )


@pytest.fixture
def db():
    with db_session() as database:
        yield database


def test_account_round_trips_through_get(db):
    db.accounts.create(account="CASH", name="Cash on hand")
    assert db.accounts.get(account="CASH") == AccountRow(account="CASH", name="Cash on hand")


def test_account_get_absent_returns_none(db):
    assert db.accounts.get(account="NOPE") is None


def test_account_list_is_empty_on_fresh_store(db):
    assert db.accounts.list() == []


def test_account_list_returns_every_row(db):
    db.accounts.create(account="CASH", name="Cash")
    db.accounts.create(account="BANK1", name="Checking")
    assert sorted(row.account for row in db.accounts.list()) == ["BANK1", "CASH"]


def test_account_rename_reads_back_new_name(db):
    db.accounts.create(account="CASH", name="Cash")
    assert db.accounts.update(account="CASH", name="Petty cash") == 1
    assert db.accounts.get(account="CASH").name == "Petty cash"


def test_account_delete_removes_row(db):
    db.accounts.create(account="CASH", name="Cash")
    assert db.accounts.delete(account="CASH") == 1
    assert db.accounts.get(account="CASH") is None


def test_account_delete_absent_removes_nothing(db):
    assert db.accounts.delete(account="NOPE") == 0


def test_account_accepts_maximum_length_code_and_name(db):
    db.accounts.create(account="A" * 12, name="N" * 40)
    row = db.accounts.get(account="A" * 12)
    assert row.name == "N" * 40


def test_category_round_trips_through_get(db):
    db.categories.create(category="FOOD", description="Groceries and dining")
    assert db.categories.get(category="FOOD").description == "Groceries and dining"


def test_category_list_returns_every_row(db):
    db.categories.create(category="FOOD", description="Food")
    db.categories.create(category="RENT", description="Rent")
    assert sorted(row.category for row in db.categories.list()) == ["FOOD", "RENT"]


def test_transaction_round_trips_integer_cents(db):
    db.accounts.create(account="CASH", name="Cash")
    db.categories.create(category="FOOD", description="Food")
    _txn(db, txn_id=7, amount=-1999)
    row = db.transactions.get(txn_id=7)
    assert row.txn_id == 7
    assert row.date == "2026-10-01"
    assert row.account == "CASH"
    assert row.category == "FOOD"
    assert row.amount == -1999
    assert type(row.amount) is int
    assert row.memo == "lunch"


def test_transaction_positive_amount_round_trips(db):
    db.accounts.create(account="CASH", name="Cash")
    db.categories.create(category="FOOD", description="Food")
    _txn(db, amount=250000)
    assert db.transactions.get(txn_id=1).amount == 250000


def test_transaction_absent_memo_takes_empty_default(db):
    db.accounts.create(account="CASH", name="Cash")
    db.categories.create(category="FOOD", description="Food")
    db.transactions.create(txn_id=1, date="2026-10-01", account="CASH", category="FOOD", amount=5)
    assert db.transactions.get(txn_id=1).memo == ""


def test_transaction_memo_at_sixty_characters_round_trips(db):
    db.accounts.create(account="CASH", name="Cash")
    db.categories.create(category="FOOD", description="Food")
    _txn(db, memo="m" * 60)
    assert db.transactions.get(txn_id=1).memo == "m" * 60


def test_transaction_list_returns_every_row(db):
    db.accounts.create(account="CASH", name="Cash")
    db.categories.create(category="FOOD", description="Food")
    _txn(db, txn_id=1)
    _txn(db, txn_id=2)
    assert sorted(row.txn_id for row in db.transactions.list()) == [1, 2]


def test_transaction_amend_reads_back_new_amount(db):
    db.accounts.create(account="CASH", name="Cash")
    db.categories.create(category="FOOD", description="Food")
    _txn(db, amount=-100)
    assert db.transactions.update(txn_id=1, amount=-250) == 1
    assert db.transactions.get(txn_id=1).amount == -250


def test_transaction_delete_removes_row(db):
    db.accounts.create(account="CASH", name="Cash")
    db.categories.create(category="FOOD", description="Food")
    _txn(db)
    assert db.transactions.delete(txn_id=1) == 1
    assert db.transactions.get(txn_id=1) is None


def test_transaction_rejects_unknown_account(db):
    db.categories.create(category="FOOD", description="Food")
    with pytest.raises(PersistenceError):
        _txn(db, account="NOPE")
    assert db.transactions.list() == []


def test_transaction_rejects_unknown_category(db):
    db.accounts.create(account="CASH", name="Cash")
    with pytest.raises(PersistenceError):
        _txn(db, category="NOPE")
    assert db.transactions.list() == []


def test_undeclared_verb_raises_unknown_operation(db):
    with pytest.raises(UnknownOperation):
        db.accounts.upsert(account="CASH", name="Cash")


def test_each_test_gets_a_fresh_store(db):
    assert db.accounts.list() == []
