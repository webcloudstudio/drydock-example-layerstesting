# FEATURE: Bulk Transaction Loading

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Loads validated transaction CSV files atomically into the ledger. |
| Depends On  | DATABASE.md, FEATURE-Validation.md, FEATURE-Bulk-Reference-Loading.md |
| Provides    | `ledger load transactions` |
| Consumes    | domain validation, relational ledger schema, transaction persistence operations |

## Purpose

Load a transaction CSV file only after validating its complete contents, references, identifiers, and resulting account balances.

## Workflow

1. Validate the file header and every row.
2. Reject duplicate transaction identifiers and invalid values.
3. Resolve every account and category reference.
4. Evaluate balances after applying the complete batch.
5. Insert all rows in one transaction.
6. Emit the loaded-row result only after commit.

A rejected file changes no table.

## Database Interface


- None — persistence is owned by DATABASE.md, FEATURE-Accounts.md, FEATURE-Balance-Reports.md, FEATURE-Category-Reports.md, FEATURE-Monthly-Reports.md, FEATURE-Transaction-Mutation.md, FEATURE-Transaction-Posting.md.

## Programmatic Acceptance

=== AC load-transactions-valid ===
Intent: A valid transaction CSV is loaded and its supplied row count is reported.
from pathlib import Path
import csv
import tempfile
from cli.testing import cli_runner

rows = [
    ["txn_id", "date", "account", "category", "amount", "memo"],
    ["1", "2026-01-01", "A", "C", "10.00", "opening"],
]
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "transactions.csv"
    path.write_text("\n".join(",".join(row) for row in rows) + "\n")
    code, stdout, stderr = cli_runner("load", "transactions", str(path))
    parsed = list(csv.reader(stdout.splitlines()))
    assert code == 0
    assert parsed[0] == ["table", "loaded"]
    assert parsed[1] == ["transactions", str(len(rows) - 1)]
=== END AC load-transactions-valid ===

=== AC load-transactions-invalid-is-atomic ===
Intent: A transaction file with an unknown account is rejected before any row is written.
from pathlib import Path
import tempfile
from cli.testing import cli_runner

rows = [
    "txn_id,date,account,category,amount,memo",
    "1,2026-01-01,A,C,10.00,valid",
    "2,2026-01-01,NOSUCH,C,10.00,invalid",
]
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "transactions.csv"
    path.write_text("\n".join(rows) + "\n")
    code, stdout, stderr = cli_runner("load", "transactions", str(path))
    assert code == 3
    assert stdout == ""
    count_code, count_stdout, count_stderr = cli_runner("count")
    assert count_code == 0
    assert "transactions,0" in count_stdout
=== END AC load-transactions-invalid-is-atomic ===

=== AC load-transactions-negative-balance ===
Intent: A batch that would make an account balance negative is rejected.
from pathlib import Path
import tempfile
from cli.testing import cli_runner

rows = [
    "txn_id,date,account,category,amount,memo",
    "1,2026-01-01,A,C,-1.00,overdraw",
]
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "transactions.csv"
    path.write_text("\n".join(rows) + "\n")
    code, stdout, stderr = cli_runner("load", "transactions", str(path))
    assert code == 3
    assert stdout == ""
=== END AC load-transactions-negative-balance ===

## User Acceptance

- None.

## Guardrails

- Validate the entire file before the first insert.
- Never read or modify supplied source fixtures from application code.
- Store amounts as integer cents.
- Preserve transaction identifiers supplied by the file.
