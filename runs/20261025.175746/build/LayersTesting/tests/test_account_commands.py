"""``ledger account get|add|rename|delete``: read back through the store after every command."""

from __future__ import annotations

import csv
import io

import pytest

from cli.testing import cli_runner


def _rows(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out)))


def _post(scratch_db, account: str, cents: int, txn_id: int) -> None:
    if scratch_db.categories.get(category="ACCTC") is None:
        scratch_db.categories.create(category="ACCTC", description="Account Probe")
    scratch_db.transactions.create(
        txn_id=txn_id, date="2098-01-01", account=account, category="ACCTC", amount=cents, memo=""
    )


# account get


def test_get_prints_name_count_and_balance_of_stored_transactions(scratch_db):
    scratch_db.accounts.create(account="GET1", name="Get One")
    _post(scratch_db, "GET1", 10000, 1001)
    _post(scratch_db, "GET1", -2550, 1002)
    code, out, _ = cli_runner("account", "get", "GET1")
    assert code == 0
    assert _rows(out) == [["account", "name", "transactions", "balance"], ["GET1", "Get One", "2", "74.50"]]


def test_get_of_account_without_transactions_reports_zero(scratch_db):
    scratch_db.accounts.create(account="GET2", name="Empty")
    code, out, _ = cli_runner("account", "get", "GET2")
    assert code == 0
    assert _rows(out)[1] == ["GET2", "Empty", "0", "0.00"]


def test_get_shows_negative_balance_with_leading_minus(scratch_db):
    scratch_db.accounts.create(account="GET3", name="Neg")
    _post(scratch_db, "GET3", -5, 1003)
    code, out, _ = cli_runner("account", "get", "GET3")
    assert code == 0
    assert _rows(out)[1][3] == "-0.05"


def test_get_absent_account_exits_4_with_no_stdout(scratch_db):
    code, out, _ = cli_runner("account", "get", "GETNONE")
    assert code == 4
    assert out == ""


@pytest.mark.parametrize("argv", [["account", "get"], ["account", "get", "A", "B"]])
def test_get_wrong_argument_count_is_a_usage_error(scratch_db, argv):
    code, out, _ = cli_runner(*argv)
    assert code == 2
    assert out == ""


# account add


def test_add_stores_account_and_prints_its_zero_row(scratch_db):
    code, out, _ = cli_runner("account", "add", "ADD1", "Float")
    assert code == 0
    assert _rows(out) == [["account", "name", "transactions", "balance"], ["ADD1", "Float", "0", "0.00"]]
    assert scratch_db.accounts.get(account="ADD1").name == "Float"


@pytest.mark.parametrize("code_text", ["A", "A" * 12, "Z9"])
def test_add_accepts_codes_at_and_inside_bounds(scratch_db, code_text):
    code, _, _ = cli_runner("account", "add", code_text, "Bounds")
    assert code == 0
    assert scratch_db.accounts.get(account=code_text) is not None


def test_add_accepts_name_at_maximum_length(scratch_db):
    code, _, _ = cli_runner("account", "add", "ADD2", "N" * 40)
    assert code == 0
    assert scratch_db.accounts.get(account="ADD2").name == "N" * 40


def test_add_duplicate_code_exits_3_and_keeps_the_original(scratch_db):
    scratch_db.accounts.create(account="ADD3", name="Original")
    code, out, _ = cli_runner("account", "add", "ADD3", "Replacement")
    assert code == 3
    assert out == ""
    assert scratch_db.accounts.get(account="ADD3").name == "Original"


@pytest.mark.parametrize("code_text", ["lower", "A" * 13, "BAD-CODE", ""])
def test_add_invalid_code_exits_3_and_stores_nothing(scratch_db, code_text):
    before = len(scratch_db.accounts.list())
    code, out, _ = cli_runner("account", "add", code_text, "Valid")
    assert code == 3
    assert out == ""
    assert len(scratch_db.accounts.list()) == before


