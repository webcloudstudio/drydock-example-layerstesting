# FEATURE: Transfer Rejection

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Rejects invalid transfers with exit 3 and no change to any table. |
| Depends On  | FEATURE-TRANSFER.md, FEATURE-VALIDATE-AMOUNT.md |

## Purpose

A transfer is rejected when its two accounts are identical, its amount is not positive, its amount is zero, or either account is unknown. Each rejection exits 3, writes nothing to standard output, and leaves every table exactly as it was.

## Behavior

1. Check that `<from>` and `<to>` differ.
2. Check that `<amount>` is positive and passes the amount rules.
3. Check that both accounts exist.
4. On any failure, roll back and exit 3 with one diagnostic line on standard error.

## Programmatic Acceptance

=== AC transfer-rejects-invalid-cases ===
Intent: Each invalid transfer exits 3, writes nothing to standard output, and leaves the stored transactions unchanged.

import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database

os.environ["DATABASE_URL"] = os.path.join(tempfile.mkdtemp(), "ledger.db")
for args in (
    ("init",),
    ("load", "accounts", "sources/seed_accounts.csv"),
    ("load", "categories", "sources/seed_categories.csv"),
    ("load", "transactions", "sources/seed_transactions.csv"),
):
    code, out, err = cli_runner(*args)
    assert code == 0, err

db = open_database(os.environ["DATABASE_URL"])


def snapshot():
    return sorted((row.txn_id, row.account, row.amount) for row in db.transactions.list())


cases = (
    ("DRAWER1", "DRAWER1", "1.00"),
    ("DRAWER1", "SAFE", "-5.00"),
    ("DRAWER1", "SAFE", "0.00"),
    ("DRAWER1", "NOSUCH", "1.00"),
)
for from_account, to_account, amount_text in cases:
    before = snapshot()
    code, out, err = cli_runner("transfer", from_account, to_account, amount_text, "2026-04-04")
    assert code == 3, (from_account, to_account, amount_text, err)
    assert out == ""
    assert snapshot() == before
=== END AC transfer-rejects-invalid-cases ===

## User Acceptance

- None.

## Guardrails

- A rejected transfer never stores either of its two rows.
- A rejection never writes to standard output.
