"""``ledger txn get``, ``delete``, and ``amend``, against a fresh store per test."""

import csv
import io

import pytest

from cli.testing import cli_runner

TXN_HEADER = ["txn_id", "date", "account", "category", "amount", "memo"]
ACCOUNT = "ZTA1"
CATEGORY = "ZTC1"


def _rows(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out)))


@pytest.fixture
def txn_store(ledger_store, store_open):
    with store_open(ledger_store) as db:
        db.accounts.create(account=ACCOUNT, name="Txn Probe")
        db.categories.create(category=CATEGORY, description="Txn Category")
    return ledger_store


def _add(store_open, path, txn_id, amount, date="2026-04-01", memo=""):
    with store_open(path) as db:
        db.transactions.create(txn_id=txn_id, date=date, account=ACCOUNT, category=CATEGORY, amount=amount, memo=memo)


def _stored(store_open, path, txn_id):
    with store_open(path) as db:
        return db.transactions.get(txn_id=txn_id)


# ── get ───────────────────────────────────────────────────────────────────────────────────


def test_get_prints_every_column_with_two_decimal_amount(txn_store, store_open):
    _add(store_open, txn_store, 101, 1234, date="2026-04-05", memo="get probe")
    code, out, err = cli_runner("txn", "get", "101")
    assert code == 0, err
    assert _rows(out) == [TXN_HEADER, ["101", "2026-04-05", ACCOUNT, CATEGORY, "12.34", "get probe"]]


def test_get_negative_amount_has_leading_minus(txn_store, store_open):
    _add(store_open, txn_store, 102, -1250)
    code, out, _ = cli_runner("txn", "get", "102")
    assert code == 0
    assert _rows(out)[1][4] == "-12.50"


def test_get_whole_amount_has_two_decimals(txn_store, store_open):
    _add(store_open, txn_store, 103, 500)
    assert _rows(cli_runner("txn", "get", "103")[1])[1][4] == "5.00"


def test_get_is_read_only(txn_store, store_open):
    _add(store_open, txn_store, 104, 700)
    cli_runner("txn", "get", "104")
    stored = _stored(store_open, txn_store, 104)
    assert stored.amount == 700
    with store_open(txn_store) as db:
        assert len(db.transactions.list()) == 1


def test_get_absent_exits_four_with_no_stdout(txn_store):
    code, out, _ = cli_runner("txn", "get", "999999991")
    assert code == 4
    assert out == ""


@pytest.mark.parametrize("bad", ["abc", "1.5", "", "12 3"])
def test_get_non_integer_id_exits_three(txn_store, bad):
    code, out, _ = cli_runner("txn", "get", bad)
    assert code == 3
    assert out == ""


@pytest.mark.parametrize("args", [("txn", "get"), ("txn", "get", "1", "2")])
def test_get_wrong_argument_count_is_usage_error(txn_store, args):
    code, out, _ = cli_runner(*args)
    assert code == 2
    assert out == ""


# ── delete ────────────────────────────────────────────────────────────────────────────────


def test_delete_prints_confirmation_and_removes_row(txn_store, store_open):
    _add(store_open, txn_store, 201, -500)
    _add(store_open, txn_store, 202, 9000)
    code, out, err = cli_runner("txn", "delete", "201")
    assert code == 0, err
    assert _rows(out) == [["deleted"], ["201"]]
    assert _stored(store_open, txn_store, 201) is None
    assert _stored(store_open, txn_store, 202).amount == 9000


def test_delete_of_deposit_is_refused_when_payment_would_overdraw(txn_store, store_open):
    _add(store_open, txn_store, 203, 10000)
    _add(store_open, txn_store, 204, -4000)
    code, out, _ = cli_runner("txn", "delete", "203")
    assert code == 3
    assert out == ""
    assert _stored(store_open, txn_store, 203).amount == 10000


def test_delete_of_payment_that_leaves_balance_positive_succeeds(txn_store, store_open):
    _add(store_open, txn_store, 205, 10000)
    _add(store_open, txn_store, 206, -4000)
    assert cli_runner("txn", "delete", "206")[0] == 0
    assert _stored(store_open, txn_store, 206) is None


def test_delete_leaving_exactly_zero_is_allowed(txn_store, store_open):
    _add(store_open, txn_store, 207, 5000)
    _add(store_open, txn_store, 208, 1000)
    _add(store_open, txn_store, 209, -1000)
    assert cli_runner("txn", "delete", "207")[0] == 0
    assert _stored(store_open, txn_store, 207) is None


