from __future__ import annotations

import csv

from cli.testing import cli_runner


def test_empty_and_ordered_accounts_are_reported(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "ledger.db"))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "ZED", "Zed")[0] == 0
    assert cli_runner("account", "add", "ALPHA", "Alpha")[0] == 0
    code, output, error = cli_runner("report", "balances")
    assert code == 0 and error == ""
    rows = list(csv.reader(output.splitlines()))
    assert rows[1] == ["ALPHA", "Alpha", "0", "0.00"]
    assert rows[2] == ["ZED", "Zed", "0", "0.00"]
    assert rows[3] == ["TOTAL", "", "0", "0.00"]
