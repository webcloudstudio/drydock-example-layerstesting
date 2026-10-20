# FEATURE: Atomic Transaction Load Rejection

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | A transaction load with any invalid or duplicate row exits 3 and stores none of its rows. |
| Depends On  | FEATURE-LOAD-TRANSACTIONS.md, FEATURE-ATOMIC-COMMANDS.md, FEATURE-NONNEGATIVE-BALANCE.md, DATABASE.md |
| Provides    | ledger load transactions <csv> (atomic rejection) |
| Consumes    | ledger load transactions <csv>, transactions.create, accounts.get, categories.get |

## Purpose

A load of transactions is one command. If any row fails validation, references an unknown account
or category, or repeats a `txn_id`, the whole command is rejected. No row from the file persists,
including rows that were valid on their own. The rejection exits 3 and writes one diagnostic line
to standard error.

## Behavior

- Every row is validated before commit. The first failing row ends the command.
- The transaction is rolled back. Rows 1 to 10 of `sources/seed_transactions_bad.csv` do not persist
  when row 11 names the unknown account `NOSUCH`.
- A file containing two rows with the same `txn_id` is rejected in full.
- A rejected load leaves `transactions` exactly as it was.

## Database Interface

- `FEATURE-TXN-001` — write: create a transaction - supplies: `txn_id`, `date`, `account`, `category`, `amount`, `memo` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-ACCOUNT-002` — read: retrieve an account by code - supplies: `account` - returns: `account`, `name`
- `FEATURE-CATEGORY-002` — read: retrieve a category by code - supplies: `category` - returns: `category`, `description`

## Programmatic Acceptance

=== AC load-atomic-bad-file ===
# Intent: A transaction load whose row 11 names an unknown account exits 3 and stores none of rows 1 to 10.

import os
import sys
import tempfile
from pathlib import Path

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = str(Path(tempfile.mkdtemp()) / "ledger.db")
os.environ["DATABASE_URL"] = dsn

account_code = "DRAWER1"
account_name = "Front Drawer"
category_code = "SALES"
category_description = "Sales receipts"

exit_code, out, err = cli_runner("init")
assert exit_code == 0

with db_session(dsn) as db:
    db.accounts.create(account=account_code, name=account_name)
    db.categories.create(category=category_code, description=category_description)

bad_file = Path("sources/seed_transactions_bad.csv")
exit_code, out, err = cli_runner("load", "transactions", str(bad_file))
print(out)
print(err, file=sys.stderr)
assert exit_code == 3

with db_session(dsn) as db:
    assert len(db.transactions.list()) == 0
=== END AC load-atomic-bad-file ===

=== AC load-atomic-duplicate-key ===
# Intent: A transaction load that repeats a txn_id exits 3 and stores neither copy of the duplicated row.

import os
import sys
import tempfile
from pathlib import Path

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = str(Path(tempfile.mkdtemp()) / "ledger.db")
os.environ["DATABASE_URL"] = dsn

account_code = "DRAWER1"
account_name = "Front Drawer"
category_code = "SALES"
category_description = "Sales receipts"
header = "txn_id,date,account,category,amount,memo\n"
duplicate_id = 1
first_row = f"{duplicate_id},2026-04-01,{account_code},{category_code},10.00,first\n"
second_row = f"{duplicate_id},2026-04-01,{account_code},{category_code},10.00,second\n"

exit_code, out, err = cli_runner("init")
assert exit_code == 0

with db_session(dsn) as db:
    db.accounts.create(account=account_code, name=account_name)
    db.categories.create(category=category_code, description=category_description)

dup_file = Path(tempfile.mkdtemp()) / "duplicate.csv"
dup_file.write_text(header + first_row + second_row)

exit_code, out, err = cli_runner("load", "transactions", str(dup_file))
print(out)
print(err, file=sys.stderr)
assert exit_code == 3

with db_session(dsn) as db:
    assert len(db.transactions.list()) == 0
=== END AC load-atomic-duplicate-key ===

## User Acceptance

- None.

## Guardrails

- A load never stores a partial file. Either every row persists or none does.
- Application code never reads `sources/seed_transactions_bad.csv` directly. It is passed to `ledger load` only.
