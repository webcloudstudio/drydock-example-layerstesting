"""Non-negative balance: a balance below zero is rejected with exit code 3, and nothing is written."""

import pytest

from balance import RejectedError, ensure_non_negative
from persistence.testing import db_session


def _seed(db, *, account: str = "CASH1") -> None:
    db.categories.create(category="OPENING", description="Opening balance")
    db.accounts.create(account=account, name="Till")


def _txn(db, txn_id: int, amount: int, account: str = "CASH1") -> None:
    db.transactions.create(
        txn_id=txn_id, date="2026-01-01", account=account, category="OPENING", amount=amount, memo=""
    )


def test_negative_balance_raises_with_exit_code_3() -> None:
    with db_session() as db:
        _seed(db)
        _txn(db, 1, -500)

        with pytest.raises(RejectedError) as caught:
            ensure_non_negative(db, ["CASH1"])

        assert caught.value.exit_code == 3


def test_zero_balance_does_not_raise() -> None:
    with db_session() as db:
        _seed(db)
        _txn(db, 1, 500)
        _txn(db, 2, -500)

        ensure_non_negative(db, ["CASH1"])


def test_balance_is_sum_of_all_transactions() -> None:
    with db_session() as db:
        _seed(db)
        _txn(db, 1, 500)
        _txn(db, 2, -200)

        ensure_non_negative(db, ["CASH1"])
        assert len(db.transactions.list()) == 2


def test_balance_of_one_cent_below_zero_raises() -> None:
    with db_session() as db:
        _seed(db)
        _txn(db, 1, 499)
        _txn(db, 2, -500)

        with pytest.raises(RejectedError):
            ensure_non_negative(db, ["CASH1"])


def test_negative_amounts_summing_below_zero_raise() -> None:
    with db_session() as db:
        _seed(db)
        _txn(db, 1, -300)
        _txn(db, 2, -300)

        with pytest.raises(RejectedError):
            ensure_non_negative(db, ["CASH1"])


def test_account_with_no_transactions_has_zero_balance() -> None:
    with db_session() as db:
        _seed(db)

        ensure_non_negative(db, ["CASH1"])


def test_empty_account_list_does_not_raise() -> None:
    with db_session() as db:
        _seed(db)
        _txn(db, 1, -500)

        ensure_non_negative(db, [])


def test_unknown_account_has_zero_balance() -> None:
    with db_session() as db:
        _seed(db)

        ensure_non_negative(db, ["NOPE"])


def test_only_named_accounts_are_checked() -> None:
    with db_session() as db:
        _seed(db)
        db.accounts.create(account="BANK1", name="Bank")
        _txn(db, 1, -500, account="CASH1")
        _txn(db, 2, 900, account="BANK1")

        ensure_non_negative(db, ["BANK1"])


def test_negative_account_among_several_named_raises() -> None:
    with db_session() as db:
        _seed(db)
        db.accounts.create(account="BANK1", name="Bank")
        _txn(db, 1, 900, account="BANK1")
        _txn(db, 2, -500, account="CASH1")

        with pytest.raises(RejectedError):
            ensure_non_negative(db, ["BANK1", "CASH1"])


def test_duplicate_account_names_are_checked_once() -> None:
    with db_session() as db:
        _seed(db)
        _txn(db, 1, 100)

        ensure_non_negative(db, ["CASH1", "CASH1"])


def test_rejection_changes_no_transaction_rows() -> None:
    with db_session() as db:
        _seed(db)
        _txn(db, 1, -500)
        before = db.transactions.list()

        with pytest.raises(RejectedError):
            ensure_non_negative(db, ["CASH1"])

        assert db.transactions.list() == before


def test_accepted_check_changes_no_rows() -> None:
    with db_session() as db:
        _seed(db)
        _txn(db, 1, 500)
        before = (db.accounts.list(), db.transactions.list())

        ensure_non_negative(db, ["CASH1"])

        assert (db.accounts.list(), db.transactions.list()) == before


def test_check_reads_current_database_state_each_call() -> None:
    with db_session() as db:
        _seed(db)
        _txn(db, 1, 500)
        ensure_non_negative(db, ["CASH1"])

        _txn(db, 2, -600)

        with pytest.raises(RejectedError):
            ensure_non_negative(db, ["CASH1"])


def test_large_integer_cents_are_summed_exactly() -> None:
    with db_session() as db:
        _seed(db)
        _txn(db, 1, 10**15 + 1)
        _txn(db, 2, -(10**15))

        ensure_non_negative(db, ["CASH1"])


def test_rejected_error_is_an_exception() -> None:
    assert issubclass(RejectedError, Exception)
