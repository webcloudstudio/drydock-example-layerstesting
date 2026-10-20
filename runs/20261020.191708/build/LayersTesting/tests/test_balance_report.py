import csv

from cli.testing import cli_runner


def _database(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "ledger.db"))
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    assert cli_runner("init")[0] == 0


def _report_rows():
    code, output, stderr = cli_runner("report", "balances")
    return code, list(csv.reader(output.splitlines())), stderr


def test_balances_report_empty_ledger_has_header_and_zero_total(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)

    code, rows, stderr = _report_rows()

    assert code == 0
    assert stderr == ""
    assert rows == [
        ["account", "name", "transactions", "balance"],
        ["TOTAL", "", "0", "0.00"],
    ]


def test_balances_report_orders_accounts_and_computes_persisted_totals(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)
    assert cli_runner("account", "add", "B", "Second")[0] == 0
    assert cli_runner("account", "add", "A", "First")[0] == 0
    assert cli_runner("category", "add", "C", "Category")[0] == 0
    assert cli_runner("txn", "post", "A", "C", "12.50", "2026-01-01")[0] == 0
    assert cli_runner("txn", "post", "B", "C", "3.25", "2026-01-02")[0] == 0

    code, rows, stderr = _report_rows()

    assert code == 0
    assert stderr == ""
    assert rows == [
        ["account", "name", "transactions", "balance"],
        ["A", "First", "1", "12.50"],
        ["B", "Second", "1", "3.25"],
        ["TOTAL", "", "2", "15.75"],
    ]


def test_balances_report_unavailable_database_is_operational_failure(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "missing" / "ledger.db"))
    monkeypatch.delenv("DATABASE_PATH", raising=False)

    code, output, stderr = cli_runner("report", "balances")

    assert code == 1
    assert output == ""
    assert stderr != ""
