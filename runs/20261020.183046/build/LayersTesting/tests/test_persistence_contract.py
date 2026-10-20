from __future__ import annotations

from persistence.testing import db_session


def test_declared_account_operations_round_trip() -> None:
    with db_session() as db:
        created = db.accounts.create(account="cash", name="Cash")
        assert created.account == "cash"
        assert db.accounts.get(account="cash") == created
        listed = db.accounts.list()
        assert [(row.account, row.name) for row in listed] == [("cash", "Cash")]

        assert db.accounts.update(account="cash", name="Main cash") == 1
        assert db.accounts.get(account="cash").name == "Main cash"
        assert db.accounts.delete(account="cash") == 1
        assert db.accounts.get(account="cash") is None


def test_declared_category_and_transaction_operations_round_trip() -> None:
    with db_session() as db:
        # Categories intentionally declare read operations only.
        assert db.categories.list() == []
        assert db.categories.get(category="food") is None

        assert db.transactions.list() == []
        assert db.transactions.get(txn_id=1) is None
        assert db.transactions.update(txn_id=1, amount=-1300) == 0
        assert db.transactions.delete(txn_id=1) == 0
        assert db.transactions.get(txn_id=1) is None
