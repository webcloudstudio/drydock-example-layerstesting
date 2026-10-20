# FEATURE: Post Transaction

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Post one cash transaction to an existing account and category, assigning the next transaction id. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-AccountAdd.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md, FEATURE-CommandTransaction.md, FEATURE-NonNegativeBalance.md, FEATURE-ValidateText.md, FEATURE-ValidateAmount.md, FEATURE-ValidateDate.md |
| Provides    | ledger txn post |
| Consumes    | db.accounts.get, db.categories.get, db.transactions.list, db.transactions.create |

## Purpose

Adds one transaction to the ledger. The command is the only way a new cash movement enters the
store outside `ledger load` and `ledger transfer`.

## Command

`ledger txn post <account> <category> <amount> <date> [<memo>]`

## Behavior

- Validate the account and category codes with FEATURE-ValidateText, the amount with
  FEATURE-ValidateAmount, and the date with FEATURE-ValidateDate. Any violation exits 3.
- An account or category that is not present exits 3 and stores nothing.
- Assign `txn_id` one more than the largest id present, or `1` when the table is empty. The largest
  id is computed from the stored rows, never assumed.
- Store the amount as integer cents. Store the memo as given; when the memo argument is omitted,
  store an empty memo.
- Run the command inside the transaction wrapper of FEATURE-CommandTransaction. The stored row is
  rejected with exit 3 when it would leave the account balance below zero, per
  FEATURE-NonNegativeBalance.
- On success, write the new row as the transaction CSV row defined by FEATURE-CliOutput.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC txn-post-round-trip ===
Intent: A posted transaction is stored with the supplied fields and is read back unchanged, with id 1 in an empty table.

# Exercises ledger txn post, then reads the stored row back through the persistence library.
import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database
from persistence.schema import AccountRow, CategoryRow, TransactionKey
from persistence.testing import db_session

account = "DRAWER1"
category = "SALES"
date = "2026-04-01"
amount_in = "45.50"
memo = "walk in sale"

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
with db_session(dsn) as db:
    db.accounts.create(AccountRow(account=account, name="Front Drawer"))
    db.categories.create(CategoryRow(category=category, description="Sales receipts"))

code, out, err = cli_runner("txn", "post", account, category, amount_in, date, memo)
print(out)
print(err)
assert code == 0

row = open_database(dsn).transactions.get(TransactionKey(txn_id=1))
assert row is not None
assert row.account == account
assert row.category == category
assert row.date == date
assert row.amount == 4550
assert row.memo == memo
=== END AC txn-post-round-trip ===

=== AC txn-post-id-sequence ===
Intent: A posted transaction receives one more than the largest existing txn_id.

# Exercises ledger txn post against a table that already holds id 7.
import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database
from persistence.schema import AccountRow, CategoryRow, TransactionKey, TransactionRow
from persistence.testing import db_session

account = "DRAWER1"
category = "SALES"
date = "2026-04-01"
memo = "next"
seeded_id = 7
next_id = seeded_id + 1

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
with db_session(dsn) as db:
    db.accounts.create(AccountRow(account=account, name="Front Drawer"))
    db.categories.create(CategoryRow(category=category, description="Sales receipts"))
    db.transactions.create(
        TransactionRow(txn_id=seeded_id, date=date, account=account, category=category, amount=100, memo="seed")
    )

code, out, err = cli_runner("txn", "post", account, category, "1.00", date, memo)
print(out)
print(err)
assert code == 0

row = open_database(dsn).transactions.get(TransactionKey(txn_id=next_id))
assert row is not None
assert row.memo == memo
=== END AC txn-post-id-sequence ===

=== AC txn-post-empty-memo ===
Intent: A transaction posted without a memo stores an empty memo field.

# Exercises ledger txn post with the memo argument omitted.
import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database
from persistence.schema import AccountRow, CategoryRow, TransactionKey
from persistence.testing import db_session

account = "DRAWER1"
category = "SALES"
date = "2026-04-01"

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
with db_session(dsn) as db:
    db.accounts.create(AccountRow(account=account, name="Front Drawer"))
    db.categories.create(CategoryRow(category=category, description="Sales receipts"))

code, out, err = cli_runner("txn", "post", account, category, "1.00", date)
print(out)
print(err)
assert code == 0

row = open_database(dsn).transactions.get(TransactionKey(txn_id=1))
assert row is not None
assert row.memo == ""
=== END AC txn-post-empty-memo ===

=== AC txn-post-rejects-invalid-fields ===
Intent: Each unknown reference or invalid field exits 3 and stores no transaction.

# Exercises ledger txn post with four rejected argument sets.
import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database
from persistence.schema import AccountRow, CategoryRow
from persistence.testing import db_session

account = "DRAWER1"
category = "SALES"
date = "2026-04-01"
rejected_exit = 3
stored_before = 0

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
with db_session(dsn) as db:
    db.accounts.create(AccountRow(account=account, name="Front Drawer"))
    db.categories.create(CategoryRow(category=category, description="Sales receipts"))

cases = [
    ("unknown account", "NOSUCH", category, "1.00", date),
    ("unknown category", account, "NOSUCH", "1.00", date),
    ("amount with three decimals", account, category, "1.234", date),
    ("impossible date", account, category, "1.00", "2026-02-30"),
]
for name, acct, cat, amount_text, when in cases:
    code, out, err = cli_runner("txn", "post", acct, cat, amount_text, when)
    print(name, code, err)
    assert code == rejected_exit
    assert len(open_database(dsn).transactions.list()) == stored_before
=== END AC txn-post-rejects-invalid-fields ===

=== AC txn-post-refuses-negative-balance ===
Intent: A post that would leave the account balance below zero exits 3 and stores nothing.

# Exercises ledger txn post against an account with a zero balance.
import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database
from persistence.schema import AccountRow, CategoryRow
from persistence.testing import db_session

account = "DRAWER1"
category = "SUPPLY"
date = "2026-04-01"
rejected_exit = 3
stored_before = 0

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
with db_session(dsn) as db:
    db.accounts.create(AccountRow(account=account, name="Front Drawer"))
    db.categories.create(CategoryRow(category=category, description="Supplies"))

code, out, err = cli_runner("txn", "post", account, category, "-1.00", date, "tape")
print(out)
print(err)
assert code == rejected_exit
assert len(open_database(dsn).transactions.list()) == stored_before
=== END AC txn-post-refuses-negative-balance ===

## User Acceptance

- None.

## Guardrails

- Do not hardcode a transaction id, a balance, or a report total; compute each from the database.
- Do not open a database driver outside the shipped persistence library.
- Do not use floating point for amounts at any layer.
- Do not store a row for a command that exits non-zero.
