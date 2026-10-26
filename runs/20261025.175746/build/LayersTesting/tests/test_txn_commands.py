"""``ledger txn get|post|amend|delete``: each command's effect is read back from the store."""

from __future__ import annotations

import csv
import io

import pytest

from cli.testing import cli_runner

HEADER = ["txn_id", "date", "account", "category", "amount", "memo"]


def _rows(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out)))


@pytest.fixture
def ledger(scratch_db):
    """One account and one category, both criterion-owned, in the scratch store."""
    scratch_db.accounts.create(account="TXA", name="Txn Account")
    scratch_db.categories.create(category="TXC", description="Txn Category")
    return scratch_db


def _store(db, txn_id: int, cents: int, account: str = "TXA", memo: str = "m") -> None:
    db.transactions.create(
        txn_id=txn_id, date="2026-04-01", account=account, category="TXC", amount=cents, memo=memo
    )


# txn get


def test_get_prints_header_and_the_stored_row(ledger):
    _store(ledger, 3001, 1234, memo="get probe")
    code, out, _ = cli_runner("txn", "get", "3001")
    assert code == 0
    assert _rows(out) == [HEADER, ["3001", "2026-04-01", "TXA", "TXC", "12.34", "get probe"]]


def test_get_formats_negative_amount_with_two_decimals(ledger):
    _store(ledger, 3002, -1250)
    code, out, _ = cli_runner("txn", "get", "3002")
    assert code == 0
    assert _rows(out)[1][4] == "-12.50"


def test_get_formats_amount_under_one_unit_with_two_decimals(ledger):
    _store(ledger, 3003, 5)
    assert _rows(cli_runner("txn", "get", "3003")[1])[1][4] == "0.05"


def test_get_absent_id_exits_4_with_no_stdout(ledger):
    code, out, _ = cli_runner("txn", "get", "3999")
    assert code == 4
    assert out == ""


@pytest.mark.parametrize("argv", [["txn", "get", "abc"], ["txn", "get", "1.5"]])
def test_get_non_integer_id_exits_3(ledger, argv):
    code, out, _ = cli_runner(*argv)
    assert code == 3
    assert out == ""


@pytest.mark.parametrize("argv", [["txn", "get"], ["txn", "get", "1", "2"]])
def test_get_wrong_argument_count_is_a_usage_error(ledger, argv):
    code, out, _ = cli_runner(*argv)
    assert code == 2
    assert out == ""


# txn post


def test_post_stores_row_with_next_id_and_prints_it(ledger):
    _store(ledger, 4000, 100)
    code, out, _ = cli_runner("txn", "post", "TXA", "TXC", "45.50", "2026-04-02", "walk in")
    assert code == 0
    assert _rows(out) == [HEADER, ["4001", "2026-04-02", "TXA", "TXC", "45.50", "walk in"]]
    stored = ledger.transactions.get(txn_id=4001)
    assert stored.amount == 4550
    assert isinstance(stored.amount, int)


def test_post_into_empty_store_assigns_id_one(ledger):
    code, out, _ = cli_runner("txn", "post", "TXA", "TXC", "1.00", "2026-04-02")
    assert code == 0
    assert _rows(out)[1][0] == "1"


def test_post_without_memo_stores_empty_memo(ledger):
    code, out, _ = cli_runner("txn", "post", "TXA", "TXC", "10.00", "2026-04-02")
    assert code == 0
    row = _rows(out)[1]
    assert len(row) == 6
    assert ledger.transactions.get(txn_id=int(row[0])).memo == ""


@pytest.mark.parametrize(
    "args",
    [
        ("TXNONE", "TXC", "1.00", "2026-04-01"),
        ("TXA", "TXNONE", "1.00", "2026-04-01"),
        ("TXA", "TXC", "1.234", "2026-04-01"),
        ("TXA", "TXC", "0", "2026-04-01"),
        ("TXA", "TXC", "1.00", "2026-02-30"),
        ("TXA", "TXC", "1.00", "not-a-date"),
        ("lower", "TXC", "1.00", "2026-04-01"),
        ("TXA", "TXC", "1.00", "2026-04-01", "bad,memo"),
    ],
)
def test_post_invalid_input_exits_3_and_stores_nothing(ledger, args):
    before = len(ledger.transactions.list())
    code, out, _ = cli_runner("txn", "post", *args)
    assert code == 3
    assert out == ""
    assert len(ledger.transactions.list()) == before


def test_post_payment_beyond_balance_exits_3_and_within_balance_succeeds(ledger):
    _store(ledger, 4100, 1000)
    code, out, _ = cli_runner("txn", "post", "TXA", "TXC", "-10.01", "2026-04-02")
    assert code == 3
    assert out == ""
    assert len(ledger.transactions.list(account="TXA")) == 1
    code, _, _ = cli_runner("txn", "post", "TXA", "TXC", "-5.00", "2026-04-02")
    assert code == 0
    assert sum(row.amount for row in ledger.transactions.list(account="TXA")) == 500


