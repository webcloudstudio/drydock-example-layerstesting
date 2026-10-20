from __future__ import annotations

import os
import subprocess


def run_ledger(database: str, *args: str) -> subprocess.CompletedProcess[str]:
    environment = {**os.environ, "DATABASE_URL": database}
    return subprocess.run(["./ledger", *args], capture_output=True, text=True, env=environment)


def write_csv(path, content: str):
    path.write_text(content, encoding="utf-8")
    return str(path)


def test_accounts_load_round_trip(tmp_path):
    database = str(tmp_path / "ledger.db")
    accounts = write_csv(tmp_path / "accounts.csv", "account,name\nA1,Main\nA2,Reserve\n")

    assert run_ledger(database, "init").returncode == 0
    loaded = run_ledger(database, "load", "accounts", accounts)
    assert loaded.returncode == 0
    assert loaded.stdout == "table,loaded\naccounts,2\n"
    counted = run_ledger(database, "count")
    assert counted.returncode == 0
    assert counted.stdout.splitlines()[1] == "accounts,2"


def test_categories_load_round_trip(tmp_path):
    database = str(tmp_path / "ledger.db")
    categories = write_csv(tmp_path / "categories.csv", "category,description\nSALES,Sales\nSUPPLY,Supplies\n")

    assert run_ledger(database, "init").returncode == 0
    loaded = run_ledger(database, "load", "categories", categories)
    assert loaded.returncode == 0
    assert loaded.stdout == "table,loaded\ncategories,2\n"
    counted = run_ledger(database, "count")
    assert counted.returncode == 0
    assert counted.stdout.splitlines()[2] == "categories,2"


def test_invalid_account_batch_rolls_back_every_row(tmp_path):
    database = str(tmp_path / "ledger.db")
    accounts = write_csv(tmp_path / "accounts.csv", "account,name\nA1,Main\nINVALID-CODE,Rejected\n")

    assert run_ledger(database, "init").returncode == 0
    rejected = run_ledger(database, "load", "accounts", accounts)
    assert rejected.returncode == 3
    assert rejected.stdout == ""
    counted = run_ledger(database, "count")
    assert counted.returncode == 0
    assert counted.stdout.splitlines()[1] == "accounts,0"


def test_load_rejects_wrong_header_duplicate_and_invalid_text(tmp_path):
    database = str(tmp_path / "ledger.db")
    assert run_ledger(database, "init").returncode == 0

    cases = [
        "account,wrong\nA1,Main\n",
        "account,name\nA1,Main\nA1,Again\n",
        "account,name\nA1,\n",
        "account,name\nA1234567890123,Too long\n",
    ]
    for index, content in enumerate(cases):
        path = write_csv(tmp_path / f"invalid-{index}.csv", content)
        rejected = run_ledger(database, "load", "accounts", path)
        assert rejected.returncode == 3
        assert rejected.stdout == ""

    counted = run_ledger(database, "count")
    assert counted.returncode == 0
    assert counted.stdout.splitlines()[1] == "accounts,0"


def test_unreadable_input_is_operational_failure(tmp_path):
    database = str(tmp_path / "ledger.db")
    assert run_ledger(database, "init").returncode == 0
    rejected = run_ledger(database, "load", "categories", str(tmp_path / "missing.csv"))
    assert rejected.returncode == 1
    assert rejected.stdout == ""
