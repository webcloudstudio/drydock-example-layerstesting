# FEATURE: Transfers

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Executes atomic two-entry transfers between distinct ledger accounts. |
| Depends On  | FEATURE-TRANSACTION-OPERATIONS.md, DATABASE.md |
| Provides    | ledger transfer |
| Consumes    | ./ledger executable, ledger persistence operations |

## Purpose

Move a positive amount between two distinct accounts by creating consecutive outgoing and incoming transaction rows in one database transaction.

## Database Interface


- None — persistence is owned by DATABASE.md, FEATURE-ACCOUNT-CATEGORY-LOAD.md, FEATURE-ACCOUNT-OPERATIONS.md, FEATURE-SCHEMA-LIFECYCLE.md, FEATURE-TRANSACTION-OPERATIONS.md.

## Workflow

1. Validate both accounts, the positive amount, and the real date.
2. Allocate consecutive identifiers.
3. Create the outgoing `TRANSFER` row with a negative amount.
4. Create the incoming `TRANSFER` row with a positive amount.
5. Validate all resulting balances before commit.
6. Emit both rows in identifier order.

## Programmatic Acceptance

=== AC transfer-success ===
Intent: A valid transfer creates two consecutive rows with opposite signed amounts and directional memos.
import csv
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    old = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = str(Path(tmp) / "ledger.db")
    try:
        assert cli_runner("init")[0] == 0
        assert cli_runner("load", "accounts", "sources/seed_accounts.csv")[0] == 0
        assert cli_runner("load", "categories", "sources/seed_categories.csv")[0] == 0
        assert cli_runner("load", "transactions", "sources/seed_transactions.csv")[0] == 0
        source = "DRAWER1"
        target = "SAFE"
        amount = "500.00"
        date = "2026-04-03"
        code, stdout, _ = cli_runner("transfer", source, target, amount, date)
        assert code == 0
        rows = list(csv.reader(stdout.splitlines()))
        first = rows[1]
        second = rows[2]
        assert int(second[0]) == int(first[0]) + 1
        assert first[2] == source
        assert second[2] == target
        assert first[3] == "TRANSFER"
        assert second[3] == "TRANSFER"
        assert first[4] == "-500.00"
        assert second[4] == amount
    finally:
        if old is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = old
=== END AC transfer-success ===

=== AC transfer-atomic ===
Intent: An insufficient-balance transfer is rejected without adding either transaction.
import csv
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    old = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = str(Path(tmp) / "ledger.db")
    try:
        assert cli_runner("init")[0] == 0
        assert cli_runner("load", "accounts", "sources/seed_accounts.csv")[0] == 0
        assert cli_runner("load", "categories", "sources/seed_categories.csv")[0] == 0
        assert cli_runner("load", "transactions", "sources/seed_transactions.csv")[0] == 0
        before = list(csv.reader(cli_runner("count")[1].splitlines()))[3][1]
        code, stdout, _ = cli_runner("transfer", "SAFE", "PETTY", "999.99", "2026-04-04")
        assert code == 3
        assert stdout == ""
        after = list(csv.reader(cli_runner("count")[1].splitlines()))[3][1]
        assert after == before
    finally:
        if old is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = old
=== END AC transfer-atomic ===

=== AC transfer-validation ===
Intent: Transfers reject non-positive amounts and identical accounts.
from cli.testing import cli_runner

for args in [
    ("DRAWER1", "DRAWER1", "1.00", "2026-04-03"),
    ("DRAWER1", "SAFE", "0.00", "2026-04-03"),
]:
    code, stdout, _ = cli_runner("transfer", *args)
    assert code == 3
    assert stdout == ""
=== END AC transfer-validation ===

## User Acceptance

- None.

## Guardrails

- Transfers create both rows or neither.
- The outgoing row precedes the incoming row.
- Account balances must remain non-negative.
- The transfer category and directional memos are fixed by the ledger contract.