def test_post_exact_balance_is_allowed(ledger):
    _store(ledger, 4200, 1000)
    code, _, _ = cli_runner("txn", "post", "TXA", "TXC", "-10.00", "2026-04-02")
    assert code == 0
    assert sum(row.amount for row in ledger.transactions.list(account="TXA")) == 0


@pytest.mark.parametrize("argv", [["txn", "post", "A", "B", "1.00"], ["txn", "post", "A", "B", "1.00", "2026-04-01", "m", "x"]])
def test_post_wrong_argument_count_is_a_usage_error(ledger, argv):
    before = len(ledger.transactions.list())
    code, out, _ = cli_runner(*argv)
    assert code == 2
    assert out == ""
    assert len(ledger.transactions.list()) == before


# txn amend


def test_amend_changes_only_the_amount(ledger):
    _store(ledger, 5001, 5000, memo="keep me")
    code, out, _ = cli_runner("txn", "amend", "5001", "60.00")
    assert code == 0
    assert _rows(out)[1] == ["5001", "2026-04-01", "TXA", "TXC", "60.00", "keep me"]
    stored = ledger.transactions.get(txn_id=5001)
    assert stored.amount == 6000
    assert stored.date == "2026-04-01"
    assert stored.memo == "keep me"


def test_amend_absent_id_exits_4(ledger):
    code, out, _ = cli_runner("txn", "amend", "5999", "1.00")
    assert code == 4
    assert out == ""


@pytest.mark.parametrize("amount_text", ["0", "1.234", "abc"])
def test_amend_invalid_amount_exits_3_and_keeps_the_amount(ledger, amount_text):
    _store(ledger, 5002, 2500)
    code, out, _ = cli_runner("txn", "amend", "5002", amount_text)
    assert code == 3
    assert out == ""
    assert ledger.transactions.get(txn_id=5002).amount == 2500


def test_amend_that_overdraws_exits_3_and_keeps_the_amount(ledger):
    _store(ledger, 5003, 1000)
    _store(ledger, 5004, -500)
    code, out, _ = cli_runner("txn", "amend", "5003", "0.10")
    assert code == 3
    assert out == ""
    assert ledger.transactions.get(txn_id=5003).amount == 1000
    assert ledger.transactions.get(txn_id=5004).amount == -500


def test_amend_within_balance_is_allowed_when_deposit_is_reduced(ledger):
    _store(ledger, 5005, 1000)
    _store(ledger, 5006, -500)
    code, _, _ = cli_runner("txn", "amend", "5005", "5.00")
    assert code == 0
    assert ledger.transactions.get(txn_id=5005).amount == 500


@pytest.mark.parametrize("argv", [["txn", "amend", "1"], ["txn", "amend", "1", "2.00", "extra"]])
def test_amend_wrong_argument_count_is_a_usage_error(ledger, argv):
    code, out, _ = cli_runner(*argv)
    assert code == 2
    assert out == ""


# txn delete


def test_delete_removes_row_and_prints_deleted_and_id(ledger):
    _store(ledger, 6001, 4550)
    code, out, _ = cli_runner("txn", "delete", "6001")
    assert code == 0
    assert _rows(out) == [["deleted"], ["6001"]]
    assert ledger.transactions.get(txn_id=6001) is None


def test_delete_deposit_that_later_payment_depends_on_exits_3(ledger):
    _store(ledger, 6002, 1000)
    _store(ledger, 6003, -500)
    code, out, _ = cli_runner("txn", "delete", "6002")
    assert code == 3
    assert out == ""
    assert ledger.transactions.get(txn_id=6002) is not None
    assert ledger.transactions.get(txn_id=6003) is not None
    assert cli_runner("txn", "delete", "6003")[0] == 0


def test_delete_absent_id_exits_4_and_removes_nothing(ledger):
    _store(ledger, 6004, 100)
    before = len(ledger.transactions.list())
    code, out, _ = cli_runner("txn", "delete", "6999")
    assert code == 4
    assert out == ""
    assert len(ledger.transactions.list()) == before


def test_delete_non_integer_id_exits_3(ledger):
    code, out, _ = cli_runner("txn", "delete", "abc")
    assert code == 3
    assert out == ""


@pytest.mark.parametrize("argv", [["txn", "delete"], ["txn", "delete", "1", "2"]])
def test_delete_wrong_argument_count_is_a_usage_error(ledger, argv):
    code, out, _ = cli_runner(*argv)
    assert code == 2
    assert out == ""
