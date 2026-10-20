# FEATURE: Account Add

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Add an account with ledger account add, rejecting duplicates and invalid fields. |
| Depends On  | DATABASE.md, FEATURE-CommandTransaction.md, FEATURE-ValidateText.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md, FEATURE-InitSchema.md |
| Provides    | ledger account add |
| Consumes    | accounts.get, accounts.create |

## Purpose

Adds one account row. The new account starts with no transactions and a balance of `0.00`.

## Command

`ledger account add <code> <name>`

## Contract

- `code` is 1 to 12 characters from `A-Z` and `0-9`. Any other value is rejected with exit 3.
- `name` is 1 to 40 characters with no comma or newline. Any other value is rejected with exit 3.
- A code that already exists is rejected with exit 3 and changes nothing.
- On success, standard output is the header `account,name,transactions,balance` followed by the
  row `<code>,<name>,0,0.00`.
- Any failure writes nothing to standard output and one diagnostic line to standard error.
- The command runs as one transaction through FEATURE-CommandTransaction.

## Database Interface

- `FEATURE-LEDGER-002` — read: check whether the code already exists - supplies: `account` - returns: `account`
- `FEATURE-LEDGER-003` — write: create the account row - supplies: `account`, `name` - returns: `account`, `name`

## Programmatic Acceptance

=== AC acct-add-round-trip ===
Intent: A valid add writes the account row, prints it in the CSV contract, and the stored row reads back with the same name.

import csv
import io
import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

code, name = "CASH9", "Event Float"
exit_code, out, err = cli_runner("account", "add", code, name)
print(out)
print(err)
assert exit_code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["account", "name", "transactions", "balance"]
assert rows[1] == [code, name, "0", "0.00"]

with db_session(dsn) as db:
    stored = db.accounts.get(account=code)
assert stored.account == code
assert stored.name == name
=== END AC acct-add-round-trip ===

=== AC acct-add-duplicate ===
Intent: Adding a code that already exists exits 3, prints nothing, and leaves the original name unchanged.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

code, name = "CASH9", "Event Float"
assert cli_runner("account", "add", code, name)[0] == 0

exit_code, out, err = cli_runner("account", "add", code, "Other Name")
print(err)
assert exit_code == 3
assert out == ""

with db_session(dsn) as db:
    stored = db.accounts.get(account=code)
assert stored.name == name
=== END AC acct-add-duplicate ===

=== AC acct-add-code-bounds ===
Intent: A 12-character code is accepted; a 13-character code and a lowercase code are rejected with exit 3 and print nothing.

import os
import tempfile

from cli.testing import cli_runner

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

code_max = "A" * 12
code_over = "A" * 13
exit_code, out, err = cli_runner("account", "add", code_max, "Max Code")
assert exit_code == 0

exit_code, out, err = cli_runner("account", "add", code_over, "Over Code")
print(err)
assert exit_code == 3
assert out == ""

exit_code, out, err = cli_runner("account", "add", "lower9", "Lower Code")
print(err)
assert exit_code == 3
assert out == ""
=== END AC acct-add-code-bounds ===

=== AC acct-add-name-bounds ===
Intent: A 40-character name is accepted; a 41-character name and a name containing a comma are rejected with exit 3.

import os
import tempfile

from cli.testing import cli_runner

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

name_max = "N" * 40
name_over = "N" * 41
exit_code, out, err = cli_runner("account", "add", "NAMEMAX", name_max)
assert exit_code == 0

exit_code, out, err = cli_runner("account", "add", "NAMEOVER", name_over)
print(err)
assert exit_code == 3
assert out == ""

exit_code, out, err = cli_runner("account", "add", "COMMA1", "Float, Event")
print(err)
assert exit_code == 3
assert out == ""
=== END AC acct-add-name-bounds ===

## User Acceptance

- None.

## Guardrails

- A failed add changes no row and prints nothing to standard output.
- The new account's balance is `0.00` and its transaction count is `0`; neither is accepted from input.
