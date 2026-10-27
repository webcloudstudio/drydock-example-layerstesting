"""``ledger report balances|monthly|categories`` and the report arithmetic, against a fresh store per test."""

import csv
import io

import pytest

from cli.testing import cli_runner
from ledger_core.reports import flow_cells, flows

BALANCES_HEADER = ["account", "name", "transactions", "balance"]
MONTHLY_HEADER = ["month", "transactions", "inflow", "outflow", "net"]
CATEGORIES_HEADER = ["category", "description", "transactions", "inflow", "outflow", "net"]

# (txn_id, date, account, category, cents). Hand-computed expectations are written out in the tests.
DATASET = [
    (1, "2026-01-05", "ZRB1", "ZRCA", 100050),
    (2, "2026-01-20", "ZRB1", "ZRCA", -2505),
    (3, "2026-03-02", "ZRB1", "ZRCA", -7),
    (4, "2026-03-03", "ZRB2", "ZRCB", -1000),
]


def _rows(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out)))


@pytest.fixture
def base(ledger_store, store_open):
    """Three accounts (created out of code order), three categories, and no transactions."""
    with store_open(ledger_store) as db:
        db.accounts.create(account="ZRB3", name="Idle")
        db.accounts.create(account="ZRB2", name="Bal Two")
        db.accounts.create(account="ZRB1", name="Bal One")
        db.categories.create(category="ZRCC", description="Cat C")
        db.categories.create(category="ZRCB", description="Cat B")
        db.categories.create(category="ZRCA", description="Cat A")
    return ledger_store


def _post_dataset(store_open, path, rows=DATASET):
    with store_open(path) as db:
        for txn_id, date, account, category, cents in rows:
            db.transactions.create(txn_id=txn_id, date=date, account=account, category=category,
                                   amount=cents, memo="")


# ── pure arithmetic ───────────────────────────────────────────────────────────────────────


def test_flows_of_no_amounts_are_all_zero():
    assert flows([]) == (0, 0, 0, 0)


def test_flows_separate_inflow_from_outflow_and_net_is_their_difference():
    assert flows([500, -200, -50]) == (3, 500, 250, 250)


def test_flow_cells_write_outflow_positive_and_negative_net_with_sign():
    assert flow_cells([-1007]) == ["1", "0.00", "10.07", "-10.07"]


# ── balances ──────────────────────────────────────────────────────────────────────────────


def test_balances_report_count_and_balance_per_account_with_total(base, store_open):
    _post_dataset(store_open, base)
    code, out, err = cli_runner("report", "balances")
    assert code == 0, err
    assert _rows(out) == [
        BALANCES_HEADER,
        ["ZRB1", "Bal One", "3", "975.38"],
        ["ZRB2", "Bal Two", "1", "-10.00"],
        ["ZRB3", "Idle", "0", "0.00"],
        ["TOTAL", "", "4", "965.38"],
    ]


def test_balances_list_accounts_by_code_regardless_of_creation_order(base):
    code, out, _ = cli_runner("report", "balances")
    assert code == 0
    assert [row[0] for row in _rows(out)[1:-1]] == ["ZRB1", "ZRB2", "ZRB3"]


def test_balances_account_without_transactions_is_zero(base):
    code, out, _ = cli_runner("report", "balances")
    assert code == 0
    assert _rows(out)[3] == ["ZRB3", "Idle", "0", "0.00"]


def test_balances_total_row_is_sum_of_account_rows(base, store_open):
    _post_dataset(store_open, base)
    rows = _rows(cli_runner("report", "balances")[1])
    body, total = rows[1:-1], rows[-1]
    assert int(total[2]) == sum(int(row[2]) for row in body)
    assert total[3] == "965.38"


def test_balances_empty_ledger_is_zero_total_row_only(ledger_store):
    code, out, _ = cli_runner("report", "balances")
    assert code == 0
    assert _rows(out) == [BALANCES_HEADER, ["TOTAL", "", "0", "0.00"]]


def test_balances_output_has_newline_endings_and_no_trailing_spaces(base, store_open):
    _post_dataset(store_open, base)
    code, out, _ = cli_runner("report", "balances")
    assert code == 0
    assert out.endswith("\n")
    assert "\r" not in out
    assert all(line == line.rstrip(" ") for line in out.split("\n"))


def test_balances_extra_argument_is_usage_error_with_empty_stdout(ledger_store):
    code, out, _ = cli_runner("report", "balances", "extra")
    assert code == 2
    assert out == ""


# ── monthly ───────────────────────────────────────────────────────────────────────────────


