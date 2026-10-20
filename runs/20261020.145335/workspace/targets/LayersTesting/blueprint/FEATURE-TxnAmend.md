# FEATURE: Amend Transaction Amount

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Change only the amount of one stored transaction, rejecting any change that leaves a balance negative. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md, FEATURE-CommandTransaction.md, FEATURE-NonNegativeBalance.md, FEATURE-TxnGet.md, FEATURE-ValidateAmount.md |
| Provides    | ledger txn amend |
| Consumes    | db.transactions.get, db.transactions.update, db.transactions.list |

## Purpose

Corrects the amount of a recorded transaction without altering its date, account, category, or memo.

## Command

`ledger txn amend <id> <amount>`

## Behavior

- Validate the amount with FEATURE-ValidateAmount. A violation exits 3.
- An id that is not present exits 4 and changes nothing.
- Update only the amount, stored as integer cents. Date, account, category, and memo are unchanged.
- Run inside the transaction wrapper of FEATURE-CommandTransaction. If any account balance would be
  below zero after the change, per FEATURE-NonNegativeBalance, the command exits 3 and the stored
  amount is unchanged.
- On success, write the updated transaction row per FEATURE-CliOutput.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC txn-amend-round-trip ===
Intent: Amending a transaction changes only its amount, and the stored row reads back with that single change.

# Exercises ledger txn amend against a seeded transaction.
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
memo = "walk in sale"
seeded_amount = 10000
amount_in = "54.50"
amended_amount = 5450

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
with db_session(dsn) as db:
    db.accounts.create(AccountRow(account=account, name="Front Drawer"))
    db.categories.create(CategoryRow(category=category, description="Sales receipts"))
    db.transactions.create(
        TransactionRow(txn_id=txn_id, date=date, account=account, category=category, amount=seeded_amount, memo=memo)
    )

code, out, err = cli_runner("txn", "amend", str(txn_id), amount_in)
print(out)
print(err)
assert code == 0

row = open_database(dsn).transactions.get(TransactionKey(txn_id=txn_id))
assert row is not None
assert row.amount == amended_amount
assert row.date == date
assert row.account == account
assert row.category == category
assert row.memo == memo
=== END AC txn-amend-round-trip ===

=== AC txn-amend-absent-id ===
Intent: Amending an id that is not present exits 4.

# Exercises ledger txn amend against an empty transactions table.
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

code, out, err = cli_runner("txn", "amend", absent_id, "1.00")
print(out)
print(err)
assert code == not_found_exit
=== END AC txn-amend-absent-id ===

=== AC txn-amend-refuses-negative-balance ===
Intent: An amendment that would leave the account balance below zero exits 3 and leaves the stored amount unchanged.

# Exercises ledger txn amend with an amount that drives the only transaction negative.
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
memo = "walk in sale"
seeded_amount = 10000
rejected_exit = 3

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
with db_session(dsn) as db:
    db.accounts.create(AccountRow(account=account, name="Front Drawer"))
    db.categories.create(CategoryRow(category=category, description="Sales receipts"))
    db.transactions.create(
        TransactionRow(txn_id=txn_id, date=date, account=account, category=category, amount=seeded_amount, memo=memo)
    )

code, out, err = cli_runner("txn", "amend", str(txn_id), "-1.00")
print(out)
print(err)
assert code == rejected_exit

row = open_database(dsn).transactions.get(TransactionKey(txn_id=txn_id))
assert row is not None
assert row.amount == seeded_amount
=== END AC txn-amend-refuses-negative-balance ===

## User Acceptance

- None.

## Guardrails

- Do not change any field except the amount.
- Do not hardcode a balance; compute it from the transaction rows.
- Do not use floating point for the amount at any layer.
