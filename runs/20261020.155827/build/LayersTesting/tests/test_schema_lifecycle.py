from __future__ import annotations

import os
import subprocess


def run_ledger(database: str, *args: str) -> subprocess.CompletedProcess[str]:
    environment = {**os.environ, "DATABASE_URL": database}
    return subprocess.run(["./ledger", *args], capture_output=True, text=True, env=environment)


def test_init_creates_empty_schema_without_output(tmp_path):
    database = str(tmp_path / "ledger.db")

    initialized = run_ledger(database, "init")
    assert initialized.returncode == 0
    assert initialized.stdout == ""

    counted = run_ledger(database, "count")
    assert counted.returncode == 0
    assert counted.stdout.splitlines() == [
        "table,rows",
        "accounts,0",
        "categories,0",
        "transactions,0",
    ]


def test_count_reports_fixed_table_order(tmp_path):
    database = str(tmp_path / "ledger.db")

    assert run_ledger(database, "init").returncode == 0
    counted = run_ledger(database, "count")

    assert counted.returncode == 0
    assert [line.split(",", 1)[0] for line in counted.stdout.splitlines()[1:]] == [
        "accounts",
        "categories",
        "transactions",
    ]


def test_init_removes_rows_from_all_tables(tmp_path):
    database = str(tmp_path / "ledger.db")

    assert run_ledger(database, "init").returncode == 0
    assert run_ledger(database, "account", "add", "TEMP", "Temporary").returncode == 0
    assert run_ledger(database, "init").returncode == 0

    counted = run_ledger(database, "count")
    assert counted.returncode == 0
    assert counted.stdout.splitlines()[1:] == [
        "accounts,0",
        "categories,0",
        "transactions,0",
    ]