def test_delete_absent_exits_four_with_no_stdout(txn_store):
    code, out, _ = cli_runner("txn", "delete", "999999992")
    assert code == 4
    assert out == ""


def test_delete_twice_second_attempt_exits_four(txn_store, store_open):
    _add(store_open, txn_store, 209, 300)
    assert cli_runner("txn", "delete", "209")[0] == 0
    assert cli_runner("txn", "delete", "209")[0] == 4


@pytest.mark.parametrize("bad", ["abc", "2.5"])
def test_delete_non_integer_id_exits_three(txn_store, bad):
    code, out, _ = cli_runner("txn", "delete", bad)
    assert code == 3
    assert out == ""


@pytest.mark.parametrize("args", [("txn", "delete"), ("txn", "delete", "1", "2")])
def test_delete_wrong_argument_count_is_usage_error(txn_store, args):
    code, out, _ = cli_runner(*args)
    assert code == 2
    assert out == ""


# ── amend ─────────────────────────────────────────────────────────────────────────────────


def test_amend_prints_updated_row_and_persists_new_amount(txn_store, store_open):
    _add(store_open, txn_store, 301, 10000, memo="amend probe")
    code, out, err = cli_runner("txn", "amend", "301", "50.00")
    assert code == 0, err
    assert _rows(out) == [TXN_HEADER, ["301", "2026-04-01", ACCOUNT, CATEGORY, "50.00", "amend probe"]]
    assert _stored(store_open, txn_store, 301).amount == 5000


def test_amend_changes_only_the_amount(txn_store, store_open):
    _add(store_open, txn_store, 302, 2000, date="2026-05-02", memo="keep this memo")
    assert cli_runner("txn", "amend", "302", "35.50")[0] == 0
    back = _stored(store_open, txn_store, 302)
    assert back.date == "2026-05-02"
    assert back.account == ACCOUNT
    assert back.category == CATEGORY
    assert back.memo == "keep this memo"
    assert back.amount == 3550


def test_amend_to_negative_amount_is_accepted_when_balance_allows(txn_store, store_open):
    _add(store_open, txn_store, 303, 10000)
    _add(store_open, txn_store, 304, 5000)
    code, out, err = cli_runner("txn", "amend", "303", "-10.00")
    assert code == 0, err
    assert _rows(out)[1][4] == "-10.00"


def test_amend_that_overdraws_exits_three_and_keeps_amount(txn_store, store_open):
    _add(store_open, txn_store, 305, 10000)
    _add(store_open, txn_store, 306, -4000)
    code, out, _ = cli_runner("txn", "amend", "305", "30.00")
    assert code == 3
    assert out == ""
    assert _stored(store_open, txn_store, 305).amount == 10000


def test_amend_landing_exactly_on_zero_succeeds(txn_store, store_open):
    _add(store_open, txn_store, 307, 10000)
    _add(store_open, txn_store, 308, -4000)
    assert cli_runner("txn", "amend", "307", "40.00")[0] == 0
    assert _stored(store_open, txn_store, 307).amount == 4000


def test_amend_absent_exits_four_and_creates_nothing(txn_store, store_open):
    code, out, _ = cli_runner("txn", "amend", "999999993", "5.00")
    assert code == 4
    assert out == ""
    assert _stored(store_open, txn_store, 999999993) is None


@pytest.mark.parametrize("bad", ["1.234", "0", "0.00", "abc", "5.", ""])
def test_amend_invalid_amount_exits_three_and_keeps_amount(txn_store, store_open, bad):
    _add(store_open, txn_store, 309, 10000)
    code, out, _ = cli_runner("txn", "amend", "309", bad)
    assert code == 3
    assert out == ""
    assert _stored(store_open, txn_store, 309).amount == 10000


def test_amend_non_integer_id_exits_three(txn_store):
    code, out, _ = cli_runner("txn", "amend", "abc", "5.00")
    assert code == 3
    assert out == ""


@pytest.mark.parametrize("args", [("txn", "amend"), ("txn", "amend", "1"), ("txn", "amend", "1", "2.00", "x")])
def test_amend_wrong_argument_count_is_usage_error(txn_store, args):
    code, out, _ = cli_runner(*args)
    assert code == 2
    assert out == ""
