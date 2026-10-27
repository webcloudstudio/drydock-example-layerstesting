"""``ledger account get``, ``rename``, and ``delete``, against a fresh store per test."""

import csv
import io

import pytest

from cli.testing import cli_runner

ACCOUNT_HEADER = ["account", "name", "transactions", "balance"]
CATEGORY = "ZMAC1"


def _rows(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out)))


def _name(store_open, path, code):
    with store_open(path) as db:
        row = db.accounts.get(account=code)
        return None if row is None else row.name


@pytest.fixture
def account_store(ledger_store, store_open):
    with store_open(ledger_store) as db:
        db.categories.create(category=CATEGORY, description="Manage Category")
    return ledger_store


def _post(store_open, path, code, txn_id, cents):
    with store_open(path) as db:
        db.transactions.create(txn_id=txn_id, date="2026-04-01", account=code, category=CATEGORY, amount=cents, memo="")


# ── get ───────────────────────────────────────────────────────────────────────────────────


def test_get_reports_live_count_and_balance(account_store, store_open):
    cli_runner("account", "add", "ZMG1", "Get Probe")
    _post(store_open, account_store, "ZMG1", 1, 1000)
    _post(store_open, account_store, "ZMG1", 2, -250)
    code, out, err = cli_runner("account", "get", "ZMG1")
    assert code == 0, err
    assert _rows(out) == [ACCOUNT_HEADER, ["ZMG1", "Get Probe", "2", "7.50"]]


def test_get_empty_account_reports_zero_count_and_zero_balance(account_store):
    cli_runner("account", "add", "ZMG2", "Empty Probe")
    code, out, _ = cli_runner("account", "get", "ZMG2")
    assert code == 0
    assert _rows(out)[1] == ["ZMG2", "Empty Probe", "0", "0.00"]


def test_get_reflects_a_posting_made_after_the_last_read(account_store, store_open):
    cli_runner("account", "add", "ZMG3", "Live")
    assert _rows(cli_runner("account", "get", "ZMG3")[1])[1] == ["ZMG3", "Live", "0", "0.00"]
    _post(store_open, account_store, "ZMG3", 5, 4200)
    assert _rows(cli_runner("account", "get", "ZMG3")[1])[1] == ["ZMG3", "Live", "1", "42.00"]


def test_get_absent_exits_four_with_no_stdout(account_store):
    code, out, _ = cli_runner("account", "get", "ZMGNONE")
    assert code == 4
    assert out == ""


def test_get_does_not_write(account_store, store_open):
    cli_runner("account", "add", "ZMG4", "Read Only")
    cli_runner("account", "get", "ZMG4")
    with store_open(account_store) as db:
        assert [row.account for row in db.accounts.list()] == ["ZMG4"]
        assert db.transactions.list() == []


@pytest.mark.parametrize("args", [("account", "get"), ("account", "get", "ZMG5", "EXTRA")])
def test_get_wrong_argument_count_is_usage_error(account_store, args):
    code, out, _ = cli_runner(*args)
    assert code == 2
    assert out == ""


# ── rename ────────────────────────────────────────────────────────────────────────────────


def test_rename_prints_updated_row_and_persists_new_name(account_store, store_open):
    cli_runner("account", "add", "ZMR1", "Old Name")
    code, out, err = cli_runner("account", "rename", "ZMR1", "New Name")
    assert code == 0, err
    assert _rows(out) == [ACCOUNT_HEADER, ["ZMR1", "New Name", "0", "0.00"]]
    assert _name(store_open, account_store, "ZMR1") == "New Name"


def test_rename_changes_only_the_name(account_store, store_open):
    cli_runner("account", "add", "ZMR2", "Before")
    _post(store_open, account_store, "ZMR2", 7, 1250)
    cli_runner("account", "rename", "ZMR2", "After")
    with store_open(account_store) as db:
        row = db.accounts.get(account="ZMR2")
        assert row.account == "ZMR2"
        assert row.name == "After"
        posted = db.transactions.list(account="ZMR2")
        assert [(t.txn_id, t.amount) for t in posted] == [(7, 1250)]


def test_rename_to_largest_name_is_stored_whole(account_store, store_open):
    cli_runner("account", "add", "ZMR3", "Short")
    code, _, err = cli_runner("account", "rename", "ZMR3", "n" * 40)
    assert code == 0, err
    assert _name(store_open, account_store, "ZMR3") == "n" * 40


@pytest.mark.parametrize("bad", ["has,comma", "", "x" * 41, "line\nbreak"])
def test_rename_invalid_name_exits_three_and_keeps_name(account_store, store_open, bad):
    cli_runner("account", "add", "ZMR4", "Keep Me")
    code, out, _ = cli_runner("account", "rename", "ZMR4", bad)
    assert code == 3
    assert out == ""
    assert _name(store_open, account_store, "ZMR4") == "Keep Me"


def test_rename_absent_exits_four_and_creates_nothing(account_store, store_open):
    code, out, _ = cli_runner("account", "rename", "ZMRNONE", "Any Name")
    assert code == 4
    assert out == ""
    assert _name(store_open, account_store, "ZMRNONE") is None


@pytest.mark.parametrize("args", [("account", "rename", "ZMR5"), ("account", "rename", "ZMR5", "A", "B")])
def test_rename_wrong_argument_count_is_usage_error(account_store, args):
    code, out, _ = cli_runner(*args)
    assert code == 2
    assert out == ""


# ── delete ────────────────────────────────────────────────────────────────────────────────


def test_delete_without_transactions_prints_confirmation_and_removes(account_store, store_open):
    cli_runner("account", "add", "ZMD1", "Delete Me")
    code, out, err = cli_runner("account", "delete", "ZMD1")
    assert code == 0, err
    assert _rows(out) == [["deleted"], ["ZMD1"]]
    assert _name(store_open, account_store, "ZMD1") is None


def test_delete_leaves_other_accounts_untouched(account_store, store_open):
    cli_runner("account", "add", "ZMD2", "Stays")
    cli_runner("account", "add", "ZMD3", "Goes")
    cli_runner("account", "delete", "ZMD3")
    assert _name(store_open, account_store, "ZMD2") == "Stays"


def test_delete_account_with_transaction_is_refused(account_store, store_open):
    cli_runner("account", "add", "ZMD4", "In Use")
    _post(store_open, account_store, "ZMD4", 11, 500)
    code, out, _ = cli_runner("account", "delete", "ZMD4")
    assert code == 3
    assert out == ""
    assert _name(store_open, account_store, "ZMD4") == "In Use"
    with store_open(account_store) as db:
        assert db.transactions.get(txn_id=11) is not None


def test_delete_absent_exits_four_with_no_stdout(account_store):
    code, out, _ = cli_runner("account", "delete", "ZMDNONE")
    assert code == 4
    assert out == ""


def test_delete_twice_second_attempt_exits_four(account_store):
    cli_runner("account", "add", "ZMD5", "Once")
    assert cli_runner("account", "delete", "ZMD5")[0] == 0
    code, out, _ = cli_runner("account", "delete", "ZMD5")
    assert code == 4
    assert out == ""


@pytest.mark.parametrize("args", [("account", "delete"), ("account", "delete", "ZMD6", "EXTRA")])
def test_delete_wrong_argument_count_is_usage_error(account_store, args):
    code, out, _ = cli_runner(*args)
    assert code == 2
    assert out == ""
