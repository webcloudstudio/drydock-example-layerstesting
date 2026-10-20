# FEATURE: Transaction Management

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Post, retrieve, amend, and delete ledger transactions. |
| Depends On  | FEATURE-Transaction-Loading.md, FEATURE-Account-Category-Loading.md |
| Provides    | txn post, txn get, txn amend, txn delete |
| Consumes    | command dispatch, database configuration, transactions.create, transactions.get, transactions.update, transactions.delete |

## Purpose

Manage transaction rows with generated identifiers, exact cent formatting, validated dates and amounts, and atomic balance checks.

## Operations

- `txn post` assigns one greater than the largest existing identifier.
- `txn get` retrieves a persisted transaction.
- `txn amend` changes only the amount.
- `txn delete` removes a transaction when the resulting balance remains non-negative.

## Database Interface


- `FEATURE-DB-006` — read-write: transactions.get - supplies: `txn_id` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC transaction-crud-roundtrip ===
Intent: Posting, reading, amending, and deleting a transaction persist the documented fields.
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
    assert cli_runner("txn", "post", "A1", "C1", "12.34", "2026-01-01", "sale")[0] == 0
    code, out, _ = cli_runner("txn", "get", "1")
    assert code == 0
    row = list(csv.reader(out.splitlines()))[1]
    assert row[0:5] == ["1", "2026-01-01", "A1", "C1", "12.34"]
    assert cli_runner("txn", "amend", "1", "10.00")[0] == 0
    code, out, _ = cli_runner("txn", "get", "1")
    assert code == 0
    assert list(csv.reader(out.splitlines()))[1][4] == "10.00"
    assert cli_runner("txn", "delete", "1")[0] == 0
    assert cli_runner("txn", "get", "1")[0] == 4
=== END AC transaction-crud-roundtrip ===

=== AC transaction-validation ===
Intent: Invalid references, amounts, dates, memos, and absent identifiers are rejected.
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    os.environ["DATABASE_PATH"] = str(Path(d) / "ledger.db")
    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "A1", "Drawer")[0] == 0
    assert cli_runner("category", "add", "C1", "Sales")[0] in (0, 2, 3)
    assert cli_runner("txn", "post", "A1", "NOPE", "1.00", "2026-01-01")[0] == 3
    assert cli_runner("txn", "post", "A1", "C1", "1.234", "2026-01-01")[0] == 3
    assert cli_runner("txn", "post", "A1", "C1", "1.00", "2026-02-30")[0] == 3
    assert cli_runner("txn", "get", "999")[0] == 4
    assert cli_runner("txn", "amend", "999", "1.00")[0] == 4
    assert cli_runner("txn", "delete", "999")[0] == 4
=== END AC transaction-validation ===

=== AC transaction-id-generation ===
Intent: A posted transaction receives the next identifier after existing rows.
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    os.environ["DATABASE_PATH"] = str(Path(d) / "ledger.db")
    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "A1", "Drawer")[0] == 0
    assert cli_runner("category", "add", "C1", "Sales")[0] in (0, 2, 3)
    assert cli_runner("txn", "post", "A1", "C1", "1.00", "2026-01-01")[0] == 0
    assert cli_runner("txn", "post", "A1", "C1", "2.00", "2026-01-02")[0] == 0
    assert cli_runner("txn", "get", "2")[0] == 0
=== END AC transaction-id-generation ===

## User Acceptance

- None.

## Guardrails

- Amounts are parsed and stored as integer cents.
- Amendment preserves date, account, category, and memo.
- Rejected mutations write nothing.
