"""``ledger report monthly|balances|categories``: every row recomputed from stored rows."""

from __future__ import annotations

import csv
import io
import re
from decimal import Decimal

import pytest

from cli.testing import cli_runner


def _rows(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out)))


def _cents(text: str) -> int:
    assert re.fullmatch(r"-?\d+\.\d{2}", text), text
    return int(Decimal(text) * 100)


@pytest.fixture
def ledger(scratch_db):
    scratch_db.accounts.create(account="RPA", name="Report A")
    scratch_db.accounts.create(account="RPB", name="Report B")
    scratch_db.accounts.create(account="RPE", name="Never Used")
    scratch_db.categories.create(category="RPC1", description="Used")
    scratch_db.categories.create(category="RPC2", description="Unused")
    scratch_db.categories.create(category="RPC0", description="First by code")
    return scratch_db


def _store(db, txn_id: int, date: str, account: str, category: str, cents: int) -> None:
    db.transactions.create(
        txn_id=txn_id, date=date, account=account, category=category, amount=cents, memo=""
    )


# report monthly


def test_monthly_rows_are_per_month_in_ascending_order_with_total_last(ledger):
    _store(ledger, 8001, "2098-06-10", "RPA", "RPC1", 4001)
    _store(ledger, 8002, "2098-05-10", "RPA", "RPC1", 10000)
    _store(ledger, 8003, "2098-05-11", "RPA", "RPC1", -2550)
    code, out, _ = cli_runner("report", "monthly")
    assert code == 0
    rows = _rows(out)
    assert rows[0] == ["month", "transactions", "inflow", "outflow", "net"]
    assert rows[1] == ["2098-05", "2", "100.00", "25.50", "74.50"]
    assert rows[2] == ["2098-06", "1", "40.01", "0.00", "40.01"]
    assert rows[3] == ["TOTAL", "3", "140.01", "25.50", "114.51"]


def test_monthly_total_equals_sum_of_month_rows(ledger):
    _store(ledger, 8011, "2098-07-01", "RPA", "RPC1", 12345)
    _store(ledger, 8012, "2098-08-01", "RPA", "RPC1", -345)
    rows = _rows(cli_runner("report", "monthly")[1])
    body, total = rows[1:-1], rows[-1]
    assert int(total[1]) == sum(int(r[1]) for r in body)
    for col in (2, 3, 4):
        assert _cents(total[col]) == sum(_cents(r[col]) for r in body)


def test_monthly_total_count_equals_stored_transaction_count(ledger):
    code, out, _ = cli_runner("report", "monthly")
    assert code == 0
    assert _rows(out)[-1][:2] == ["TOTAL", str(len(ledger.transactions.list()))]


def test_monthly_with_no_transactions_has_only_header_and_zero_total(ledger):
    code, out, _ = cli_runner("report", "monthly")
    assert code == 0
    assert _rows(out) == [["month", "transactions", "inflow", "outflow", "net"], ["TOTAL", "0", "0.00", "0.00", "0.00"]]


@pytest.mark.parametrize("argv", [["report", "monthly", "extra"], ["report", "nosuchreport"], ["report"]])
def test_monthly_usage_errors_exit_2_with_no_stdout(ledger, argv):
    code, out, _ = cli_runner(*argv)
    assert code == 2
    assert out == ""


# report balances


def test_balances_list_every_account_by_code_with_count_and_balance(ledger):
    _store(ledger, 8101, "2098-05-01", "RPA", "RPC1", 100000)
    _store(ledger, 8102, "2098-05-01", "RPA", "RPC1", -30050)
    _store(ledger, 8103, "2098-05-01", "RPB", "RPC1", 1999)
    code, out, _ = cli_runner("report", "balances")
    assert code == 0
    rows = _rows(out)
    assert rows[0] == ["account", "name", "transactions", "balance"]
    assert rows[1:-1] == [
        ["RPA", "Report A", "2", "699.50"],
        ["RPB", "Report B", "1", "19.99"],
        ["RPE", "Never Used", "0", "0.00"],
    ]


