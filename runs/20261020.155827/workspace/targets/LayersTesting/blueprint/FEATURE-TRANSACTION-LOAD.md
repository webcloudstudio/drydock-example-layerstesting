# FEATURE: Transaction CSV Loading

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Loads validated transaction CSV batches atomically into the ledger. |
| Depends On  | FEATURE-ACCOUNT-CATEGORY-LOAD.md, DATABASE.md |
| Provides    | ledger load transactions |
| Consumes    | ./ledger executable, ledger persistence operations |

## Purpose

Load transaction rows while preserving supplied identifiers and enforcing all transaction, reference, date, amount, duplicate, balance, and atomicity rules.

## Workflow

1. Validate the exact transaction header and every row.
2. Parse amounts into integer cents and validate real calendar dates.
3. Validate account and category references and duplicate identifiers.
4. Insert the complete batch in one transaction.
5. Recompute affected balances before commit.
6. Emit the loaded-row result only after commit.

## Database Interface


- None — persistence is owned by DATABASE.md, FEATURE-ACCOUNT-CATEGORY-LOAD.md, FEATURE-ACCOUNT-OPERATIONS.md, FEATURE-SCHEMA-LIFECYCLE.md, FEATURE-TRANSACTION-OPERATIONS.md.

## Programmatic Acceptance

=== AC transaction-load-success ===
Intent: A valid transaction CSV batch is persisted with supplied identifiers and cents.
import csv
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    db = Path(tmp) / "ledger.db"
    old = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = str(db)
    try:
        assert cli_runner("init")[0] == 0
        assert cli_runner("load", "accounts", "sources/seed_accounts.csv")[0] == 0
        assert cli_runner("load", "categories", "sources/seed_categories.csv")[0] == 0
        code, stdout, _ = cli_runner("load", "transactions", "sources/seed_transactions.csv")
        assert code == 0
        rows = list(csv.reader(stdout.splitlines()))
        assert rows[0] == ["table", "loaded"]
        assert rows[1][0] == "transactions"
        assert int(rows[1][1]) == 120
        code, stdout, _ = cli_runner("txn", "get", "1")
        assert code == 0
        assert next(csv.reader(stdout.splitlines()))[0] == "txn_id"
        row = next(csv.reader(stdout.splitlines()))
        assert row[0] == "1"
        assert row[4] == "5000.00"
    finally:
        if old is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = old
=== END AC transaction-load-success ===

=== AC transaction-load-atomic ===
Intent: A rejected transaction batch leaves the existing transaction count unchanged.
import csv
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    db = Path(tmp) / "ledger.db"
    old = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = str(db)
    try:
        assert cli_runner("init")[0] == 0
        assert cli_runner("load", "accounts", "sources/seed_accounts.csv")[0] == 0
        assert cli_runner("load", "categories", "sources/seed_categories.csv")[0] == 0
        assert cli_runner("load", "transactions", "sources/seed_transactions.csv")[0] == 0
        before = next(csv.reader(cli_runner("count")[1].splitlines())) 
        code, stdout, _ = cli_runner("load", "transactions", "sources/seed_transactions_bad.csv")
        assert code == 3
        assert stdout == ""
        after = list(csv.reader(cli_runner("count")[1].splitlines()))
        assert after[3][0] == "transactions"
        assert after[3][1] == "120"
    finally:
        if old is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = old
=== END AC transaction-load-atomic ===

=== AC transaction-load-validation ===
Intent: Invalid transaction rows are rejected with the rejection exit code.
from cli.testing import cli_runner

code, stdout, stderr = cli_runner("txn", "post", "DRAWER1", "SALES", "1.234", "2026-02-30")
assert code == 3
assert stdout == ""
assert stderr != ""
=== END AC transaction-load-validation ===

## User Acceptance

- None.

## Guardrails

- A rejected batch must commit no rows.
- Amounts are integer cents and never floating point.
- Application code uses only the shipped persistence library.
