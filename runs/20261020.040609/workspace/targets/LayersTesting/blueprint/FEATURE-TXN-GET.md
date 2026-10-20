# FEATURE: Transaction Get

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Read one transaction by id through `ledger txn get <id>`. |
| Depends On  | DATABASE.md, FEATURE-TXN-POST.md |
| Provides    | ledger txn get |
| Consumes    | transactions.get |

## Purpose

`ledger txn get <id>` reads a single transaction and writes it as a report row. The command changes
nothing.

## Behavior

- Read the transaction with the given id.
- An absent id exits 4 and writes nothing to standard output.
- On success, write the header `txn_id,date,account,category,amount,memo` and the one transaction row.
  Amounts are written with exactly two decimal places.

## Database Interface

- `FEATURE-TXN-002` — read: get a transaction by id - supplies: `txn_id` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC txn-get-returns-row ===
Intent: Getting an existing transaction exits 0, writes the header and exactly one data row, and names the requested id.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
account_code = "CASH1"
category_code = "SALES"
date_value = "2026-04-01"
seeded_cents = 4550
txn_id_value = 1
with db_session(dsn) as db:
    db.accounts.create(account=account_code, name="Cash One")
    db.categories.create(category=category_code, description="Sales receipts")
    db.transactions.create(
        txn_id=txn_id_value, date=date_value, account=account_code, category=category_code,
        amount=seeded_cents, memo="walk in sale",
    )
txn_id_text = "1"

exit_code, out, err = cli_runner("txn", "get", txn_id_text)
print(out)
print(err)
assert exit_code == 0
lines = out.splitlines()
assert lines[0] == "txn_id,date,account,category,amount,memo"
assert len(lines) == 2
assert int(lines[1].split(",")[0]) == txn_id_value
=== END AC txn-get-returns-row ===

=== AC txn-get-absent-id ===
Intent: Getting a transaction id that does not exist exits 4 and writes nothing.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
absent_id_text = "999"
with db_session(dsn) as db:
    count_before = len(db.transactions.list())

exit_code, out, err = cli_runner("txn", "get", absent_id_text)
print(out)
print(err)
assert exit_code == 4
assert out == ""
with db_session(dsn) as db:
    assert len(db.transactions.list()) == count_before
=== END AC txn-get-absent-id ===

## User Acceptance

- None.

## Guardrails

- `txn get` never writes to the database.
- `txn get` never writes a row for an absent id.
