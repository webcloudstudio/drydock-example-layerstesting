# FEATURE: Account Delete

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Delete an account that has no transactions, and refuse otherwise. |
| Depends On  | DATABASE.md, FEATURE-CommandTransaction.md, FEATURE-ValidateText.md, FEATURE-AccountGet.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md |
| Provides    | ledger account delete |
| Consumes    | accounts.get, accounts.delete, transactions.list |

## Purpose

Deletes one account row when no transaction refers to it.

## Command

`ledger account delete <code>`

## Contract

- An absent code exits 4 and changes nothing.
- An account with one or more transactions is refused with exit 3 and changes nothing.
- On success, standard output is the header `deleted` followed by the row `<code>`.
- Any failure writes nothing to standard output and one diagnostic line to standard error.
- The transaction check runs before the delete operation. The command runs as one transaction
  through FEATURE-CommandTransaction.

## Database Interface

- `FEATURE-LEDGER-002` — read: confirm the account exists - supplies: `account` - returns: `account`
- `FEATURE-LEDGER-005` — write: delete the account row - supplies: `account` - returns: `account`

## Programmatic Acceptance

=== AC acct-delete-empty ===
Intent: Deleting an account with no transactions writes the deleted header and code, and the account is then absent.

import csv
import io
import os
import tempfile

from cli.testing import cli_runner

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

code = "CASH9"
assert cli_runner("account", "add", code, "Event Float")[0] == 0

exit_code, out, err = cli_runner("account", "delete", code)
print(out)
print(err)
assert exit_code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows == [["deleted"], [code]]

exit_code, out, err = cli_runner("account", "get", code)
assert exit_code == 4
assert out == ""
=== END AC acct-delete-empty ===

=== AC acct-delete-refused-with-transactions ===
Intent: An account with a stored transaction is refused with exit 3, prints nothing, and remains present with its transaction count unchanged.

import csv
import io
import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

code, name = "DRAWER1", "Front Drawer"
assert cli_runner("account", "add", code, name)[0] == 0
with db_session(dsn) as db:
    db.categories.create(category="SALES", description="Sales receipts")
    db.transactions.create(txn_id=1, date="2026-01-02", account=code, category="SALES", amount=50000, memo="")

exit_code, out, err = cli_runner("account", "delete", code)
print(err)
assert exit_code == 3
assert out == ""

exit_code, out, err = cli_runner("account", "get", code)
assert exit_code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[1] == [code, name, "1", "500.00"]
=== END AC acct-delete-refused-with-transactions ===

=== AC acct-delete-absent ===
Intent: Deleting an absent account exits 4 and prints nothing.

import os
import tempfile

from cli.testing import cli_runner

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

exit_code, out, err = cli_runner("account", "delete", "NOSUCH")
print(err)
assert exit_code == 4
assert out == ""
=== END AC acct-delete-absent ===

=== AC acct-delete-twice ===
Intent: Deleting the same account a second time exits 4, because the account is already absent.

import os
import tempfile

from cli.testing import cli_runner

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

code = "CASH9"
assert cli_runner("account", "add", code, "Event Float")[0] == 0
assert cli_runner("account", "delete", code)[0] == 0

exit_code, out, err = cli_runner("account", "delete", code)
print(err)
assert exit_code == 4
assert out == ""
=== END AC acct-delete-twice ===

## User Acceptance

- None.

## Guardrails

- A refused delete changes no row.
- An account row is never removed while any transaction names its code.
