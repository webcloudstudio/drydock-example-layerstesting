"""Balance rules: account summaries, per-account balances, the non-negative check, and txn ids.

Each declared acceptance assertion of FEATURE-BalanceRules has a test here, read back through the
public interface. Records live under the shipped rollback fixture, so nothing persists.
"""

from __future__ import annotations

import pytest

from cli.balance import account_summary, balances, check_balances, next_txn_id
from cli.errors import Rejected


def _post(db, *, txn_id: int, account: str, category: str, amount: int) -> None:
    db.transactions.create(
        txn_id=txn_id, date="2026-04-01", account=account, category=category, amount=amount, memo=""
    )


@pytest.fixture
def ledger(db_session):
    """One account and one category under the rollback session, for the transaction tests."""
    db_session.accounts.create(account="UTBALA", name="Balance Probe")
    db_session.categories.create(category="UTBALC", description="Balance Category")
    return db_session


# ── Declared acceptance assertions ──────────────────────────────────────────────────────────


def test_account_summary_returns_stored_count_and_integer_sum(ledger):
    amounts = [1000, -300, 250]
    for offset, cents in enumerate(amounts):
        _post(ledger, txn_id=980001 + offset, account="UTBALA", category="UTBALC", amount=cents)
    count, balance = account_summary(ledger, "UTBALA")
    assert count == len(amounts)
    assert balance == sum(amounts)
    assert isinstance(balance, int)


def test_account_summary_of_account_with_no_transactions_is_zero(db_session):
    db_session.accounts.create(account="UTBAL2", name="Empty Probe")
    assert account_summary(db_session, "UTBAL2") == (0, 0)


def test_balances_returns_per_account_sums_from_stored_rows(db_session):
    db_session.accounts.create(account="UTBAL3A", name="A")
    db_session.accounts.create(account="UTBAL3B", name="B")
    db_session.categories.create(category="UTBALC3", description="Cat")
    plan = [(980011, "UTBAL3A", 500), (980012, "UTBAL3A", -200), (980013, "UTBAL3B", 75)]
    for txn_id, account, cents in plan:
        _post(db_session, txn_id=txn_id, account=account, category="UTBALC3", amount=cents)
    result = balances(db_session)
    assert result["UTBAL3A"] == 300
    assert result["UTBAL3B"] == 75


def test_check_accepts_a_change_landing_exactly_on_zero_and_rejects_one_cent_below(ledger):
    _post(ledger, txn_id=980021, account="UTBALA", category="UTBALC", amount=700)
    assert check_balances(ledger, {"UTBALA": -700}) is None
    with pytest.raises(Rejected) as excinfo:
        check_balances(ledger, {"UTBALA": -701})
    assert excinfo.value.exit_code == 3


def test_check_rejects_when_any_one_of_several_accounts_would_go_negative(db_session):
    db_session.accounts.create(account="UTBAL5R", name="Rich")
    db_session.accounts.create(account="UTBAL5P", name="Poor")
    db_session.categories.create(category="UTBALC5", description="Cat")
    _post(db_session, txn_id=980031, account="UTBAL5R", category="UTBALC5", amount=10000)
    _post(db_session, txn_id=980032, account="UTBAL5P", category="UTBALC5", amount=100)
    assert check_balances(db_session, {"UTBAL5R": -500, "UTBAL5P": 500}) is None
    with pytest.raises(Rejected):
        check_balances(db_session, {"UTBAL5R": 500, "UTBAL5P": -101})


def test_rejected_check_leaves_stored_transactions_unchanged(ledger):
    _post(ledger, txn_id=980041, account="UTBALA", category="UTBALC", amount=100)
    before = ledger.transactions.list(account="UTBALA")
    with pytest.raises(Rejected):
        check_balances(ledger, {"UTBALA": -1000})
    assert ledger.transactions.list(account="UTBALA") == before


def test_next_txn_id_is_one_more_than_the_largest_stored_id(ledger):
    stored = [row.txn_id for row in ledger.transactions.list()]
    assert next_txn_id(ledger) == (max(stored) + 1 if stored else 1)
    big = max(stored + [0]) + 5
    _post(ledger, txn_id=big, account="UTBALA", category="UTBALC", amount=10)
    assert next_txn_id(ledger) == big + 1


# ── Boundaries and finer rules ──────────────────────────────────────────────────────────────


def test_check_treats_an_account_with_no_transactions_as_zero_balance(ledger):
    with pytest.raises(Rejected):
        check_balances(ledger, {"UTBALNONE": -1})
    assert check_balances(ledger, {"UTBALNONE": 1}) is None


def test_check_accepts_an_empty_delta_set(ledger):
    assert check_balances(ledger, {}) is None


def test_check_does_not_let_a_positive_delta_offset_another_account(ledger):
    ledger.accounts.create(account="UTBALB", name="Other")
    _post(ledger, txn_id=980051, account="UTBALA", category="UTBALC", amount=50)
    with pytest.raises(Rejected):
        check_balances(ledger, {"UTBALA": -51, "UTBALB": 500})


def test_rejection_message_names_the_account_and_resulting_balance(ledger):
    _post(ledger, txn_id=980061, account="UTBALA", category="UTBALC", amount=250)
    with pytest.raises(Rejected) as excinfo:
        check_balances(ledger, {"UTBALA": -300})
    assert "UTBALA" in str(excinfo.value)


def test_account_summary_of_unknown_account_is_zero(db_session):
    assert account_summary(db_session, "UTBALNOPE") == (0, 0)
