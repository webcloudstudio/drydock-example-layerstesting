"""No negative balance across every writing command that changes a transaction.

Assembly checks for FEATURE-NoNegativeBalance. Each case drives a command that would leave an
account below zero, asserts exit 3 with empty stdout, and reads the balances and row counts back
through the persistence interface and ``cli_runner`` to confirm nothing changed. Every test runs
against a fresh store.
"""

import csv
import io
from decimal import Decimal

import pytest

from cli.testing import cli_runner

HEADER = ["txn_id", "date", "account", "category", "amount", "memo"]


def _rows(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out)))


def _counts() -> dict[str, int]:
    code, out, err = cli_runner("count")
    assert code == 0, err
    return {row[0]: int(row[1]) for row in _rows(out)[1:]}


def _write_csv(path, rows) -> str:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(HEADER)
        writer.writerows(rows)
    return str(path)


# ── load transactions ──────────────────────────────────────────────────────────────────────


def test_load_whose_later_rows_overdraw_is_rejected_whole(ledger_store, store_open, tmp_path):
    acct, cat = "ZZNL1", "ZZNLC"
    with store_open(ledger_store) as db:
        db.categories.create(category=cat, description="Load Probe")
    assert cli_runner("account", "add", acct, "Load Probe")[0] == 0
    before = _counts()

    rows = [
        ["800000001", "2099-03-01", acct, cat, "50.00", "in"],
        ["800000002", "2099-03-02", acct, cat, "-30.00", "out one"],
        ["800000003", "2099-03-03", acct, cat, "-30.00", "out two"],
    ]
    path = _write_csv(tmp_path / "txns.csv", rows)
    code, out, err = cli_runner("load", "transactions", path)
    assert code == 3
    assert out == ""
    assert _counts() == before

    code, _, _ = cli_runner("txn", "get", rows[0][0])
    assert code == 4
    code, out, err = cli_runner("account", "get", acct)
    assert code == 0, err
    assert _rows(out)[1][2] == "0"
    assert _rows(out)[1][3] == "0.00"


# ── txn post ───────────────────────────────────────────────────────────────────────────────


def test_post_outflow_beyond_balance_is_rejected_and_balance_unchanged(ledger_store, store_open):
    acct, cat = "ZZNP1", "ZZNPC"
    with store_open(ledger_store) as db:
        db.categories.create(category=cat, description="Post Probe")
    assert cli_runner("account", "add", acct, "Post Probe")[0] == 0
    deposit = Decimal("10.00")
    code, _, err = cli_runner("txn", "post", acct, cat, str(deposit), "2099-03-01", "in")
    assert code == 0, err

    code, out, err = cli_runner("txn", "post", acct, cat, str(-(deposit + Decimal("0.01"))), "2099-03-02", "out")
    assert code == 3
    assert out == ""

    code, out, err = cli_runner("account", "get", acct)
    assert code == 0, err
    row = _rows(out)[1]
    assert row[2] == "1"
    assert Decimal(row[3]) == deposit


# ── txn amend ──────────────────────────────────────────────────────────────────────────────


def test_amend_deposit_below_outflow_is_rejected_and_original_remains(ledger_store, store_open):
    acct, cat = "ZZNA1", "ZZNAC"
    with store_open(ledger_store) as db:
        db.categories.create(category=cat, description="Amend Probe")
    assert cli_runner("account", "add", acct, "Amend Probe")[0] == 0
    big, spend = Decimal("100.00"), Decimal("60.00")
    code, out, err = cli_runner("txn", "post", acct, cat, str(big), "2099-03-01", "in")
    assert code == 0, err
    deposit_id = _rows(out)[1][0]
    assert cli_runner("txn", "post", acct, cat, str(-spend), "2099-03-02", "out")[0] == 0

    code, out, err = cli_runner("txn", "amend", deposit_id, "50.00")
    assert code == 3
    assert out == ""

    code, out, err = cli_runner("txn", "get", deposit_id)
    assert code == 0, err
    assert Decimal(_rows(out)[1][4]) == big
    code, out, err = cli_runner("account", "get", acct)
    assert code == 0, err
    assert Decimal(_rows(out)[1][3]) == big - spend


# ── txn delete ─────────────────────────────────────────────────────────────────────────────


def test_delete_deposit_that_funds_later_outflow_is_rejected_and_row_kept(ledger_store, store_open):
    acct, cat = "ZZND1", "ZZNDC"
    with store_open(ledger_store) as db:
        db.categories.create(category=cat, description="Delete Probe")
    assert cli_runner("account", "add", acct, "Delete Probe")[0] == 0
    big, spend = Decimal("100.00"), Decimal("60.00")
    code, out, err = cli_runner("txn", "post", acct, cat, str(big), "2099-03-01", "in")
    assert code == 0, err
    deposit_id = _rows(out)[1][0]
    assert cli_runner("txn", "post", acct, cat, str(-spend), "2099-03-02", "out")[0] == 0

    code, out, err = cli_runner("txn", "delete", deposit_id)
    assert code == 3
    assert out == ""

    assert cli_runner("txn", "get", deposit_id)[0] == 0
    code, out, err = cli_runner("account", "get", acct)
    assert code == 0, err
    row = _rows(out)[1]
    assert row[2] == "2"
    assert Decimal(row[3]) == big - spend


# ── transfer ───────────────────────────────────────────────────────────────────────────────


def test_transfer_beyond_source_balance_stores_neither_row(ledger_store, store_open):
    src, dst, cat = "ZZNT1", "ZZNT2", "ZZNTC"
    with store_open(ledger_store) as db:
        db.categories.create(category=cat, description="Transfer Probe")
        db.categories.create(category="TRANSFER", description="Internal transfer")
    for account in (src, dst):
        assert cli_runner("account", "add", account, "Xfer " + account)[0] == 0
    funds = Decimal("20.00")
    assert cli_runner("txn", "post", src, cat, str(funds), "2099-03-01", "in")[0] == 0
    before = _counts()["transactions"]

    code, out, err = cli_runner("transfer", src, dst, str(funds + Decimal("0.01")), "2099-03-02")
    assert code == 3
    assert out == ""
    assert _counts()["transactions"] == before

    code, out, err = cli_runner("account", "get", src)
    assert code == 0, err
    assert Decimal(_rows(out)[1][3]) == funds
    code, out, err = cli_runner("account", "get", dst)
    assert code == 0, err
    assert Decimal(_rows(out)[1][3]) == Decimal("0")
