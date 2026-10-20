# FEATURE: Load Transactions

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Load transactions from a CSV file atomically, keeping each txn_id from the file. |
| Depends On  | DATABASE.md, FEATURE-LoadAccounts.md, FEATURE-LoadCategories.md, FEATURE-NonNegativeBalance.md, FEATURE-ValidateText.md, FEATURE-ValidateAmount.md, FEATURE-ValidateDate.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md |
| Provides    | ledger load transactions |
| Consumes    | accounts.get, categories.get, transactions.create |

## Purpose

Loads `transactions` from a CSV file. The file either stores every row or stores none. Each row
keeps the `txn_id` written in the file, so a loaded transaction is never renumbered.

## Command

`ledger load transactions <csv>`

## Contract

- The header must match exactly `txn_id,date,account,category,amount,memo`, in that order. A file
  whose header differs, reorders, or omits a column is rejected with exit 3 and stores no rows.
- `txn_id` is an integer and must be unique among existing transactions and within the file. A
  duplicate is rejected with exit 3.
- `date` is validated by FEATURE-ValidateDate. `memo` is validated by FEATURE-ValidateText.
- `amount` is parsed to integer cents by FEATURE-ValidateAmount. No floating point is used.
- `account` must name an existing account and `category` an existing category. An unknown value
  is rejected with exit 3.
- After every row is staged, and before commit, FEATURE-NonNegativeBalance checks each account.
  Any negative balance rejects the file with exit 3.
- A file that cannot be read exits 1 and writes nothing to standard output.
- Any rejected row rejects the whole file. The command runs as one transaction through
  FEATURE-CommandTransaction.
- On success, standard output is `table,loaded` then `transactions,<rows>`.

## Database Interface

- `FEATURE-LEDGER-002` — read: look up each row's account - supplies: `account` - returns: `account`
- `FEATURE-LEDGER-007` — read: look up each row's category - supplies: `category` - returns: `category`
- `FEATURE-LEDGER-011` — write: insert each accepted row - supplies: `txn_id`, `date`, `account`, `category`, `amount`, `memo` - returns: `txn_id`

## Programmatic Acceptance

=== AC load-txn-round-trip ===
Intent: A valid file stores every row with its own txn_id and amount in integer cents, and reports the loaded count.

import csv
import io
import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

with db_session(dsn) as db:
    db.accounts.create(account="DRAWER1", name="Front Drawer")
    db.categories.create(category="SALES", description="Sales receipts")

csv_path = os.path.join(os.path.dirname(dsn), "txns.csv")
with open(csv_path, "w") as handle:
    handle.write("txn_id,date,account,category,amount,memo\n")
    handle.write("7,2026-01-02,DRAWER1,SALES,155.26,sales day 1\n")
    handle.write("8,2026-01-02,DRAWER1,SALES,-12.50,refund\n")

exit_code, out, err = cli_runner("load", "transactions", csv_path)
print(out)
print(err)
assert exit_code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["table", "loaded"]
assert rows[1] == ["transactions", "2"]

with db_session(dsn) as db:
    stored = sorted((row.txn_id, row.amount) for row in db.transactions.list())
assert stored == [(7, 15526), (8, -1250)]
=== END AC load-txn-round-trip ===

=== AC load-txn-header-mismatch ===
Intent: A file whose header reorders the transaction columns is rejected with exit 3 and stores no rows.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

with db_session(dsn) as db:
    db.accounts.create(account="DRAWER1", name="Front Drawer")
    db.categories.create(category="SALES", description="Sales receipts")
    before = len(db.transactions.list())

csv_path = os.path.join(os.path.dirname(dsn), "reordered.csv")
with open(csv_path, "w") as handle:
    handle.write("txn_id,account,date,category,amount,memo\n")
    handle.write("7,DRAWER1,2026-01-02,SALES,155.26,sales day 1\n")

exit_code, out, err = cli_runner("load", "transactions", csv_path)
print(err)
assert exit_code == 3
assert out == ""

with db_session(dsn) as db:
    after = len(db.transactions.list())
assert after == before
=== END AC load-txn-header-mismatch ===

=== AC load-txn-unknown-account-rejects-file ===
Intent: One row naming an unknown account rejects the whole file, so the valid rows before it are not stored.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

with db_session(dsn) as db:
    db.accounts.create(account="DRAWER1", name="Front Drawer")
    db.categories.create(category="SALES", description="Sales receipts")
    before = len(db.transactions.list())

csv_path = os.path.join(os.path.dirname(dsn), "unknown.csv")
with open(csv_path, "w") as handle:
    handle.write("txn_id,date,account,category,amount,memo\n")
    handle.write("7,2026-01-02,DRAWER1,SALES,10.00,good row\n")
    handle.write("8,2026-01-02,NOSUCH,SALES,10.00,unknown account\n")

exit_code, out, err = cli_runner("load", "transactions", csv_path)
print(err)
assert exit_code == 3
assert out == ""

with db_session(dsn) as db:
    after = len(db.transactions.list())
assert after == before
=== END AC load-txn-unknown-account-rejects-file ===

=== AC load-txn-duplicate-id ===
Intent: A file whose txn_id already exists in the store is rejected with exit 3 and changes nothing.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

with db_session(dsn) as db:
    db.accounts.create(account="DRAWER1", name="Front Drawer")
    db.categories.create(category="SALES", description="Sales receipts")
    db.transactions.create(txn_id=7, date="2026-01-01", account="DRAWER1", category="SALES", amount=100, memo="")
    before = len(db.transactions.list())

csv_path = os.path.join(os.path.dirname(dsn), "duplicate.csv")
with open(csv_path, "w") as handle:
    handle.write("txn_id,date,account,category,amount,memo\n")
    handle.write("7,2026-01-02,DRAWER1,SALES,10.00,clash\n")

exit_code, out, err = cli_runner("load", "transactions", csv_path)
print(err)
assert exit_code == 3
assert out == ""

with db_session(dsn) as db:
    after = len(db.transactions.list())
assert after == before
=== END AC load-txn-duplicate-id ===

=== AC load-txn-negative-balance ===
Intent: A file that would leave an account below zero is rejected with exit 3 and stores no rows.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

with db_session(dsn) as db:
    db.accounts.create(account="PETTY", name="Petty Cash")
    db.categories.create(category="SUPPLY", description="Supplies")
    before = len(db.transactions.list())

csv_path = os.path.join(os.path.dirname(dsn), "overdraw.csv")
with open(csv_path, "w") as handle:
    handle.write("txn_id,date,account,category,amount,memo\n")
    handle.write("9,2026-01-03,PETTY,SUPPLY,-1.00,overdraw\n")

exit_code, out, err = cli_runner("load", "transactions", csv_path)
print(err)
assert exit_code == 3
assert out == ""

with db_session(dsn) as db:
    after = len(db.transactions.list())
assert after == before
=== END AC load-txn-negative-balance ===

=== AC load-txn-unreadable-file ===
Intent: A file path that does not exist exits 1 and writes nothing to standard output.

import os
import tempfile

from cli.testing import cli_runner

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

missing = os.path.join(os.path.dirname(dsn), "missing.csv")
exit_code, out, err = cli_runner("load", "transactions", missing)
print(err)
assert exit_code == 1
assert out == ""
=== END AC load-txn-unreadable-file ===

## User Acceptance

- None.

## Guardrails

- A file with any rejected row stores no rows from that file.
- Amounts are parsed to integer cents. No floating-point value reaches the database.
- Application code reaches the database only through the declared repository operations.
