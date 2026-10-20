# FEATURE: Get Transaction

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Read one stored transaction by its id and write it as a CSV row. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md, FEATURE-TxnPost.md |
| Provides    | ledger txn get |
| Consumes    | db.transactions.get |

## Purpose

Lets the operator inspect a single posted or loaded transaction.

## Command

`ledger txn get <id>`

## Behavior

- Read the transaction with the given id from the database.
- On success, write the header and the transaction row as CSV, per FEATURE-CliOutput.
- An id that is not present exits 4 and writes nothing to standard output.
- The command never changes stored data.

## Database Interface

- `FEATURE-LEDGER-010` — read: get a transaction by id - supplies: `txn_id` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC txn-get-round-trip ===
Intent: The stored transaction is written as a CSV header and row carrying its stored fields.

# Exercises ledger txn get against a seeded transaction.
import csv
import io
import os
import tempfile

from cli.testing import cli_runner
from persistence.schema import AccountRow, CategoryRow, TransactionRow
from persistence.testing import db_session

txn_id = 1
date = "2026-04-01"
account = "DRAWER1"
category = "SALES"
amount_in = "45.50"
stored_amount = 4550
memo = "walk in sale"

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
with db_session(dsn) as db:
    db.accounts.create(AccountRow(account=account, name="Front Drawer"))
    db.categories.create(CategoryRow(category=category, description="Sales receipts"))
    db.transactions.create(
        TransactionRow(txn_id=txn_id, date=date, account=account, category=category, amount=stored_amount, memo=memo)
    )

code, out, err = cli_runner("txn", "get", str(txn_id))
print(out)
print(err)
assert code == 0

rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
assert rows[1] == [str(txn_id), date, account, category, amount_in, memo]
=== END AC txn-get-round-trip ===

=== AC txn-get-absent-id ===
Intent: An id that is not present exits 4.

# Exercises ledger txn get against an empty transactions table.
import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

absent_id = "999"
not_found_exit = 4

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
with db_session(dsn):
    pass

code, out, err = cli_runner("txn", "get", absent_id)
print(out)
print(err)
assert code == not_found_exit
=== END AC txn-get-absent-id ===

## User Acceptance

- None.

## Guardrails

- Do not read the transaction from a cached or in-memory copy; every read goes to the database.
- Do not write to the database from this command.
- Do not use floating point when formatting the amount.
