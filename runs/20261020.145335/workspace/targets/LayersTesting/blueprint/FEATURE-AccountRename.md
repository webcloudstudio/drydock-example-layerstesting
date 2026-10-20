# FEATURE: Account Rename

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Rename an account without changing its code, transactions, or balance. |
| Depends On  | DATABASE.md, FEATURE-CommandTransaction.md, FEATURE-ValidateText.md, FEATURE-AccountGet.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md |
| Provides    | ledger account rename |
| Consumes    | accounts.get, accounts.update |

## Purpose

Changes only the name of an existing account and writes the updated account row.

## Command

`ledger account rename <code> <name>`

## Contract

- The code must exist. An absent code exits 4 and changes nothing.
- The new name is validated by FEATURE-ValidateText as 1 to 40 characters with no comma or newline.
  An invalid name exits 3 and changes nothing.
- On success, standard output is the header `account,name,transactions,balance` followed by the
  updated row, with the transaction count and balance computed as in FEATURE-AccountGet.
- The command runs as one transaction through FEATURE-CommandTransaction.

## Database Interface

- `FEATURE-LEDGER-002` — read: confirm the account exists - supplies: `account` - returns: `account`, `name`
- `FEATURE-LEDGER-004` — write: store the new name - supplies: `account`, `name` - returns: `account`, `name`

## Programmatic Acceptance

=== AC acct-rename-round-trip ===
Intent: Renaming an empty account writes the updated row and the stored name reads back as the new name.

import csv
import io
import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

code, old_name, new_name = "CASH9", "Event Float", "Event Cash Box"
assert cli_runner("account", "add", code, old_name)[0] == 0

exit_code, out, err = cli_runner("account", "rename", code, new_name)
print(out)
print(err)
assert exit_code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["account", "name", "transactions", "balance"]
assert rows[1] == [code, new_name, "0", "0.00"]

with db_session(dsn) as db:
    stored = db.accounts.get(account=code)
assert stored.name == new_name
=== END AC acct-rename-round-trip ===

=== AC acct-rename-keeps-transactions ===
Intent: Renaming an account with a stored transaction leaves its transaction count and balance unchanged.

import csv
import io
import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

code, old_name, new_name = "DRAWER1", "Front Drawer", "Till One"
assert cli_runner("account", "add", code, old_name)[0] == 0
with db_session(dsn) as db:
    db.categories.create(category="SALES", description="Sales receipts")
    db.transactions.create(txn_id=1, date="2026-01-02", account=code, category="SALES", amount=50000, memo="")

exit_code, out, err = cli_runner("account", "rename", code, new_name)
print(err)
assert exit_code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[1] == [code, new_name, "1", "500.00"]
=== END AC acct-rename-keeps-transactions ===

=== AC acct-rename-absent ===
Intent: Renaming an absent account exits 4, prints nothing, and creates no account.

import os
import tempfile

from cli.testing import cli_runner

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

exit_code, out, err = cli_runner("account", "rename", "NOSUCH", "Anything")
print(err)
assert exit_code == 4
assert out == ""
assert cli_runner("account", "get", "NOSUCH")[0] == 4
=== END AC acct-rename-absent ===

=== AC acct-rename-invalid-name ===
Intent: An empty name and a name containing a comma are rejected with exit 3, and the original name is kept.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

code, name = "CASH9", "Event Float"
assert cli_runner("account", "add", code, name)[0] == 0

exit_code, out, err = cli_runner("account", "rename", code, "")
print(err)
assert exit_code == 3
assert out == ""

exit_code, out, err = cli_runner("account", "rename", code, "Float, Event")
print(err)
assert exit_code == 3
assert out == ""

with db_session(dsn) as db:
    stored = db.accounts.get(account=code)
assert stored.name == name
=== END AC acct-rename-invalid-name ===

=== AC acct-rename-name-bounds ===
Intent: A 40-character name is accepted and a 41-character name is rejected with exit 3.

import os
import tempfile

from cli.testing import cli_runner

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

code = "CASH9"
assert cli_runner("account", "add", code, "Event Float")[0] == 0

exit_code, out, err = cli_runner("account", "rename", code, "N" * 40)
print(err)
assert exit_code == 0

exit_code, out, err = cli_runner("account", "rename", code, "N" * 41)
print(err)
assert exit_code == 3
assert out == ""
=== END AC acct-rename-name-bounds ===

## User Acceptance

- None.

## Guardrails

- A rename never changes the account code, any transaction, or any balance.
- A rejected rename leaves the stored name exactly as it was.