def test_monthly_groups_by_first_seven_characters_of_date(base, store_open):
    _post_dataset(store_open, base)
    code, out, err = cli_runner("report", "monthly")
    assert code == 0, err
    assert _rows(out) == [
        MONTHLY_HEADER,
        ["2026-01", "2", "1000.50", "25.05", "975.45"],
        ["2026-03", "2", "0.00", "10.07", "-10.07"],
        ["TOTAL", "4", "1000.50", "35.12", "965.38"],
    ]


def test_monthly_omits_months_without_transactions(base, store_open):
    _post_dataset(store_open, base)
    rows = _rows(cli_runner("report", "monthly")[1])
    assert "2026-02" not in [row[0] for row in rows]


def test_monthly_rows_ascend_by_month(base, store_open):
    _post_dataset(store_open, base, rows=[
        (1, "2026-05-01", "ZRB1", "ZRCA", 100),
        (2, "2026-02-01", "ZRB1", "ZRCA", 100),
    ])
    months = [row[0] for row in _rows(cli_runner("report", "monthly")[1])[1:-1]]
    assert months == ["2026-02", "2026-05"]


def test_monthly_empty_ledger_is_header_and_zero_total(ledger_store):
    code, out, _ = cli_runner("report", "monthly")
    assert code == 0
    assert _rows(out) == [MONTHLY_HEADER, ["TOTAL", "0", "0.00", "0.00", "0.00"]]


def test_monthly_reflects_a_posting_made_after_the_last_read(base, store_open):
    _post_dataset(store_open, base)
    before = {row[0] for row in _rows(cli_runner("report", "monthly")[1])[1:-1]}
    assert "2026-07" not in before
    code, _, err = cli_runner("txn", "post", "ZRB1", "ZRCA", "12.34", "2026-07-10", "m")
    assert code == 0, err
    rows = {row[0]: row for row in _rows(cli_runner("report", "monthly")[1])[1:-1]}
    assert set(rows) == before | {"2026-07"}
    assert rows["2026-07"] == ["2026-07", "1", "12.34", "0.00", "12.34"]


def test_monthly_extra_argument_is_usage_error_with_empty_stdout(ledger_store):
    code, out, _ = cli_runner("report", "monthly", "extra")
    assert code == 2
    assert out == ""


# ── categories ────────────────────────────────────────────────────────────────────────────


def test_categories_report_inflow_outflow_and_net_per_category_with_total(base, store_open):
    _post_dataset(store_open, base)
    code, out, err = cli_runner("report", "categories")
    assert code == 0, err
    assert _rows(out) == [
        CATEGORIES_HEADER,
        ["ZRCA", "Cat A", "3", "1000.50", "25.12", "975.38"],
        ["ZRCB", "Cat B", "1", "0.00", "10.00", "-10.00"],
        ["ZRCC", "Cat C", "0", "0.00", "0.00", "0.00"],
        ["TOTAL", "", "4", "1000.50", "35.12", "965.38"],
    ]


def test_categories_list_by_code_regardless_of_creation_order_with_total_last(base):
    rows = _rows(cli_runner("report", "categories")[1])
    assert [row[0] for row in rows[1:-1]] == ["ZRCA", "ZRCB", "ZRCC"]
    assert rows[-1][0] == "TOTAL"


def test_categories_empty_category_has_zero_values(base):
    rows = _rows(cli_runner("report", "categories")[1])
    assert rows[3] == ["ZRCC", "Cat C", "0", "0.00", "0.00", "0.00"]


def test_categories_net_is_inflow_minus_outflow_and_outflow_is_never_negative(base, store_open):
    _post_dataset(store_open, base)
    rows = _rows(cli_runner("report", "categories")[1])[1:]
    for row in rows:
        assert not row[4].startswith("-")
        inflow, outflow, net = (int(v.replace(".", "")) for v in row[3:6])
        assert net == inflow - outflow


def test_categories_empty_ledger_is_zero_total_row_only(base):
    code, out, _ = cli_runner("report", "categories")
    assert code == 0
    assert _rows(out) == [
        CATEGORIES_HEADER,
        ["ZRCA", "Cat A", "0", "0.00", "0.00", "0.00"],
        ["ZRCB", "Cat B", "0", "0.00", "0.00", "0.00"],
        ["ZRCC", "Cat C", "0", "0.00", "0.00", "0.00"],
        ["TOTAL", "", "0", "0.00", "0.00", "0.00"],
    ]


def test_categories_extra_argument_is_usage_error_with_empty_stdout(ledger_store):
    code, out, _ = cli_runner("report", "categories", "extra")
    assert code == 2
    assert out == ""


# ── unknown report words ──────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("args", [("report",), ("report", "nosuchreport")])
def test_unknown_or_missing_report_name_is_usage_error(ledger_store, args):
    code, out, _ = cli_runner(*args)
    assert code == 2
    assert out == ""
