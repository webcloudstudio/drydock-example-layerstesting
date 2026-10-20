# FEATURE: Account Get

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Get one account with its transaction count and balance computed from the database. |
| Depends On  | DATABASE.md, FEATURE-AccountAdd.md, FEATURE-ValidateText.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md, FEATURE-InitSchema.md |
| Provides    | ledger account get |
| Consumes    | accounts.get, transactions.list |

## Purpose

Writes the account row for one code. The transaction count and balance are computed by query from
the stored transactions, never stored on the account.

## Command

`ledger account get <code>`

## Contract

- On success, standard output is the header `account,name,transactions,balance` followed by one row
  `<code>,<name>,<count>,<balance>`. `balance` is the signed sum of the account's transaction
  amounts in integer cents, written with exactly two decimals.
- A code that is well formed but absent exits 4 and writes nothing to standard output.
- A code that is malformed under FEATURE-ValidateText exits 3 and writes nothing to standard output.
  Validation precedes the lookup.
- The command is read-only. It changes no table.

## Database Interface

- `FEATURE-LEDGER-002` — read: read the account row - supplies: `account` - returns: `account`, `name`

## Programmatic Acceptance

=== AC acct-get-after-add ===
Intent: A newly added account reads back with zero transactions and a balance of 0.00.

import csv
import io
import os
import tempfile

from cli.testing import cli_runner

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

code, name = "CASH9", "Event Float"
assert cli_runner("account", "add", code, name)[0] == 0

exit_code, out, err = cli_runner("account", "get", code)
print(out)
print(err)
assert exit_code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["account", "name", "transactions", "balance"]
assert rows[1] == [code, name, "0", "0.00"]
=== END AC acct-get-after-add ===

=== AC acct-get-counts-and-balance ===
Intent: The transaction count and balance are computed from stored transactions, so a stored 500.00 transaction reads back as one transaction with balance 500.00.

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

exit_code, out, err = cli_runner("account", "get", code)
print(out)
print(err)
assert exit_code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[1] == [code, name, "1", "500.00"]
=== END AC acct-get-counts-and-balance ===

=== AC acct-get-absent ===
Intent: A well-formed code that does not exist exits 4 and writes nothing to standard output.

import os
import tempfile

from cli.testing import cli_runner

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

exit_code, out, err = cli_runner("account", "get", "NOSUCH")
print(err)
assert exit_code == 4
assert out == ""
=== END AC acct-get-absent ===

=== AC acct-get-malformed-code ===
Intent: A lowercase code is rejected by validation with exit 3 before any lookup, and writes nothing to standard output.

import os
import tempfile

from cli.testing import cli_runner

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
assert cli_runner("init")[0] == 0

exit_code, out, err = cli_runner("account", "get", "lower9")
print(err)
assert exit_code == 3
assert out == ""
=== END AC acct-get-malformed-code ===

## User Acceptance

- None.

## Guardrails

- Account get never writes to any table.
- The balance is never stored on the account row; it is computed from transactions on each read.
