"""Output contract: stdout carries only the result CSV; failures keep stdout empty.

Every test reads the result back through the command's own output (parsed with ``csv``) or through
a follow-up command, never by matching diagnostic text. Each test runs against its own store.
"""

import csv
import io

import pytest

from cli.testing import cli_runner

TXN_HEADER = ["txn_id", "date", "account", "category", "amount", "memo"]
ACCOUNT_HEADER = ["account", "name", "transactions", "balance"]


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "ledger.db"))
    assert cli_runner("init")[0] == 0
    return tmp_path


def parse(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out, newline="")))


def make_account(code: str, name: str = "Output Check") -> None:
    assert cli_runner("account", "add", code, name)[0] == 0


def make_category(tmp_path, code: str) -> None:
    path = tmp_path / f"{code}.csv"
    path.write_text(f"category,description\n{code},Desc {code}\n", encoding="utf-8")
    assert cli_runner("load", "categories", str(path))[0] == 0


def test_account_add_writes_header_and_one_unquoted_lf_row(store):
    code, out, err = cli_runner("account", "add", "OUTC1", "Output Check")
    assert code == 0
    assert err == ""
    assert "\r" not in out
    assert out.endswith("\n")
    assert '"' not in out
    assert out == "account,name,transactions,balance\nOUTC1,Output Check,0,0.00\n"


def test_fields_are_written_without_quoting_when_they_hold_no_comma(store):
    make_account("OUTQ1", "Plain Name")
    code, out, _ = cli_runner("account", "get", "OUTQ1")
    assert code == 0
    assert out == "account,name,transactions,balance\nOUTQ1,Plain Name,0,0.00\n"


def test_init_writes_nothing_to_stdout_and_is_repeatable(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "fresh.db"))
    for _ in range(2):
        code, out, err = cli_runner("init")
        assert code == 0
        assert out == ""


def test_rejected_failure_writes_nothing_to_stdout_and_one_stderr_line(store):
    make_account("OUTF1", "Failure Check")
    code, out, err = cli_runner("account", "add", "OUTF1", "Failure Check")
    assert code == 3
    assert out == ""
    assert len(err.strip().splitlines()) == 1


def test_not_found_failure_writes_nothing_to_stdout_and_one_stderr_line(store):
    code, out, err = cli_runner("account", "get", "OUTF2")
    assert code == 4
    assert out == ""
    assert len(err.strip().splitlines()) == 1


def test_usage_failure_writes_nothing_to_stdout_and_one_stderr_line(store):
    code, out, err = cli_runner("frobnicate")
    assert code == 2
    assert out == ""
    assert len(err.strip().splitlines()) == 1


def test_operational_failure_writes_nothing_to_stdout(store, tmp_path):
    code, out, err = cli_runner("load", "accounts", str(tmp_path / "absent.csv"))
    assert code == 1
    assert out == ""
    assert len(err.strip().splitlines()) == 1


def test_txn_post_prints_the_row_with_the_amount_as_two_decimals(store):
    make_account("OUTT1", "Output Txn")
    make_category(store, "OUTTC1")
    code, out, err = cli_runner("txn", "post", "OUTT1", "OUTTC1", "12.34", "2026-06-01", "output row")
    assert code == 0
    assert "\r" not in out
    rows = parse(out)
    assert rows == [TXN_HEADER, [rows[1][0], "2026-06-01", "OUTT1", "OUTTC1", "12.34", "output row"]]
    code, read_back, _ = cli_runner("txn", "get", rows[1][0])
    assert code == 0
    assert parse(read_back) == rows


def test_txn_post_renders_a_whole_amount_and_a_single_cent_with_two_decimals(store):
    make_account("OUTW1", "Whole")
    make_category(store, "OUTWC")
    code, out, _ = cli_runner("txn", "post", "OUTW1", "OUTWC", "7", "2026-06-01")
    assert code == 0
    assert parse(out)[1][4] == "7.00"
    code, out, _ = cli_runner("txn", "post", "OUTW1", "OUTWC", "0.05", "2026-06-02")
    assert code == 0
    assert parse(out)[1][4] == "0.05"


def test_negative_amount_is_rendered_with_a_leading_minus(store):
    make_account("OUTN1", "Negative")
    make_category(store, "OUTNC")
    code, _, _ = cli_runner("txn", "post", "OUTN1", "OUTNC", "-3", "2026-06-01")
    assert code == 3
    assert cli_runner("txn", "post", "OUTN1", "OUTNC", "4.50", "2026-06-01")[0] == 0
    code, out, _ = cli_runner("txn", "post", "OUTN1", "OUTNC", "-3", "2026-06-02")
    assert code == 0
    assert parse(out)[1][4] == "-3.00"
    code, out, _ = cli_runner("account", "get", "OUTN1")
    assert parse(out)[1][3] == "1.50"


def test_report_balances_has_header_one_row_per_account_and_a_total(store):
    make_account("OUTR1", "Report Check")
    code, out, err = cli_runner("report", "balances")
    assert code == 0
    assert "\r" not in out
    assert out.endswith("\n")
    rows = parse(out)
    assert rows[0] == ACCOUNT_HEADER
    assert rows[-1][0] == "TOTAL"
    mine = [row for row in rows[1:-1] if row[0] == "OUTR1"]
    assert mine == [["OUTR1", "Report Check", "0", "0.00"]]
    codes = [row[0] for row in rows[1:-1]]
    assert codes == sorted(codes)


def test_report_balances_on_an_empty_store_is_header_and_zero_total(store):
    code, out, _ = cli_runner("report", "balances")
    assert code == 0
    assert parse(out) == [ACCOUNT_HEADER, ["TOTAL", "", "0", "0.00"]]