def test_balances_total_row_sums_counts_and_balances(ledger):
    _store(ledger, 8111, "2098-05-01", "RPA", "RPC1", 2500)
    _store(ledger, 8112, "2098-05-01", "RPB", "RPC1", 700)
    rows = _rows(cli_runner("report", "balances")[1])
    total = rows[-1]
    assert total[:3] == ["TOTAL", "", "2"]
    assert _cents(total[3]) == 3200


def test_balances_change_by_exactly_the_amount_of_a_later_transaction(ledger):
    _store(ledger, 8121, "2098-05-01", "RPA", "RPC1", 8000)
    before = _rows(cli_runner("report", "balances")[1])[1]
    _store(ledger, 8122, "2098-05-02", "RPA", "RPC1", 1234)
    after = _rows(cli_runner("report", "balances")[1])[1]
    assert _cents(after[3]) == _cents(before[3]) + 1234
    assert int(after[2]) == int(before[2]) + 1


@pytest.mark.parametrize("argv", [["report", "balances", "extra"], ["report"], ["report", "nosuchreport"]])
def test_balances_usage_errors_exit_2_with_no_stdout(ledger, argv):
    code, out, _ = cli_runner(*argv)
    assert code == 2
    assert out == ""


# report categories


def test_categories_compute_count_inflow_outflow_and_net_and_keep_empty_ones(ledger):
    amounts = [50000, 1999, -1250, -75]
    for offset, cents in enumerate(amounts):
        _store(ledger, 8201 + offset, "2098-05-01", "RPA", "RPC1", cents)
    code, out, _ = cli_runner("report", "categories")
    assert code == 0
    rows = _rows(out)
    assert rows[0] == ["category", "description", "transactions", "inflow", "outflow", "net"]
    assert rows[1] == ["RPC0", "First by code", "0", "0.00", "0.00", "0.00"]
    assert rows[2] == ["RPC1", "Used", "4", "519.99", "13.25", "506.74"]
    assert rows[3] == ["RPC2", "Unused", "0", "0.00", "0.00", "0.00"]


def test_categories_order_by_code_and_total_equals_the_rows(ledger):
    _store(ledger, 8301, "2098-05-01", "RPA", "RPC1", 900)
    _store(ledger, 8302, "2098-05-02", "RPA", "RPC0", -300)
    rows = _rows(cli_runner("report", "categories")[1])
    data, total = rows[1:-1], rows[-1]
    codes = [r[0] for r in data]
    assert codes == sorted(codes)
    assert total[0] == "TOTAL" and total[1] == ""
    assert int(total[2]) == len(ledger.transactions.list()) == sum(int(r[2]) for r in data)
    assert _cents(total[3]) == sum(_cents(r[3]) for r in data)
    assert _cents(total[4]) == sum(_cents(r[4]) for r in data)
    assert _cents(total[5]) == _cents(total[3]) - _cents(total[4])


def test_categories_outflow_rises_and_net_falls_after_a_spend(ledger):
    _store(ledger, 8401, "2098-05-01", "RPA", "RPC1", 7000)
    before = {r[0]: r for r in _rows(cli_runner("report", "categories")[1])[1:]}["RPC1"]
    assert _cents(before[4]) == 0
    _store(ledger, 8402, "2098-05-02", "RPA", "RPC1", -2345)
    after = {r[0]: r for r in _rows(cli_runner("report", "categories")[1])[1:]}["RPC1"]
    assert int(after[2]) == int(before[2]) + 1
    assert _cents(after[4]) == 2345
    assert _cents(after[5]) == 7000 - 2345


@pytest.mark.parametrize("argv", [["report", "categories", "extra"], ["report"]])
def test_categories_usage_errors_exit_2_with_no_stdout(ledger, argv):
    code, out, _ = cli_runner(*argv)
    assert code == 2
    assert out == ""
