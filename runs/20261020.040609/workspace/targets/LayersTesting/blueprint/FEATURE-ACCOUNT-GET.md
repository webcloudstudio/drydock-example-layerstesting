# FEATURE: Account Get

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | `account get` writes the account row for a code; an absent code exits 4. |
| Depends On  | FEATURE-ACCOUNT-ADD.md, DATABASE.md |
| Provides    | ledger account get <code> |
| Consumes    | accounts.get |

## Purpose

`ledger account get <code>` reads one account from the database and writes it as a single account row.

## Behavior

- The output is the account row: `account,name,transactions,balance`.
- The transaction count and balance are computed from the database at read time.
- An absent code exits 4 and writes nothing to standard output.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: retrieve an account by code - supplies: `account` - returns: `account`, `name`

## Programmatic Acceptance

=== AC account-get-present ===
# Intent: `account get` for an existing code writes that account's row and exits 0.

import csv
import io
import os
import sys
import tempfile
from pathlib import Path

from cli.testing import cli_runner

dsn = str(Path(tempfile.mkdtemp()) / "ledger.db")
os.environ["DATABASE_URL"] = dsn

account_code = "CASH9"
account_name = "Event Float"

exit_code, out, err = cli_runner("init")
assert exit_code == 0

exit_code, out, err = cli_runner("account", "add", account_code, account_name)
assert exit_code == 0

exit_code, out, err = cli_runner("account", "get", account_code)
print(out)
print(err, file=sys.stderr)
assert exit_code == 0

rows = list(csv.DictReader(io.StringIO(out)))
assert len(rows) == 1
assert rows[0]["account"] == account_code
assert rows[0]["name"] == account_name
=== END AC account-get-present ===

=== AC account-get-absent ===
# Intent: `account get` for a code that does not exist exits 4.

import os
import sys
import tempfile
from pathlib import Path

from cli.testing import cli_runner

dsn = str(Path(tempfile.mkdtemp()) / "ledger.db")
os.environ["DATABASE_URL"] = dsn

missing_code = "NOSUCH"

exit_code, out, err = cli_runner("init")
assert exit_code == 0

exit_code, out, err = cli_runner("account", "get", missing_code)
print(out)
print(err, file=sys.stderr)
assert exit_code == 4
=== END AC account-get-absent ===

## User Acceptance

- None.

## Guardrails

- A get never creates an account. An absent code stays absent.
