import csv

from cli.testing import cli_runner


def _database(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "ledger.db"))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert cli_runner("init")[0] == 0


def test_account_crud_reports_balance_and_persists_rename(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)

    assert cli_runner("account", "add", "A1", "Drawer")[0] == 0
    code, output, _ = cli_runner("account", "get", "A1")
    assert code == 0
    assert list(csv.reader(output.splitlines()))[1] == ["A1", "Drawer", "0", "0.00"]
    assert cli_runner("account", "rename", "A1", "Front")[0] == 0
    assert list(csv.reader(cli_runner("account", "get", "A1")[1].splitlines()))[1][1] == "Front"
    assert cli_runner("account", "delete", "A1")[0] == 0
    assert cli_runner("account", "get", "A1")[0] == 4


def test_account_rejects_duplicate_missing_and_invalid_names(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)
    assert cli_runner("account", "add", "A1", "Drawer")[0] == 0
    assert cli_runner("account", "add", "A1", "Again")[0] == 3
    assert cli_runner("account", "add", "A2", "")[0] == 3
    assert cli_runner("account", "rename", "NOPE", "Name")[0] == 4
    assert cli_runner("account", "rename", "A1", "x" * 41)[0] == 3
    assert cli_runner("account", "delete", "NOPE")[0] == 4


def test_account_in_use_cannot_be_deleted(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)
    assert cli_runner("account", "add", "A1", "Drawer")[0] == 0
    assert cli_runner("account", "add", "A2", "Other")[0] == 0
    assert cli_runner("category", "add", "C1", "Sales")[0] == 0
    assert cli_runner("txn", "post", "A1", "C1", "1.00", "2026-01-01")[0] == 0
    assert cli_runner("account", "delete", "A1")[0] == 3
    assert cli_runner("account", "get", "A1")[0] == 0
