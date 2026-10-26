"""``ledger transfer``: two matching TRANSFER rows, stored together or not at all."""

from __future__ import annotations

import csv
import io

import pytest

from cli.testing import cli_runner
from cli.writes import store_transactions
from persistence import PersistenceError

HEADER = ["txn_id", "date", "account", "category", "amount", "memo"]


def _rows(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out)))


@pytest.fixture
def accounts(scratch_db):
    scratch_db.accounts.create(account="TRS", name="Source")
    scratch_db.accounts.create(account="TRD", name="Destination")
    scratch_db.categories.create(category="TRANSFER", description="Internal transfer")
    scratch_db.categories.create(category="TROPEN", description="Opening")
    return scratch_db


def _fund(db, txn_id: int, account: str, cents: int) -> None:
    db.transactions.create(
        txn_id=txn_id, date="2026-04-01", account=account, category="TROPEN", amount=cents, memo="fund"
    )


def test_valid_transfer_prints_two_rows_with_consecutive_ids_and_opposite_amounts(accounts):
    _fund(accounts, 7001, "TRS", 100000)
    code, out, _ = cli_runner("transfer", "TRS", "TRD", "250.00", "2026-04-03")
    assert code == 0
    rows = _rows(out)
    assert rows[0] == HEADER
    assert rows[1] == ["7002", "2026-04-03", "TRS", "TRANSFER", "-250.00", "transfer to TRD"]
    assert rows[2] == ["7003", "2026-04-03", "TRD", "TRANSFER", "250.00", "transfer from TRS"]
    assert accounts.transactions.get(txn_id=7002).amount == -25000
    assert accounts.transactions.get(txn_id=7003).amount == 25000


def test_transfer_conserves_cash_across_the_two_accounts(accounts):
    _fund(accounts, 7101, "TRS", 50000)
    _fund(accounts, 7102, "TRD", 1000)

    def total(code: str) -> int:
        return sum(row.amount for row in accounts.transactions.list(account=code))

    before = total("TRS") + total("TRD")
    assert cli_runner("transfer", "TRS", "TRD", "100.00", "2026-04-03")[0] == 0
    assert total("TRS") == 40000
    assert total("TRD") == 11000
    assert total("TRS") + total("TRD") == before


def test_transfer_of_exact_balance_is_allowed(accounts):
    _fund(accounts, 7201, "TRS", 1000)
    assert cli_runner("transfer", "TRS", "TRD", "10.00", "2026-04-03")[0] == 0
    assert sum(row.amount for row in accounts.transactions.list(account="TRS")) == 0


@pytest.mark.parametrize(
    "args",
    [
        ("TRS", "TRS", "10.00", "2026-04-03"),
        ("TRS", "TRD", "0", "2026-04-03"),
        ("TRS", "TRD", "0.00", "2026-04-03"),
        ("TRS", "TRD", "-5.00", "2026-04-03"),
        ("TRS", "TRNONE", "10.00", "2026-04-03"),
        ("TRNONE", "TRD", "10.00", "2026-04-03"),
        ("TRS", "TRD", "1.234", "2026-04-03"),
        ("TRS", "TRD", "10.00", "2026-02-30"),
    ],
    ids=["same-account", "zero", "zero-cents", "negative", "unknown-destination", "unknown-source",
         "three-decimals", "impossible-date"],
)
def test_invalid_transfer_exits_3_and_stores_no_rows(accounts, args):
    _fund(accounts, 7301, "TRS", 50000)
    before = len(accounts.transactions.list())
    code, out, _ = cli_runner("transfer", *args)
    assert code == 3
    assert out == ""
    assert len(accounts.transactions.list()) == before


def test_transfer_larger_than_source_balance_stores_neither_row(accounts):
    _fund(accounts, 7401, "TRS", 10000)
    before_all = len(accounts.transactions.list())
    before_dst = len(accounts.transactions.list(account="TRD"))
    code, out, _ = cli_runner("transfer", "TRS", "TRD", "100.01", "2026-04-03")
    assert code == 3
    assert out == ""
    assert len(accounts.transactions.list()) == before_all
    assert len(accounts.transactions.list(account="TRD")) == before_dst


def test_transfer_without_transfer_category_exits_3_and_stores_nothing(accounts):
    accounts.categories.delete(category="TRANSFER")
    code, out, _ = cli_runner("transfer", "TRS", "TRD", "1.00", "2026-04-03")
    assert code == 3
    assert out == ""
    assert accounts.transactions.get(txn_id=7502) is None


class _FailSecondCreate:
    """Proxies the real transactions table and fails its second create, as a store fault would."""

    def __init__(self, real):
        self._real = real
        self._creates = 0

    def create(self, **kwargs):
        self._creates += 1
        if self._creates == 2:
            raise PersistenceError("simulated second write failure")
        return self._real.create(**kwargs)

    def __getattr__(self, name):
        return getattr(self._real, name)


class _FlakyDb:
    def __init__(self, real):
        self.transactions = _FailSecondCreate(real.transactions)


def test_failure_on_second_row_removes_the_first_row(accounts):
    _fund(accounts, 7601, "TRS", 5000)
    rows = [
        {"txn_id": 7602, "date": "2026-04-03", "account": "TRS", "category": "TRANSFER",
         "amount": -1000, "memo": "transfer to TRD"},
        {"txn_id": 7603, "date": "2026-04-03", "account": "TRD", "category": "TRANSFER",
         "amount": 1000, "memo": "transfer from TRS"},
    ]
    with pytest.raises(PersistenceError):
        store_transactions(_FlakyDb(accounts), rows)
    assert accounts.transactions.get(txn_id=7602) is None
    assert accounts.transactions.get(txn_id=7603) is None
    assert accounts.transactions.get(txn_id=7601).amount == 5000


@pytest.mark.parametrize("argv", [["transfer", "A", "B", "1.00"], ["transfer", "A", "B", "1.00", "2026-04-03", "x"]])
def test_wrong_argument_count_is_a_usage_error(accounts, argv):
    before = len(accounts.transactions.list())
    code, out, _ = cli_runner(*argv)
    assert code == 2
    assert out == ""
    assert len(accounts.transactions.list()) == before
