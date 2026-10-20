import csv

from cli.testing import cli_runner


def _ready(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "ledger.db"))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "A1", "Drawer")[0] == 0
    assert cli_runner("category", "add", "C1", "Sales")[0] == 0


def _transaction(transaction_id="1"):
    code, output, _ = cli_runner("txn", "get", transaction_id)
    return code, list(csv.reader(output.splitlines()))


def test_negative_posting_is_rejected_before_creation(tmp_path, monkeypatch):
    _ready(tmp_path, monkeypatch)

    assert cli_runner("txn", "post", "A1", "C1", "-1.00", "2026-01-01")[0] == 3
    assert _transaction()[0] == 4


def test_negative_amendment_preserves_original_transaction(tmp_path, monkeypatch):
    _ready(tmp_path, monkeypatch)
    assert cli_runner("txn", "post", "A1", "C1", "5.00", "2026-01-01")[0] == 0

    assert cli_runner("txn", "amend", "1", "-6.00")[0] == 3
    assert _transaction()[1][1][4] == "5.00"


def test_negative_delete_preserves_positive_transaction(tmp_path, monkeypatch):
    _ready(tmp_path, monkeypatch)
    assert cli_runner("txn", "post", "A1", "C1", "5.00", "2026-01-01")[0] == 0

    assert cli_runner("txn", "delete", "1")[0] == 3
    assert _transaction()[0] == 0
