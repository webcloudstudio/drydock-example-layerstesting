# FEATURE: Delete Transaction

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Remove one stored transaction by id, refusing any removal that leaves a balance negative. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md, FEATURE-CommandTransaction.md, FEATURE-NonNegativeBalance.md, FEATURE-TxnGet.md |
| Provides    | ledger txn delete |
| Consumes    | db.transactions.get, db.transactions.delete, db.transactions.list |

## Purpose

Removes a transaction recorded in error, while keeping every account balance non-negative.

## Command

`ledger txn delete <id>`

## Behavior

- An id that is not present exits 4 and changes nothing.
- Delete the transaction row. Run inside the transaction wrapper of FEATURE-CommandTransaction.
- If any account balance would be below zero after the deletion, per FEATURE-NonNegativeBalance, the
  command exits 3 and the row remains stored.
- On success, write `deleted` then the id, per FEATURE-CliOutput.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC txn-delete-round-trip ===
Intent: Deleting an existing transaction removes it, and a read by its id then finds nothing.

# Exercises ledger txn delete against a seeded transaction whose removal keeps the balance non-negative.
import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database
from persistence.schema import AccountRow, CategoryRow, TransactionKey, TransactionRow
from persistence.testing import db_session

txn_id = 1
date = "2026-04-01"
account = "DRAWER1"
category = "SALES"

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
with db_session(dsn) as db:
    db.accounts.create(AccountRow(account=account, name="Front Drawer"))
    db.categories.create(CategoryRow(category=category, description="Sales receipts"))
    db.transactions.create(
        TransactionRow(txn_id=txn_id, date=date, account=account, category=category, amount=10000, memo="sale")
    )

code, out, err = cli_runner("txn", "delete", str(txn_id))
print(out)
print(err)
assert code == 0
assert open_database(dsn).transactions.get(TransactionKey(txn_id=txn_id)) is None
=== END AC txn-delete-round-trip ===

=== AC txn-delete-absent-id ===
Intent: Deleting an id that is not present exits 4.

# Exercises ledger txn delete against an empty transactions table.
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

code, out, err = cli_runner("txn", "delete", absent_id)
print(out)
print(err)
assert code == not_found_exit
=== END AC txn-delete-absent-id ===

=== AC txn-delete-refuses-negative-balance ===
Intent: Deleting a transaction that would leave the account balance below zero exits 3 and keeps the row.

# Exercises ledger txn delete on the credit that funds a later debit.
import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database
from persistence.schema import AccountRow, CategoryRow, TransactionKey, TransactionRow
from persistence.testing import db_session

txn_id = 1
debit_id = 2
date = "2026-04-01"
account = "DRAWER1"
category = "SALES"
credit_amount = 10000
debit_amount = -5000
rejected_exit = 3

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
with db_session(dsn) as db:
    db.accounts.create(AccountRow(account=account, name="Front Drawer"))
    db.categories.create(CategoryRow(category=category, description="Sales receipts"))
    db.transactions.create(
        TransactionRow(txn_id=txn_id, date=date, account=account, category=category, amount=credit_amount, memo="sale")
    )
    db.transactions.create(
        TransactionRow(txn_id=debit_id, date=date, account=account, category=category, amount=debit_amount, memo="refund")
    )

code, out, err = cli_runner("txn", "delete", str(txn_id))
print(out)
print(err)
assert code == rejected_exit

row = open_database(dsn).transactions.get(TransactionKey(txn_id=txn_id))
assert row is not None
assert row.amount == credit_amount
=== END AC txn-delete-refuses-negative-balance ===

## User Acceptance

- None.

## Guardrails

- Do not delete a row for a command that exits non-zero.
- Do not hardcode a balance; compute it from the transaction rows.
- Do not open a database driver outside the shipped persistence library.
