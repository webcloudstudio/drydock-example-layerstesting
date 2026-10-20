# FEATURE: Account Add

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | `account add` stores a new account with zero transactions and a zero balance; a duplicate code exits 3. |
| Depends On  | FEATURE-ATOMIC-COMMANDS.md, FEATURE-VALIDATE-CODE.md, FEATURE-VALIDATE-TEXT.md, DATABASE.md |
| Provides    | ledger account add <code> <name> |
| Consumes    | accounts.create, accounts.get |

## Purpose

`ledger account add <code> <name>` creates one account. The command is one transaction. The output
is the new account row in the `account,name,transactions,balance` format.

## Behavior

- The code and name are validated before any database access.
- A new account has zero transactions and a balance of `0.00`.
- A code that already exists is rejected with exit 3 and changes nothing.

## Database Interface

- `FEATURE-ACCOUNT-001` — write: create an account - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-ACCOUNT-002` — read: retrieve an account by code - supplies: `account` - returns: `account`, `name`

## Programmatic Acceptance

=== AC account-add-round-trip ===
# Intent: `account add` stores the account, reports zero transactions and a zero balance, and is readable back through the database.

import csv
import io
import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = str(Path(tempfile.mkdtemp()) / "ledger.db")
os.environ["DATABASE_URL"] = dsn

account_code = "CASH9"
account_name = "Event Float"

exit_code, out, err = cli_runner("init")
assert exit_code == 0

exit_code, out, err = cli_runner("account", "add", account_code, account_name)
print(out)
print(err, file=sys.stderr)
assert exit_code == 0

rows = list(csv.DictReader(io.StringIO(out)))
assert len(rows) == 1
assert rows[0]["account"] == account_code
assert rows[0]["name"] == account_name
assert int(rows[0]["transactions"]) == 0
assert Decimal(rows[0]["balance"]) == Decimal(0)

with db_session(dsn) as db:
    stored = db.accounts.get(account=account_code)
assert stored is not None
assert stored.name == account_name
=== END AC account-add-round-trip ===

=== AC account-add-duplicate ===
# Intent: Adding an account whose code already exists exits 3 and leaves the stored name unchanged.

import os
import sys
import tempfile
from pathlib import Path

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = str(Path(tempfile.mkdtemp()) / "ledger.db")
os.environ["DATABASE_URL"] = dsn

account_code = "CASH9"
account_name = "Event Float"
other_name = "Other Float"

exit_code, out, err = cli_runner("init")
assert exit_code == 0

exit_code, out, err = cli_runner("account", "add", account_code, account_name)
assert exit_code == 0

exit_code, out, err = cli_runner("account", "add", account_code, other_name)
print(out)
print(err, file=sys.stderr)
assert exit_code == 3

with db_session(dsn) as db:
    stored = db.accounts.get(account=account_code)
assert stored.name == account_name
=== END AC account-add-duplicate ===

## User Acceptance

- None.

## Guardrails

- A new account's balance is never stored. It is derived from transactions and is zero at creation.
