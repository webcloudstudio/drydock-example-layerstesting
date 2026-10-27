"""``ledger account add`` and the ``account_row`` helper, against a fresh store per test."""

import csv
import io

import pytest

from cli.testing import cli_runner
from ledger_core.accounts import account_row

ACCOUNT_HEADER = ["account", "name", "transactions", "balance"]


def _rows(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out)))


def test_add_prints_header_and_zero_row(ledger_store):
    code, out, err = cli_runner("account", "add", "ZZNA1", "Add Probe")
    assert code == 0, err
    assert _rows(out) == [ACCOUNT_HEADER, ["ZZNA1", "Add Probe", "0", "0.00"]]


def test_added_account_reads_back_from_the_store(ledger_store, store_open):
    cli_runner("account", "add", "ZZNA2", "Read Back")
    with store_open(ledger_store) as db:
        row = db.accounts.get(account="ZZNA2")
        assert row is not None
        assert row.name == "Read Back"


def test_added_account_is_listed_once(ledger_store, store_open):
    cli_runner("account", "add", "ZZNA3", "Listed")
    with store_open(ledger_store) as db:
        assert [row.account for row in db.accounts.list()] == ["ZZNA3"]


def test_duplicate_code_is_rejected_and_name_unchanged(ledger_store, store_open):
    code, _, err = cli_runner("account", "add", "ZZNB1", "Original Name")
    assert code == 0, err
    code, out, _ = cli_runner("account", "add", "ZZNB1", "Different Name")
    assert code == 3
    assert out == ""
    with store_open(ledger_store) as db:
        assert db.accounts.get(account="ZZNB1").name == "Original Name"


@pytest.mark.parametrize("bad", ["zznc1", "ABCDEFGHIJKLM", "ZZ-NC", "ZZ NC", "", "ZZé"])
def test_invalid_code_is_rejected_and_stores_nothing(ledger_store, store_open, bad):
    code, out, _ = cli_runner("account", "add", bad, "Valid Name")
    assert code == 3
    assert out == ""
    with store_open(ledger_store) as db:
        assert db.accounts.list() == []


@pytest.mark.parametrize("bad", ["", "n" * 41, "has,comma", "line\nbreak"])
def test_invalid_name_is_rejected_and_stores_nothing(ledger_store, store_open, bad):
    code, out, _ = cli_runner("account", "add", "ZZND1", bad)
    assert code == 3
    assert out == ""
    with store_open(ledger_store) as db:
        assert db.accounts.get(account="ZZND1") is None


def test_largest_code_and_name_are_stored_whole(ledger_store, store_open):
    code_text, name = "Z" * 12, "n" * 40
    code, out, err = cli_runner("account", "add", code_text, name)
    assert code == 0, err
    assert _rows(out)[1] == [code_text, name, "0", "0.00"]
    with store_open(ledger_store) as db:
        assert db.accounts.get(account=code_text).name == name


def test_single_character_code_and_name_are_accepted(ledger_store):
    code, out, err = cli_runner("account", "add", "A", "n")
    assert code == 0, err
    assert _rows(out)[1] == ["A", "n", "0", "0.00"]


@pytest.mark.parametrize(
    "args",
    [("account", "add"), ("account", "add", "ZZNE1"), ("account", "add", "ZZNE1", "Name", "Extra")],
)
def test_wrong_argument_count_is_usage_error(ledger_store, args):
    code, out, _ = cli_runner(*args)
    assert code == 2
    assert out == ""


def test_account_row_reports_count_and_cent_balance(ledger_store, store_open):
    amounts = [10000, -2550, 1]
    with store_open(ledger_store) as db:
        db.accounts.create(account="ZZNF1", name="Helper Probe")
        db.categories.create(category="ZZNFC", description="Helper Category")
        for i, cents in enumerate(amounts):
            db.transactions.create(txn_id=930000000 + i, date="2026-03-01", account="ZZNF1",
                                   category="ZZNFC", amount=cents, memo="")
        row = account_row(db, "ZZNF1")
    assert tuple(row) == ("ZZNF1", "Helper Probe", len(amounts), sum(amounts))


def test_account_row_is_none_for_absent_account(ledger_store, store_open):
    with store_open(ledger_store) as db:
        assert account_row(db, "ZZNFNONE") is None


def test_account_row_is_zero_for_account_without_transactions(ledger_store, store_open):
    cli_runner("account", "add", "ZZNG1", "Empty")
    with store_open(ledger_store) as db:
        assert account_row(db, "ZZNG1") == ("ZZNG1", "Empty", 0, 0)
