from __future__ import annotations

import csv

from cli.testing import cli_runner


def invoke(monkeypatch, tmp_path, *args: str):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "ledger.db"))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    return cli_runner(*args)


def test_post_get_amend_delete_round_trip(monkeypatch, tmp_path) -> None:
    assert invoke(monkeypatch, tmp_path, "init")[0] == 0
    assert invoke(monkeypatch, tmp_path, "account", "add", "CASH", "Cash")[0] == 0
    assert invoke(monkeypatch, tmp_path, "load", "categories", "sources/seed_categories.csv")[0] == 0

    code, output, error = invoke(monkeypatch, tmp_path, "txn", "post", "CASH", "SALES", "12.34", "2026-01-02", "sale")
    assert code == 0 and error == ""
    assert list(csv.reader(output.splitlines()))[1] == ["1", "2026-01-02", "CASH", "SALES", "12.34", "sale"]

    code, output, _ = invoke(monkeypatch, tmp_path, "txn", "amend", "1", "10.00")
    assert code == 0
    assert list(csv.reader(output.splitlines()))[1][4] == "10.00"
    assert invoke(monkeypatch, tmp_path, "txn", "delete", "1")[0] == 0
    assert invoke(monkeypatch, tmp_path, "txn", "get", "1")[0] == 4


def test_invalid_post_does_not_write(monkeypatch, tmp_path) -> None:
    assert invoke(monkeypatch, tmp_path, "init")[0] == 0
    assert invoke(monkeypatch, tmp_path, "account", "add", "CASH", "Cash")[0] == 0
    code, output, _ = invoke(monkeypatch, tmp_path, "txn", "post", "CASH", "SALES", "1.234", "2026-01-01")
    assert (code, output) == (3, "")
    code, output, _ = invoke(monkeypatch, tmp_path, "count")
    assert code == 0
    assert list(csv.reader(output.splitlines()))[-1] == ["transactions", "0"]


def test_negative_post_is_rejected_without_changing_balance(monkeypatch, tmp_path) -> None:
    assert invoke(monkeypatch, tmp_path, "init")[0] == 0
    assert invoke(monkeypatch, tmp_path, "account", "add", "CASH", "Cash")[0] == 0
    assert invoke(monkeypatch, tmp_path, "load", "categories", "sources/seed_categories.csv")[0] == 0
    assert invoke(monkeypatch, tmp_path, "txn", "post", "CASH", "SALES", "5.00", "2026-01-01")[0] == 0

    code, output, _ = invoke(
        monkeypatch, tmp_path, "txn", "post", "CASH", "SALES", "-6.00", "2026-01-02"
    )
    assert (code, output) == (3, "")

    code, output, _ = invoke(monkeypatch, tmp_path, "report", "balances")
    assert code == 0
    rows = list(csv.DictReader(output.splitlines()))
    assert rows[0]["transactions"] == "1"
    assert rows[0]["balance"] == "5.00"
