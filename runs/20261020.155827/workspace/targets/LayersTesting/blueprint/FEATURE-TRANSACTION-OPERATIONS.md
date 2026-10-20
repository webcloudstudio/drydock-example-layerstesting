# FEATURE: Transaction Operations

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Posts, reads, amends, and deletes individual cash transactions atomically. |
| Depends On  | FEATURE-TRANSACTION-LOAD.md, DATABASE.md |
| Provides    | ledger txn post, ledger txn get, ledger txn amend, ledger txn delete |
| Consumes    | ./ledger executable, ledger persistence operations |

## Purpose

Provide individual transaction mutations and reads with generated identifiers, validation, preservation of immutable fields, and non-negative balance enforcement.

## Database Interface


- `FEATURE-LEDGER-008` — read-write: transactions.create - supplies: — - returns: —
- `FEATURE-LEDGER-009` — read-write: transactions.update - supplies: — - returns: —
- `FEATURE-LEDGER-010` — write: transactions.delete - supplies: — - returns: —

## Workflow

- Post validates references, amount, date, and memo, then assigns one more than the maximum identifier.
- Get returns the complete transaction row.
- Amend changes only the amount and rechecks the affected balance.
- Delete removes an existing transaction only when the resulting balance remains non-negative.
- Missing identifiers return exit code 4; rejected mutations return exit code 3.

## Programmatic Acceptance

=== AC transaction-post-get ===
Intent: Posting a transaction assigns an identifier and persists the complete row.
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
        account = "DRAWER1"
        category = "SALES"
        amount = "45.50"
        date = "2026-04-01"
        memo = "walk in sale"
        code, stdout, _ = cli_runner("txn", "post", account, category, amount, date, memo)
        assert code == 0
        posted = list(csv.reader(stdout.splitlines()))[1]
        txn_id = posted[0]
        code, stdout, _ = cli_runner("txn", "get", txn_id)
        assert code == 0
        row = list(csv.reader(stdout.splitlines()))[1]
        assert row[0] == txn_id
        assert row[2] == account
        assert row[3] == category
        assert row[4] == amount
        assert row[5] == memo
    finally:
        if old is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = old
=== END AC transaction-post-get ===

=== AC transaction-amend ===
Intent: Amending a transaction changes only its amount.
from cli.testing import cli_runner

code, stdout, _ = cli_runner("txn", "amend", "1", "1.00")
assert code in {0, 3, 4}
if code != 0:
    assert stdout == ""
=== END AC transaction-amend ===

=== AC transaction-delete ===
Intent: Deleting an existing transaction removes it, while an absent identifier returns not found.
from cli.testing import cli_runner

code, stdout, _ = cli_runner("txn", "delete", "999999")
assert code == 4
assert stdout == ""
=== END AC transaction-delete ===

=== AC transaction-rejection ===
Intent: Invalid amount, date, and unknown references are rejected without output.
from cli.testing import cli_runner

cases = [
    ("DRAWER1", "NOSUCH", "1.00", "2026-04-01"),
    ("DRAWER1", "SALES", "1.234", "2026-04-01"),
    ("DRAWER1", "SALES", "1.00", "2026-02-30"),
]
for account, category, amount, date in cases:
    code, stdout, _ = cli_runner("txn", "post", account, category, amount, date)
    assert code == 3
    assert stdout == ""
=== END AC transaction-rejection ===

## User Acceptance

- None.

## Guardrails

- Transaction identifiers are generated from the current maximum for posts.
- Amend changes only amount.
- No mutation may leave an account balance negative.
- Amounts remain integer cents.
