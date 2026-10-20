import csv

from cli.testing import cli_runner


def _ready(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "ledger.db"))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "A1", "Drawer")[0] == 0
    assert cli_runner("category", "add", "C1", "Sales")[0] == 0


def _get(txn_id="1"):
    code, output, _ = cli_runner("txn", "get", txn_id)
    return code, list(csv.reader(output.splitlines()))


def test_transaction_crud_preserves_fields_and_uses_integer_cents(tmp_path, monkeypatch):
    _ready(tmp_path, monkeypatch)
    assert cli_runner("txn", "post", "A1", "C1", "90071992547409.91", "2026-01-01", "sale")[0] == 0
    assert _get()[1][1] == ["1", "2026-01-01", "A1", "C1", "90071992547409.91", "sale"]
    assert cli_runner("txn", "amend", "1", "90071992547409.90")[0] == 0
    assert _get()[1][1] == ["1", "2026-01-01", "A1", "C1", "90071992547409.90", "sale"]
    assert cli_runner("txn", "delete", "1")[0] == 0
    assert _get()[0] == 4


def test_transaction_post_rejects_invalid_fields_before_writing(tmp_path, monkeypatch):
    _ready(tmp_path, monkeypatch)
    cases = [
        ("BAD-CODE", "C1", "1.00", "2026-01-01", "ok"),
        ("A1", "C1", "1.001", "2026-01-01", "ok"),
        ("A1", "C1", "1.00", "2026-02-30", "ok"),
        ("A1", "C1", "1.00", "2026-01-01", "x" * 61),
    ]
    for account, category, amount, day, memo in cases:
        assert cli_runner("txn", "post", account, category, amount, day, memo)[0] == 3
    assert _get()[0] == 4


def test_transaction_amend_and_delete_reject_negative_result_atomically(tmp_path, monkeypatch):
    _ready(tmp_path, monkeypatch)
    assert cli_runner("txn", "post", "A1", "C1", "5.00", "2026-01-01", "opening")[0] == 0
    assert cli_runner("txn", "post", "A1", "C1", "-2.00", "2026-01-02", "refund")[0] == 0
    assert cli_runner("txn", "amend", "1", "-10.00")[0] == 3
    assert _get()[1][1] == ["1", "2026-01-01", "A1", "C1", "5.00", "opening"]
    assert cli_runner("txn", "delete", "1")[0] == 3
    assert _get()[0] == 0
