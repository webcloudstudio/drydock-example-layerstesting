# FEATURE: Transfer Between Accounts

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Move a positive amount between two accounts as two linked TRANSFER transactions, or store neither. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-AccountAdd.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md, FEATURE-CommandTransaction.md, FEATURE-NonNegativeBalance.md, FEATURE-ValidateAmount.md, FEATURE-ValidateDate.md, FEATURE-ValidateText.md |
| Provides    | ledger transfer |
| Consumes    | db.accounts.get, db.transactions.list, db.transactions.create |

## Purpose

Records a movement of cash between two places, such as drawer to safe, as a matched pair of rows.

## Command

`ledger transfer <from> <to> <amount> <date>`

## Behavior

- Validate both account codes with FEATURE-ValidateText, the amount with FEATURE-ValidateAmount, and
  the date with FEATURE-ValidateDate. A violation exits 3.
- The amount must be positive. The two accounts must differ. Either rule failing exits 3.
- An account that is not present exits 3.
- Write two rows in category `TRANSFER`, both in one transaction. The outgoing row takes the next
  id after the largest present; the incoming row takes the id after that.
  - Outgoing: the source account, a negative amount, memo `transfer to <to>`.
  - Incoming: the destination account, a positive amount, memo `transfer from <from>`.
- If either account balance would be below zero after both rows, per FEATURE-NonNegativeBalance,
  the command exits 3 and neither row is stored.
- On success, write the two rows as CSV per FEATURE-CliOutput, outgoing first.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC xfer-round-trip ===
Intent: A transfer stores two TRANSFER rows, outgoing first with the next two ids, with the linked memos and opposite signed amounts.

# Exercises ledger transfer between two seeded accounts.
import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database
from persistence.schema import AccountRow, CategoryRow, TransactionKey, TransactionRow
from persistence.testing import db_session

source = "DRAWER1"
destination = "SAFE"
category = "SALES"
transfer_category = "TRANSFER"
date = "2026-04-03"
amount_in = "50.00"
moved_amount = 5000
outgoing_id = 2
incoming_id = 3

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
with db_session(dsn) as db:
    db.accounts.create(AccountRow(account=source, name="Front Drawer"))
    db.accounts.create(AccountRow(account=destination, name="Store Safe"))
    db.categories.create(CategoryRow(category=category, description="Sales receipts"))
    db.categories.create(CategoryRow(category=transfer_category, description="Internal transfer"))
    db.transactions.create(
        TransactionRow(txn_id=1, date=date, account=source, category=category, amount=10000, memo="sale")
    )

code, out, err = cli_runner("transfer", source, destination, amount_in, date)
print(out)
print(err)
assert code == 0

db = open_database(dsn)
out_row = db.transactions.get(TransactionKey(txn_id=outgoing_id))
in_row = db.transactions.get(TransactionKey(txn_id=incoming_id))
assert out_row is not None
assert in_row is not None
assert out_row.account == source
assert out_row.category == transfer_category
assert out_row.amount == -moved_amount
assert out_row.memo.split() == ["transfer", "to", destination]
assert in_row.account == destination
assert in_row.category == transfer_category
assert in_row.amount == moved_amount
assert in_row.memo.split() == ["transfer", "from", source]
=== END AC xfer-round-trip ===

=== AC xfer-rejects-invalid-transfers ===
Intent: Each invalid transfer exits 3 and stores neither row.

# Exercises ledger transfer with five rejected argument sets against one seeded transaction.
import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database
from persistence.schema import AccountRow, CategoryRow, TransactionRow
from persistence.testing import db_session

source = "DRAWER1"
destination = "SAFE"
category = "SALES"
date = "2026-04-03"
seeded_amount = 10000
stored_before = 1
rejected_exit = 3

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
with db_session(dsn) as db:
    db.accounts.create(AccountRow(account=source, name="Front Drawer"))
    db.accounts.create(AccountRow(account=destination, name="Store Safe"))
    db.categories.create(CategoryRow(category=category, description="Sales receipts"))
    db.categories.create(CategoryRow(category="TRANSFER", description="Internal transfer"))
    db.transactions.create(
        TransactionRow(txn_id=1, date=date, account=source, category=category, amount=seeded_amount, memo="sale")
    )

cases = [
    ("same account", source, source, "50.00"),
    ("zero amount", source, destination, "0.00"),
    ("negative amount", source, destination, "-5.00"),
    ("unknown account", source, "NOSUCH", "50.00"),
    ("overdraws source", source, destination, "500.00"),
]
for name, frm, to, amount_text in cases:
    code, out, err = cli_runner("transfer", frm, to, amount_text, date)
    print(name, code, err)
    assert code == rejected_exit
    assert len(open_database(dsn).transactions.list()) == stored_before
=== END AC xfer-rejects-invalid-transfers ===

## User Acceptance

- None.

## Guardrails

- Do not store one of the two transfer rows without the other.
- Do not hardcode the transfer ids; take them from the id sequence in the database.
- Do not use floating point for the amount at any layer.
- Do not let a transfer make either account balance negative.
