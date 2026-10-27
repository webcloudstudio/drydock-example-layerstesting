"""``ledger transfer``: two linked rows stored together or not at all, against a fresh store per test."""

import csv
import io

import pytest

from cli.testing import cli_runner

TXN_HEADER = ["txn_id", "date", "account", "category", "amount", "memo"]
TRANSFER = "TRANSFER"


@pytest.fixture
def transfer_store(ledger_store, store_open):
    """Two accounts, the TRANSFER category, and a funded source account."""
    with store_open(ledger_store) as db:
        db.accounts.create(account="ZTFS", name="Source Account")
        db.accounts.create(account="ZTFD", name="Dest Account")
        db.categories.create(category=TRANSFER, description="Internal transfer")
        db.transactions.create(txn_id=1, date="2026-05-01", account="ZTFS", category=TRANSFER, amount=100000, memo="funding")
    return ledger_store


def _rows(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out)))


def _all(store_open, path):
    with store_open(path) as db:
        return db.transactions.list()


def _balance(store_open, path, account):
    with store_open(path) as db:
        return sum(row.amount for row in db.transactions.list(account=account))


def test_transfer_prints_two_rows_with_consecutive_ids(transfer_store, store_open):
    code, out, err = cli_runner("transfer", "ZTFS", "ZTFD", "250.00", "2026-05-10")
    assert code == 0, err
    assert _rows(out) == [
        TXN_HEADER,
        ["2", "2026-05-10", "ZTFS", TRANSFER, "-250.00", "transfer to ZTFD"],
        ["3", "2026-05-10", "ZTFD", TRANSFER, "250.00", "transfer from ZTFS"],
    ]


def test_transfer_rows_read_back_from_the_store(transfer_store, store_open):
    cli_runner("transfer", "ZTFS", "ZTFD", "250.00", "2026-05-10")
    with store_open(transfer_store) as db:
        outgoing = db.transactions.get(txn_id=2)
        incoming = db.transactions.get(txn_id=3)
    assert outgoing.amount == -25000 and outgoing.account == "ZTFS"
    assert incoming.amount == 25000 and incoming.account == "ZTFD"
    assert outgoing.category == incoming.category == TRANSFER


def test_transfer_conserves_cash_across_the_two_accounts(transfer_store, store_open):
    before = _balance(store_open, transfer_store, "ZTFS") + _balance(store_open, transfer_store, "ZTFD")
    assert cli_runner("transfer", "ZTFS", "ZTFD", "123.45", "2026-05-11")[0] == 0
    after = _balance(store_open, transfer_store, "ZTFS") + _balance(store_open, transfer_store, "ZTFD")
    assert after == before
    assert _balance(store_open, transfer_store, "ZTFS") == 100000 - 12345
    assert _balance(store_open, transfer_store, "ZTFD") == 12345


def test_transfer_ids_follow_largest_stored_id_not_row_count(transfer_store, store_open):
    with store_open(transfer_store) as db:
        db.transactions.create(txn_id=50, date="2026-05-01", account="ZTFD", category=TRANSFER, amount=100, memo="")
    code, out, _ = cli_runner("transfer", "ZTFS", "ZTFD", "1.00", "2026-05-12")
    assert code == 0
    assert [row[0] for row in _rows(out)[1:]] == ["51", "52"]


def test_transfer_of_exact_balance_leaves_source_at_zero(transfer_store, store_open):
    code, _, err = cli_runner("transfer", "ZTFS", "ZTFD", "1000.00", "2026-05-12")
    assert code == 0, err
    assert _balance(store_open, transfer_store, "ZTFS") == 0


def test_transfer_one_cent_over_balance_exits_three_and_stores_neither_row(transfer_store, store_open):
    before = len(_all(store_open, transfer_store))
    code, out, _ = cli_runner("transfer", "ZTFS", "ZTFD", "1000.01", "2026-05-12")
    assert code == 3
    assert out == ""
    assert len(_all(store_open, transfer_store)) == before
    assert _balance(store_open, transfer_store, "ZTFD") == 0


@pytest.mark.parametrize(
    "args",
    [
        ("ZTFS", "ZTFS", "5.00", "2026-05-13"),
        ("ZTFS", "ZTFD", "0", "2026-05-13"),
        ("ZTFS", "ZTFD", "-5.00", "2026-05-13"),
        ("ZTFS", "ZTFD", "5.001", "2026-05-13"),
        ("ZTFS", "ZTFD", "5", "2026-02-30"),
        ("ZTFS", "ZTFD", "5.00", "13/05/2026"),
        ("ZTFS", "ZTFNONE", "5.00", "2026-05-13"),
        ("ZTFNONE", "ZTFD", "5.00", "2026-05-13"),
    ],
)
def test_rejected_transfer_exits_three_with_no_output_and_no_rows(transfer_store, store_open, args):
    before = len(_all(store_open, transfer_store))
    code, out, _ = cli_runner("transfer", *args)
    assert code == 3
    assert out == ""
    assert len(_all(store_open, transfer_store)) == before


def test_transfer_without_transfer_category_is_rejected(ledger_store, store_open):
    with store_open(ledger_store) as db:
        db.accounts.create(account="ZTNS", name="Source")
        db.accounts.create(account="ZTND", name="Dest")
        db.categories.create(category="ZTNC", description="Other")
        db.transactions.create(txn_id=1, date="2026-05-01", account="ZTNS", category="ZTNC", amount=900, memo="")
    code, out, _ = cli_runner("transfer", "ZTNS", "ZTND", "1.00", "2026-05-02")
    assert code == 3
    assert out == ""
    with store_open(ledger_store) as db:
        assert db.transactions.list(account="ZTND") == []


@pytest.mark.parametrize(
    "args",
    [("transfer",), ("transfer", "A", "B", "1.00"), ("transfer", "A", "B", "1.00", "2026-05-01", "extra")],
)
def test_transfer_wrong_argument_count_is_usage_error(transfer_store, args):
    code, out, _ = cli_runner(*args)
    assert code == 2
    assert out == ""
