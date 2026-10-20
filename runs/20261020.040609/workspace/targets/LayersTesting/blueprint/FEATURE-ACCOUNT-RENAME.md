# FEATURE: Account Rename

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | `account rename` updates an account's name and writes the updated row; an absent code exits 4. |
| Depends On  | FEATURE-ACCOUNT-GET.md, FEATURE-ATOMIC-COMMANDS.md, FEATURE-VALIDATE-TEXT.md, DATABASE.md |
| Provides    | ledger account rename <code> <name> |
| Consumes    | accounts.update, accounts.get |

## Purpose

`ledger account rename <code> <name>` changes the name of one existing account. The code and all
transactions are unchanged.

## Behavior

- The new name is validated before any database access.
- The command writes the updated account row.
- An absent code exits 4 and changes nothing.

## Database Interface

- `FEATURE-ACCOUNT-004` — write: rename an account - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-ACCOUNT-002` — read: retrieve an account by code - supplies: `account` - returns: `account`, `name`

## Programmatic Acceptance

=== AC account-rename-round-trip ===
# Intent: `account rename` changes only the name and the new name is readable back through the database.

import csv
import io
import os
import sys
import tempfile
from pathlib import Path

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = str(Path(tempfile.mkdtemp()) / "ledger.db")
os.environ["DATABASE_URL"] = dsn

account_code = "CASH9"
original_name = "Event Float"
new_name = "Event Cash Box"

exit_code, out, err = cli_runner("init")
assert exit_code == 0

exit_code, out, err = cli_runner("account", "add", account_code, original_name)
assert exit_code == 0

exit_code, out, err = cli_runner("account", "rename", account_code, new_name)
print(out)
print(err, file=sys.stderr)
assert exit_code == 0

rows = list(csv.DictReader(io.StringIO(out)))
assert len(rows) == 1
assert rows[0]["account"] == account_code
assert rows[0]["name"] == new_name

with db_session(dsn) as db:
    stored = db.accounts.get(account=account_code)
assert stored.name == new_name
=== END AC account-rename-round-trip ===

=== AC account-rename-absent ===
# Intent: Renaming an account whose code does not exist exits 4 and creates no account.

import os
import sys
import tempfile
from pathlib import Path

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = str(Path(tempfile.mkdtemp()) / "ledger.db")
os.environ["DATABASE_URL"] = dsn

missing_code = "NOSUCH"
new_name = "Ghost Account"

exit_code, out, err = cli_runner("init")
assert exit_code == 0

exit_code, out, err = cli_runner("account", "rename", missing_code, new_name)
print(out)
print(err, file=sys.stderr)
assert exit_code == 4

with db_session(dsn) as db:
    assert db.accounts.get(account=missing_code) is None
=== END AC account-rename-absent ===

## User Acceptance

- None.

## Guardrails

- A rename never changes an account code. Transactions keep referencing the same code.
