# FEATURE: Load Accounts

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Loads accounts from a CSV file, validating every row before commit. |
| Depends On  | FEATURE-NONNEGATIVE-BALANCE.md, FEATURE-VALIDATE-CODE.md, FEATURE-VALIDATE-TEXT.md, FEATURE-EXIT-CODES.md, FEATURE-TEST-RUNNER.md, DATABASE.md |
| Provides    | ledger load accounts <csv> |

## Purpose

`ledger load accounts <csv>` reads a file whose header is `account,name`, validates each row's
code and name, and inserts every row in one transaction. Output is `table,loaded` then
`accounts,<rows>`. A row that fails validation or duplicates an existing key rejects the whole
file with exit 3.

## Database Interface

- `FEATURE-ACCOUNT-001` — write: create an account from a loaded row - supplies: `account`, `name` - returns: `account`, `name`

## Programmatic Acceptance

=== AC load-accounts-valid-file ===
Intent: A valid accounts file loads every row and writes table,loaded then accounts,<rows>.

import os
import tempfile
from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
accounts = os.path.join(work, "accounts.csv")
with open(accounts, "w") as handle:
    handle.write("account,name\nDRAWER1,Front Drawer\nSAFE,Store Safe\n")
row_count = 2

assert cli_runner("init")[0] == 0
code, out, err = cli_runner("load", "accounts", accounts)
assert code == 0
lines = out.splitlines()
assert lines[0] == "table,loaded"
assert lines[1].split(",") == ["accounts", str(row_count)]
assert cli_runner("count")[1].splitlines()[1].split(",") == ["accounts", str(row_count)]
=== END AC load-accounts-valid-file ===

=== AC load-accounts-rows-readable ===
Intent: Each loaded account reads back through account get with the name it was loaded with.

import os
import tempfile
from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
accounts = os.path.join(work, "accounts.csv")
with open(accounts, "w") as handle:
    handle.write("account,name\nDRAWER1,Front Drawer\n")
code_text = "DRAWER1"
name_text = "Front Drawer"

assert cli_runner("init")[0] == 0
assert cli_runner("load", "accounts", accounts)[0] == 0
code, out, err = cli_runner("account", "get", code_text)
assert code == 0
row = out.splitlines()[1].split(",")
assert row[0] == code_text
assert row[1] == name_text
=== END AC load-accounts-rows-readable ===

=== AC load-accounts-invalid-row-rejects-file ===
Intent: A file containing an invalid account code exits 3 and stores none of its rows.

import os
import tempfile
from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
accounts = os.path.join(work, "accounts.csv")
with open(accounts, "w") as handle:
    handle.write("account,name\nSAFE,Store Safe\nbad-code,Bad Row\n")
empty = 0

assert cli_runner("init")[0] == 0
code, out, err = cli_runner("load", "accounts", accounts)
assert code == 3
rows = int(cli_runner("count")[1].splitlines()[1].split(",")[1])
assert rows == empty
assert cli_runner("account", "get", "SAFE")[0] == 4
=== END AC load-accounts-invalid-row-rejects-file ===

=== AC load-accounts-duplicate-key-rejected ===
Intent: Loading an account code that already exists exits 3 and leaves the stored row unchanged.

import os
import tempfile
from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
accounts = os.path.join(work, "accounts.csv")
with open(accounts, "w") as handle:
    handle.write("account,name\nSAFE,Store Safe\n")

assert cli_runner("init")[0] == 0
assert cli_runner("load", "accounts", accounts)[0] == 0
before = cli_runner("count")[1]
assert cli_runner("load", "accounts", accounts)[0] == 3
assert cli_runner("count")[1] == before
=== END AC load-accounts-duplicate-key-rejected ===

## User Acceptance

- None.

## Guardrails

- The loader reads the file only through the `accounts` table operations; it never opens a driver.
- Validation of every row completes before the transaction commits.
