import csv

from cli.testing import cli_runner


def _ready(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "ledger.db"))
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "A", "Account")[0] == 0
    assert cli_runner("category", "add", "C", "Category")[0] == 0


def _monthly_rows():
    code, output, stderr = cli_runner("report", "monthly")
    return code, list(csv.reader(output.splitlines())), stderr


def test_monthly_report_empty_ledger_has_header_and_total(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "ledger.db"))
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    assert cli_runner("init")[0] == 0

    code, rows, stderr = _monthly_rows()

    assert code == 0
    assert stderr == ""
    assert rows == [
        ["month", "transactions", "inflow", "outflow", "net"],
        ["TOTAL", "0", "0.00", "0.00", "0.00"],
    ]


def test_monthly_report_orders_months_and_computes_integer_cent_totals(tmp_path, monkeypatch):
    _ready(tmp_path, monkeypatch)
    assert cli_runner("txn", "post", "A", "C", "2.00", "2026-02-15", "later")[0] == 0
    assert cli_runner("txn", "post", "A", "C", "-1.25", "2026-01-15", "earlier")[0] == 0
    assert cli_runner("txn", "post", "A", "C", "3.50", "2026-01-02", "same month")[0] == 0

    code, rows, stderr = _monthly_rows()

    assert code == 0
    assert stderr == ""
    assert rows == [
        ["month", "transactions", "inflow", "outflow", "net"],
        ["2026-01", "2", "3.50", "1.25", "2.25"],
        ["2026-02", "1", "2.00", "0.00", "2.00"],
        ["TOTAL", "3", "5.50", "1.25", "4.25"],
    ]
