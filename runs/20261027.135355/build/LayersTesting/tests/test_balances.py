"""Balance rule: changes are judged by net effect per account, and a check never writes."""

import pytest

from ledger_core.balances import Delete, Edit, Insert, check_no_negative, current_balance
from ledger_core.errors import NotFound, Rejected
from persistence.testing import db_session

CATEGORY = "ZZBRCAT"


def _seed(db, account, amounts, first_txn_id):
    db.accounts.create(account=account, name="Balance Test")
    db.categories.create(category=CATEGORY, description="Balance Cat")
    for offset, cents in enumerate(amounts):
        db.transactions.create(txn_id=first_txn_id + offset, date="2026-05-01", account=account,
                               category=CATEGORY, amount=cents, memo="")


def _count(db, *accounts):
    return sum(len(db.transactions.list(account=account)) for account in accounts)


def test_current_balance_sums_stored_amounts():
    with db_session() as db:
        _seed(db, "ZZBRA", [1000, -300, -50], 910000001)
        assert current_balance(db, "ZZBRA") == 650


def test_current_balance_is_zero_for_account_without_transactions():
    with db_session() as db:
        db.accounts.create(account="ZZBRE", name="Empty Test")
        assert current_balance(db, "ZZBRE") == 0


def test_insert_landing_on_zero_is_allowed():
    with db_session() as db:
        _seed(db, "ZZBRB", [700], 910000011)
        assert check_no_negative(db, [Insert("ZZBRB", -700)]) is None


def test_insert_one_cent_below_zero_is_rejected_and_writes_nothing():
    with db_session() as db:
        _seed(db, "ZZBRC", [700], 910000021)
        before = _count(db, "ZZBRC")
        with pytest.raises(Rejected) as info:
            check_no_negative(db, [Insert("ZZBRC", -701)])
        assert info.value.exit_code == 3
        assert _count(db, "ZZBRC") == before


def test_insert_into_new_account_accepts_positive_and_rejects_negative():
    with db_session() as db:
        db.accounts.create(account="ZZBRD", name="Fresh Test")
        assert check_no_negative(db, [Insert("ZZBRD", 500)]) is None
        with pytest.raises(Rejected):
            check_no_negative(db, [Insert("ZZBRD", -1)])


def test_edit_below_what_debits_need_is_rejected_and_stored_amount_unchanged():
    with db_session() as db:
        _seed(db, "ZZBRE2", [1000, -300], 910000031)
        assert check_no_negative(db, [Edit(910000031, 300)]) is None
        with pytest.raises(Rejected) as info:
            check_no_negative(db, [Edit(910000031, 299)])
        assert info.value.exit_code == 3
        assert db.transactions.get(txn_id=910000031).amount == 1000


def test_delete_of_funding_credit_is_rejected_and_credit_remains():
    with db_session() as db:
        _seed(db, "ZZBRF", [1000, -300], 910000041)
        assert check_no_negative(db, [Delete(910000042)]) is None
        with pytest.raises(Rejected) as info:
            check_no_negative(db, [Delete(910000041)])
        assert info.value.exit_code == 3
        assert db.transactions.get(txn_id=910000041) is not None


def test_edit_or_delete_of_missing_transaction_is_not_found():
    with db_session() as db:
        with pytest.raises(NotFound) as info:
            check_no_negative(db, [Edit(919999999, 100)])
        assert info.value.exit_code == 4
        with pytest.raises(NotFound):
            check_no_negative(db, [Delete(919999999)])


def test_combined_changes_judged_by_net_effect_in_either_order():
    with db_session() as db:
        _seed(db, "ZZBRG", [700], 910000051)
        credit, debit = Insert("ZZBRG", 500), Insert("ZZBRG", -1100)
        assert check_no_negative(db, [credit, debit]) is None
        assert check_no_negative(db, [debit, credit]) is None


def test_combined_changes_netting_below_zero_are_rejected():
    with db_session() as db:
        _seed(db, "ZZBRH", [700], 910000061)
        with pytest.raises(Rejected):
            check_no_negative(db, [Insert("ZZBRH", 500), Insert("ZZBRH", -1300)])


def test_one_overdrawn_account_rejects_whole_set_and_writes_nothing():
    with db_session() as db:
        _seed(db, "ZZBRI", [900], 910000071)
        db.accounts.create(account="ZZBRJ", name="Poor Test")
        db.transactions.create(txn_id=910000072, date="2026-05-01", account="ZZBRJ",
                               category=CATEGORY, amount=100, memo="")
        before = _count(db, "ZZBRI", "ZZBRJ")
        with pytest.raises(Rejected):
            check_no_negative(db, [Insert("ZZBRI", -900), Insert("ZZBRJ", -101)])
        assert _count(db, "ZZBRI", "ZZBRJ") == before


def test_untouched_account_does_not_affect_result():
    with db_session() as db:
        _seed(db, "ZZBRK", [100], 910000081)
        db.accounts.create(account="ZZBRL", name="Other Test")
        db.transactions.create(txn_id=910000082, date="2026-05-01", account="ZZBRL",
                               category=CATEGORY, amount=-500, memo="")
        assert check_no_negative(db, [Insert("ZZBRK", -100)]) is None