@pytest.mark.parametrize("name_text", ["", "N" * 41, "has,comma"])
def test_add_invalid_name_exits_3_and_stores_nothing(scratch_db, name_text):
    code, out, _ = cli_runner("account", "add", "ADD4", name_text)
    assert code == 3
    assert out == ""
    assert scratch_db.accounts.get(account="ADD4") is None


@pytest.mark.parametrize("argv", [["account", "add", "ADD5"], ["account", "add", "ADD5", "A", "extra"]])
def test_add_wrong_argument_count_is_a_usage_error(scratch_db, argv):
    code, out, _ = cli_runner(*argv)
    assert code == 2
    assert out == ""
    assert scratch_db.accounts.get(account="ADD5") is None


# account rename


def test_rename_changes_only_the_name_and_keeps_transactions(scratch_db):
    scratch_db.accounts.create(account="REN1", name="Before")
    _post(scratch_db, "REN1", 500, 2001)
    code, out, _ = cli_runner("account", "rename", "REN1", "After")
    assert code == 0
    assert _rows(out)[1] == ["REN1", "After", "1", "5.00"]
    assert scratch_db.accounts.get(account="REN1").name == "After"
    assert scratch_db.transactions.get(txn_id=2001).account == "REN1"


def test_rename_absent_account_exits_4_and_creates_nothing(scratch_db):
    code, out, _ = cli_runner("account", "rename", "RENNONE", "New")
    assert code == 4
    assert out == ""
    assert scratch_db.accounts.get(account="RENNONE") is None


@pytest.mark.parametrize("name_text", ["", "N" * 41, "has,comma"])
def test_rename_invalid_name_exits_3_and_keeps_the_name(scratch_db, name_text):
    scratch_db.accounts.create(account="REN2", name="Keep")
    code, out, _ = cli_runner("account", "rename", "REN2", name_text)
    assert code == 3
    assert out == ""
    assert scratch_db.accounts.get(account="REN2").name == "Keep"


@pytest.mark.parametrize("argv", [["account", "rename", "REN3"], ["account", "rename", "REN3", "A", "B"]])
def test_rename_wrong_argument_count_is_a_usage_error(scratch_db, argv):
    scratch_db.accounts.create(account="REN3", name="Usage")
    code, out, _ = cli_runner(*argv)
    assert code == 2
    assert out == ""
    assert scratch_db.accounts.get(account="REN3").name == "Usage"


# account delete


def test_delete_unused_account_prints_deleted_and_removes_it(scratch_db):
    scratch_db.accounts.create(account="DEL1", name="Unused")
    code, out, _ = cli_runner("account", "delete", "DEL1")
    assert code == 0
    assert _rows(out) == [["deleted"], ["DEL1"]]
    assert scratch_db.accounts.get(account="DEL1") is None


def test_delete_account_with_transactions_exits_3_and_removes_nothing(scratch_db):
    scratch_db.accounts.create(account="DEL2", name="Used")
    _post(scratch_db, "DEL2", 900, 2101)
    code, out, _ = cli_runner("account", "delete", "DEL2")
    assert code == 3
    assert out == ""
    assert scratch_db.accounts.get(account="DEL2") is not None
    assert scratch_db.transactions.get(txn_id=2101) is not None


def test_delete_absent_account_exits_4(scratch_db):
    code, out, _ = cli_runner("account", "delete", "DELNONE")
    assert code == 4
    assert out == ""


def test_get_after_delete_exits_4(scratch_db):
    scratch_db.accounts.create(account="DEL3", name="Gone")
    assert cli_runner("account", "delete", "DEL3")[0] == 0
    assert cli_runner("account", "get", "DEL3")[0] == 4


@pytest.mark.parametrize("argv", [["account", "delete"], ["account", "delete", "DEL4", "extra"]])
def test_delete_wrong_argument_count_is_a_usage_error(scratch_db, argv):
    scratch_db.accounts.create(account="DEL4", name="Usage")
    code, out, _ = cli_runner(*argv)
    assert code == 2
    assert out == ""
    assert scratch_db.accounts.get(account="DEL4") is not None
