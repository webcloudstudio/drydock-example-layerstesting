from __future__ import annotations

import os
import subprocess


def run_ledger(database: str, *args: str) -> subprocess.CompletedProcess[str]:
    environment = {**os.environ, "DATABASE_URL": database}
    return subprocess.run(["./ledger", *args], capture_output=True, text=True, env=environment)


def write_csv(path, content: str) -> str:
    path.write_text(content, encoding="utf-8")
    return str(path)


def prepare_ledger(tmp_path):
    database = str(tmp_path / "ledger.db")
    assert run_ledger(database, "init").returncode == 0
    assert run_ledger(database, "load", "accounts", "sources/seed_accounts.csv").returncode == 0
    assert run_ledger(database, "load", "categories", "sources/seed_categories.csv").returncode == 0
    return database


def test_transactions_load_preserves_ids_and_cents(tmp_path):
    database = prepare_ledger(tmp_path)
    loaded = run_ledger(database, "load", "transactions", "sources/seed_transactions.csv")

    assert loaded.returncode == 0
    assert loaded.stdout == "table,loaded\ntransactions,120\n"
    transaction = run_ledger(database, "txn", "get", "1")
    assert transaction.returncode == 0
    assert transaction.stdout.splitlines()[1].split(",")[0:5] == [
        "1", "2026-01-01", "SAFE", "OPENING", "5000.00"
    ]


def test_invalid_transaction_batch_is_atomic(tmp_path):
    database = prepare_ledger(tmp_path)
    assert run_ledger(database, "load", "transactions", "sources/seed_transactions.csv").returncode == 0

    rejected = run_ledger(database, "load", "transactions", "sources/seed_transactions_bad.csv")
    assert rejected.returncode == 3
    assert rejected.stdout == ""
    counted = run_ledger(database, "count")
    assert counted.returncode == 0
    assert counted.stdout.splitlines()[3] == "transactions,120"


def test_transaction_load_rejects_bad_rows_before_insertion(tmp_path):
    database = prepare_ledger(tmp_path)
    cases = [
        "txn_id,date,account,category,amount,memo\n1,2026-02-30,SAFE,OPENING,1.00,bad\n",
        "txn_id,date,account,category,amount,memo\n1,2026-02-01,NOSUCH,SALES,1.00,bad\n",
        "txn_id,date,account,category,amount,memo\n1,2026-02-01,SAFE,NOSUCH,1.00,bad\n",
        "txn_id,date,account,category,amount,memo\n1,2026-02-01,SAFE,OPENING,1.001,bad\n",
        "txn_id,date,account,category,amount,memo\n1,2026-02-01,SAFE,OPENING,1.00,bad\n1,2026-02-01,SAFE,OPENING,1.00,duplicate\n",
    ]
    for index, content in enumerate(cases):
        rejected = run_ledger(
            database,
            "load",
            "transactions",
            write_csv(tmp_path / f"invalid-{index}.csv", content),
        )
        assert rejected.returncode == 3
        assert rejected.stdout == ""

    assert run_ledger(database, "count").stdout.splitlines()[3] == "transactions,0"

