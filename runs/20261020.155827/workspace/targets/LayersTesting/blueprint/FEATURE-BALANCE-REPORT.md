# FEATURE: Balance Report

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Reports computed transaction counts and balances for every account. |
| Depends On  | FEATURE-ACCOUNT-OPERATIONS.md, FEATURE-TRANSACTION-OPERATIONS.md, FEATURE-TRANSFERS.md, DATABASE.md |
| Provides    | ledger report balances |
| Consumes    | ./ledger executable, ledger persistence operations |

## Purpose

Compute the balances report directly from account and transaction data, including accounts with no transactions and a computed total row.

## Database Interface


- None — persistence is owned by DATABASE.md, FEATURE-ACCOUNT-CATEGORY-LOAD.md, FEATURE-ACCOUNT-OPERATIONS.md, FEATURE-SCHEMA-LIFECYCLE.md, FEATURE-TRANSACTION-OPERATIONS.md.

## Report Contract

The report emits:

- `account,name,transactions,balance`
- One row per account ordered by account code.
- `TOTAL,,<count>,<sum>` using aggregate transaction count and balance.
- Amounts formatted with exactly two decimal places.

## Programmatic Acceptance

=== AC balance-report-empty ===
Intent: The balances report includes an account with no transactions and a zero balance.
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
        account = "CASH9"
        name = "Event Float"
        assert cli_runner("account", "add", account, name)[0] == 0
        code, stdout, _ = cli_runner("report", "balances")
        assert code == 0
        rows = list(csv.reader(stdout.splitlines()))
        matching = [row for row in rows[1:] if row[0] == account]
        assert len(matching) == 1
        assert matching[0][1] == name
        assert matching[0][2] == "0"
        assert matching[0][3] == "0.00"
    finally:
        if old is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = old
=== END AC balance-report-empty ===

=== AC balance-report-computed ===
Intent: The balances report reflects stored transaction counts and signed amounts.
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
        code, stdout, _ = cli_runner("report", "balances")
        assert code == 0
        rows = list(csv.reader(stdout.splitlines()))
        assert rows[0] == ["account", "name", "transactions", "balance"]
        accounts = [row[0] for row in rows[1:-1]]
        assert accounts == sorted(accounts)
        total = rows[-1]
        assert total[0] == "TOTAL"
        assert int(total[2]) == 120
    finally:
        if old is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = old
=== END AC balance-report-computed ===

=== AC balance-report-no-hardcoding ===
Intent: Changing persisted transactions changes the computed account report.
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
        before = list(csv.reader(cli_runner("report", "balances")[1].splitlines()))
        assert cli_runner("txn", "post", "DRAWER1", "SALES", "1.00", "2026-04-01")[0] == 0
        after = list(csv.reader(cli_runner("report", "balances")[1].splitlines()))
        before_row = next(row for row in before if row[0] == "DRAWER1")
        after_row = next(row for row in after if row[0] == "DRAWER1")
        assert int(after_row[2]) == int(before_row[2]) + 1
    finally:
        if old is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = old
=== END AC balance-report-no-hardcoding ===

## User Acceptance

- None.

## Guardrails

- Every account remains visible, including unused accounts.
- Values are computed from database queries, never hardcoded.
- Ordering is by account code.
- The total row is derived from the detailed transaction data.
