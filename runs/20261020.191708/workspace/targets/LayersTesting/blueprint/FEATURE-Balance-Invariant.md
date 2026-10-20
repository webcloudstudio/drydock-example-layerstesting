# FEATURE: Balance Invariant

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Enforce non-negative account balances before every transaction mutation. |
| Depends On  | FEATURE-Transaction-Management.md, FEATURE-Transaction-Loading.md |
| Provides    | prospective balance validation |
| Consumes    | transactions.create, transactions.update, transactions.delete |

## Purpose

Every posting, amendment, deletion, transfer, and transaction load computes the affected account balances before writing. Any negative result rejects the complete command with no table changes.

## Invariant

For each account, the sum of all persisted transaction amounts must be greater than or equal to zero after every successful command.

## Database Interface


- None — persistence is owned by DATABASE.md, FEATURE-Account-Category-Loading.md, FEATURE-Account-Management.md, FEATURE-Transaction-Loading.md, FEATURE-Transaction-Management.md.

## Programmatic Acceptance

=== AC negative-posting-rejected ===
Intent: A transaction that would make an account balance negative is rejected atomically.
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    os.environ["DATABASE_PATH"] = str(Path(d) / "ledger.db")
    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "A1", "Drawer")[0] == 0
    assert cli_runner("category", "add", "C1", "Supply")[0] in (0, 2, 3)
    assert cli_runner("txn", "post", "A1", "C1", "-1.00", "2026-01-01")[0] == 3
    assert cli_runner("txn", "get", "1")[0] == 4
=== END AC negative-posting-rejected ===

=== AC negative-amend-rejected ===
Intent: An amendment that would make the account balance negative leaves the transaction unchanged.
import csv
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    os.environ["DATABASE_PATH"] = str(Path(d) / "ledger.db")
    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "A1", "Drawer")[0] == 0
    assert cli_runner("category", "add", "C1", "Sales")[0] in (0, 2, 3)
    assert cli_runner("txn", "post", "A1", "C1", "5.00", "2026-01-01")[0] == 0
    assert cli_runner("txn", "amend", "1", "-6.00")[0] == 3
    code, out, _ = cli_runner("txn", "get", "1")
    assert code == 0
    assert list(csv.reader(out.splitlines()))[1][4] == "5.00"
=== END AC negative-amend-rejected ===

=== AC negative-delete-rejected ===
Intent: Deleting the only positive transaction is rejected when it would make the balance negative.
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    os.environ["DATABASE_PATH"] = str(Path(d) / "ledger.db")
    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "A1", "Drawer")[0] == 0
    assert cli_runner("category", "add", "C1", "Sales")[0] in (0, 2, 3)
    assert cli_runner("txn", "post", "A1", "C1", "5.00", "2026-01-01")[0] == 0
    assert cli_runner("txn", "delete", "1")[0] == 3
    assert cli_runner("txn", "get", "1")[0] == 0
=== END AC negative-delete-rejected ===

## User Acceptance

- None.

## Guardrails

- Prospective balances are checked before the first write.
- Failed operations preserve every table.
- No successful command leaves an account balance below zero.
