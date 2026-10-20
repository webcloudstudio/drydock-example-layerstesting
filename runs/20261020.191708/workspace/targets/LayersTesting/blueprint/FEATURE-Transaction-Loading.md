# FEATURE: Transaction Loading

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Atomically validate and load transaction CSV files. |
| Depends On  | FEATURE-Account-Category-Loading.md, FEATURE-Database-Configuration.md |
| Provides    | load transactions |
| Consumes    | command dispatch, database configuration, transactions.create, accounts.get, categories.get |

## Purpose

`ledger load transactions <csv>` validates every transaction before writing any row, including headers, fields, references, duplicate identifiers, dates, amounts, and prospective account balances.

## Workflow

The complete file is parsed into integer-cent transactions, validated against existing accounts and categories and against duplicate IDs, then checked for non-negative balances. Only a fully valid batch is inserted in one transaction.

## Database Interface


- `FEATURE-DB-004` — read-write: transactions.create - supplies: `txn_id`, `date`, `account`, `category`, `amount`, `memo` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC transaction-load-roundtrip ===
Intent: A valid transaction file persists integer-cent data and remains readable.
import csv
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    os.environ["DATABASE_PATH"] = str(Path(d) / "ledger.db")
    assert cli_runner("init")[0] == 0
    accounts = Path(d) / "accounts.csv"
    categories = Path(d) / "categories.csv"
    txns = Path(d) / "txns.csv"
    accounts.write_text("account,name\nA1,Drawer\n")
    categories.write_text("category,description\nC1,Sales\n")
    txns.write_text("txn_id,date,account,category,amount,memo\n1,2026-01-01,A1,C1,12.34,sale\n")
    assert cli_runner("load", "accounts", str(accounts))[0] == 0
    assert cli_runner("load", "categories", str(categories))[0] == 0
    assert cli_runner("load", "transactions", str(txns))[0] == 0
    code, out, _ = cli_runner("txn", "get", "1")
    assert code == 0
    row = list(csv.reader(out.splitlines()))[1]
    assert row[0:4] == ["1", "2026-01-01", "A1", "C1"]
    assert row[4] == "12.34"
=== END AC transaction-load-roundtrip ===

=== AC transaction-load-atomic-rejection ===
Intent: A later invalid reference rejects the entire transaction batch.
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    os.environ["DATABASE_PATH"] = str(Path(d) / "ledger.db")
    assert cli_runner("init")[0] == 0
    accounts = Path(d) / "accounts.csv"
    categories = Path(d) / "categories.csv"
    bad = Path(d) / "bad.csv"
    accounts.write_text("account,name\nA1,Drawer\n")
    categories.write_text("category,description\nC1,Sales\n")
    bad.write_text("txn_id,date,account,category,amount,memo\n1,2026-01-01,A1,C1,1.00,ok\n2,2026-01-01,NOPE,C1,1.00,bad\n")
    assert cli_runner("load", "accounts", str(accounts))[0] == 0
    assert cli_runner("load", "categories", str(categories))[0] == 0
    assert cli_runner("load", "transactions", str(bad))[0] == 3
    assert cli_runner("txn", "get", "1")[0] == 4
=== END AC transaction-load-atomic-rejection ===

=== AC transaction-load-validation ===
Intent: Invalid dates, amounts, duplicate IDs, and negative prospective balances are rejected.
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    os.environ["DATABASE_PATH"] = str(Path(d) / "ledger.db")
    assert cli_runner("init")[0] == 0
    a = Path(d) / "a.csv"
    c = Path(d) / "c.csv"
    a.write_text("account,name\nA1,Drawer\n")
    c.write_text("category,description\nC1,Sales\n")
    assert cli_runner("load", "accounts", str(a))[0] == 0
    assert cli_runner("load", "categories", str(c))[0] == 0
    for name, body in {
        "date.csv": "txn_id,date,account,category,amount,memo\n1,2026-02-30,A1,C1,1.00,x\n",
        "amount.csv": "txn_id,date,account,category,amount,memo\n1,2026-01-01,A1,C1,1.234,x\n",
        "duplicate.csv": "txn_id,date,account,category,amount,memo\n1,2026-01-01,A1,C1,1.00,x\n1,2026-01-01,A1,C1,1.00,y\n",
        "balance.csv": "txn_id,date,account,category,amount,memo\n1,2026-01-01,A1,C1,-1.00,x\n",
    }.items():
        path = Path(d) / name
        path.write_text(body)
        assert cli_runner("load", "transactions", str(path))[0] == 3
=== END AC transaction-load-validation ===

## User Acceptance

- None.

## Guardrails

- All rows are validated before the first write.
- Amounts are integer cents and never floating point.
- A rejected batch leaves every table unchanged.
