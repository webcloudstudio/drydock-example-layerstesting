import csv

from cli.testing import cli_runner


def _database(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "ledger.db"))
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    assert cli_runner("init")[0] == 0


def _report_rows():
    code, output, stderr = cli_runner("report", "categories")
    return code, list(csv.reader(output.splitlines())), stderr


def test_category_report_includes_zero_activity_categories_in_code_order(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)
    assert cli_runner("category", "add", "Z", "Last")[0] == 0
    assert cli_runner("category", "add", "A", "First")[0] == 0
    assert cli_runner("account", "add", "CASH", "Cash")[0] == 0
    assert cli_runner("txn", "post", "CASH", "Z", "5.00", "2026-01-01", "sale")[0] == 0

    code, rows, stderr = _report_rows()

    assert code == 0
    assert stderr == ""
    assert [row[0] for row in rows[1:-1]] == ["A", "Z"]
    assert rows[1] == ["A", "First", "0", "0.00", "0.00", "0.00"]


def test_category_report_calculates_inflow_outflow_and_net_from_transactions(
    tmp_path, monkeypatch
):
    _database(tmp_path, monkeypatch)
    assert cli_runner("account", "add", "CASH", "Cash")[0] == 0
    assert cli_runner("category", "add", "SALES", "Sales")[0] == 0
    assert cli_runner("category", "add", "FEES", "Fees")[0] == 0
    assert cli_runner("txn", "post", "CASH", "SALES", "10.00", "2026-01-01", "sale")[0] == 0
    assert cli_runner("txn", "post", "CASH", "SALES", "-3.25", "2026-01-02", "fee")[0] == 0

    code, rows, stderr = _report_rows()

    assert code == 0
    assert stderr == ""
    assert rows[1] == ["FEES", "Fees", "0", "0.00", "0.00", "0.00"]
    assert rows[2] == ["SALES", "Sales", "2", "10.00", "3.25", "6.75"]
    assert rows[-1] == ["TOTAL", "", "2", "10.00", "3.25", "6.75"]


def test_category_report_empty_ledger_has_zero_total(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)

    code, rows, stderr = _report_rows()

    assert code == 0
    assert stderr == ""
    assert rows == [["category", "description", "transactions", "inflow", "outflow", "net"],
                    ["TOTAL", "", "0", "0.00", "0.00", "0.00"]]
