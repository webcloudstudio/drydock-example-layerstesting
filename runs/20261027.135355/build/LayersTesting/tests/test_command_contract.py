"""Command contract across every delivered command: CSV output, exit codes, and rejected writes.

Assembly checks for FEATURE-CommandContract. Each check acts through ``cli_runner``, then reads the
output back as CSV or reads the counts through ``count``. Every test runs against a fresh store.
"""

import csv
import io
import re

import pytest

from cli.testing import cli_runner

ACCOUNT_HEADER = ["account", "name", "transactions", "balance"]
TXN_HEADER = ["txn_id", "date", "account", "category", "amount", "memo"]
AMOUNT = re.compile(r"-?\d+\.\d{2}")


def _rows(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out)))


def _clean(out: str) -> None:
    assert out.endswith("\n")
    assert "\r" not in out
    for line in out.split("\n"):
        assert line == line.rstrip(" ")


def _counts() -> dict[str, int]:
    code, out, err = cli_runner("count")
    assert code == 0, err
    return {row[0]: int(row[1]) for row in _rows(out)[1:]}


# ── usage errors: exit 2, nothing on stdout ─────────────────────────────────────────────────


@pytest.mark.parametrize(
    "args",
    [
        ("frobnicate",),
        ("report", "nosuch"),
        ("report",),
        ("load", "nosuch", "x.csv"),
        ("account",),
        ("account", "get"),
        ("txn", "post", "A"),
        ("transfer", "A", "B"),
        ("count", "extra"),
    ],
)
def test_usage_error_exits_two_with_empty_stdout(ledger_store, args):
    code, out, err = cli_runner(*args)
    assert code == 2
    assert out == ""


# ── CSV format on successful output ─────────────────────────────────────────────────────────


@pytest.fixture
def probe_category(ledger_store, store_open):
    with store_open(ledger_store) as db:
        db.categories.create(category="ZZCFC", description="Format Probe")
    return "ZZCFC"


def test_account_add_prints_clean_csv_with_account_header(ledger_store, probe_category):
    code, out, err = cli_runner("account", "add", "ZZCF1", "Format Probe")
    assert code == 0, err
    _clean(out)
    assert _rows(out)[0] == ACCOUNT_HEADER


def test_txn_post_prints_clean_csv_with_two_decimal_amount(ledger_store, probe_category):
    assert cli_runner("account", "add", "ZZCF1", "Format Probe")[0] == 0
    code, out, err = cli_runner("txn", "post", "ZZCF1", probe_category, "7.5", "2099-05-05", "fmt")
    assert code == 0, err
    _clean(out)
    table = _rows(out)
    assert table[0] == TXN_HEADER
    assert AMOUNT.fullmatch(table[1][4])
    assert table[1][4] == "7.50"


def test_count_prints_clean_csv_with_table_rows_in_declared_order(ledger_store):
    code, out, err = cli_runner("count")
    assert code == 0, err
    _clean(out)
    table = _rows(out)
    assert table[0] == ["table", "rows"]
    assert [row[0] for row in table[1:]] == ["accounts", "categories", "transactions"]


@pytest.mark.parametrize(
    "args, header",
    [
        (("report", "balances"), ACCOUNT_HEADER),
        (("report", "categories"), ["category", "description", "transactions", "inflow", "outflow", "net"]),
        (("report", "monthly"), ["month", "transactions", "inflow", "outflow", "net"]),
    ],
)
def test_report_prints_clean_csv_with_declared_header(ledger_store, args, header):
    code, out, err = cli_runner(*args)
    assert code == 0, err
    _clean(out)
    assert _rows(out)[0] == header


# ── failing commands: exit class, nothing on stdout, one diagnostic line on stderr ──────────


@pytest.mark.parametrize(
    "args, want",
    [
        (("account", "get", "ZZNOSUCH9"), 4),
        (("account", "add", "lower", "Bad Code"), 3),
        (("txn", "get", "999999999"), 4),
        (("txn", "post", "ZZNOSUCH9", "ZZNOCAT9", "1.00", "2099-01-01"), 3),
        (("load", "accounts", "/nonexistent-dir/zz-missing.csv"), 1),
    ],
)
def test_failure_exits_with_class_code_and_one_stderr_line(ledger_store, args, want):
    code, out, err = cli_runner(*args)
    assert code == want
    assert out == ""
    assert len(err.strip().splitlines()) == 1


# ── rejected writes leave every table count unchanged ───────────────────────────────────────


@pytest.fixture
def reject_store(ledger_store, store_open):
    """Two accounts with one posted transaction on the first, and a category to post against."""
    with store_open(ledger_store) as db:
        db.categories.create(category="ZZCRC", description="Reject Probe")
    for account in ("ZZCR1", "ZZCR2"):
        assert cli_runner("account", "add", account, "Reject " + account)[0] == 0
    assert cli_runner("txn", "post", "ZZCR1", "ZZCRC", "5.00", "2099-02-02", "seed")[0] == 0
    return ledger_store


@pytest.mark.parametrize(
    "args",
    [
        ("account", "add", "ZZCR1", "Duplicate"),
        ("account", "add", "bad code", "Name"),
        ("account", "delete", "ZZCR1"),
        ("txn", "post", "ZZCR1", "ZZCRC", "1.234", "2099-02-03"),
        ("txn", "post", "ZZCR1", "ZZCRC", "1.00", "2026-02-30"),
        ("txn", "post", "ZZCR1", "ZZNOCAT9", "1.00", "2099-02-03"),
        ("txn", "post", "ZZCR1", "ZZCRC", "0", "2099-02-03"),
        ("transfer", "ZZCR1", "ZZCR1", "1.00", "2099-02-03"),
        ("transfer", "ZZCR1", "ZZCR2", "0.50", "2026-02-30"),
    ],
)
def test_rejected_write_exits_three_and_leaves_counts_unchanged(reject_store, args):
    before = _counts()
    code, out, err = cli_runner(*args)
    assert code == 3
    assert out == ""
    assert _counts() == before
