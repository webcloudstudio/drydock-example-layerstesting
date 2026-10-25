# FEATURE: Account Add

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger account add <code> <name>`, which creates one validated account. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-CliEntry.md, FEATURE-LedgerCore.md, FEATURE-Init.md, FEATURE-Count.md |
| Provides | ledger account add |
| Consumes | cli.main, format_amount, validate_code, validate_text |

## Purpose

Add a new place where the shop keeps cash. A new account has no transactions and a zero balance.

## Command Contract

`ledger account add <code> <name>` registers under the `account` command in the cli command table.

| Condition | Result |
|---|---|
| Valid code and name, code not in use | Exit 0. Stdout is `account,name,transactions,balance` then the new row with `0` transactions and balance `0.00`. |
| Wrong argument count | Exit 2, nothing on stdout. |
| Code not 1 to 12 characters of `A-Z0-9` | Exit 3, nothing stored. |
| Name empty, longer than 40 characters, or containing a comma or newline | Exit 3, nothing stored. |
| Code already exists | Exit 3, nothing stored. |

## Behavior

1. Validate the code and name with the `ledger-core` validators.
2. Confirm the code is not already stored.
3. Create the row, then print the account row. The transaction count and balance are computed from
   the database, never hard-coded, and formatted from integer cents with two decimal places.
4. A failing command writes one diagnostic line to standard error and nothing to standard output.

## Database Interface

- `FEATURE-ACCOUNT-003` — write: create an account - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-ACCOUNT-002` — read: detect an existing code - supplies: `account` - returns: `account`, `name`
- `FEATURE-TXN-002` — read: count the account's transactions and sum its balance - supplies: `account` - returns: `txn_id`, `amount`

## Programmatic Acceptance

=== AC account-add-valid ===
Intent: Adding a valid account prints its zero-balance row and the account reads back with the supplied name.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

code = "ADDOK1"
name = "Added Account"
rc, out, err = cli_runner("account", "add", code, name)
print(out)
print(err)
assert rc == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows == [["account", "name", "transactions", "balance"], [code, name, "0", "0.00"]]
with db_session() as db:
    got = db.accounts.get(account=code)
    assert got is not None
    assert got.name == name
=== END AC account-add-valid ===

=== AC account-add-boundaries ===
Intent: A 12-character code and a 40-character name are accepted.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

code = "ADDMAXCODE12"
name = "N" * 40
assert len(code) == 12
rc, out, err = cli_runner("account", "add", code, name)
print(out)
print(err)
assert rc == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[1][:2] == [code, name]
with db_session() as db:
    got = db.accounts.get(account=code)
    assert got is not None
    assert got.name == name
=== END AC account-add-boundaries ===

=== AC account-add-invalid-code ===
Intent: A code that is too long, lowercase, or contains a forbidden character is rejected with exit 3 and not stored.

from cli.testing import cli_runner
from persistence.testing import db_session

bad_codes = ["ADDBADCODE123X", "addlower", "ADD-DASH", "ADD SPACE"]
for code in bad_codes:
    rc, out, err = cli_runner("account", "add", code, "Some Name")
    print(code, out, err)
    assert rc == 3
    assert out == ""
with db_session() as db:
    for code in bad_codes:
        assert db.accounts.get(account=code) is None
=== END AC account-add-invalid-code ===

=== AC account-add-invalid-name ===
Intent: A name that is empty, longer than 40 characters, or holds a comma or newline is rejected with exit 3 and not stored.

from cli.testing import cli_runner
from persistence.testing import db_session

bad_names = ["", "N" * 41, "has,comma", "has\nnewline"]
for n, name in enumerate(bad_names, start=1):
    code = "ADDBN%d" % n
    rc, out, err = cli_runner("account", "add", code, name)
    print(code, out, err)
    assert rc == 3
    assert out == ""
with db_session() as db:
    for n in range(1, len(bad_names) + 1):
        assert db.accounts.get(account="ADDBN%d" % n) is None
=== END AC account-add-invalid-name ===

=== AC account-add-usage ===
Intent: Missing or extra arguments to account add are a usage error (exit 2) and store nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

code = "ADDUSE1"
rc, out, err = cli_runner("account", "add", code)
print(out, err)
assert rc == 2
assert out == ""
rc, out, err = cli_runner("account", "add", code, "Name", "extra")
print(out, err)
assert rc == 2
assert out == ""
rc, out, err = cli_runner("account", "add")
print(out, err)
assert rc == 2
assert out == ""
with db_session() as db:
    assert db.accounts.get(account=code) is None
=== END AC account-add-usage ===

## User Acceptance

- None.

## Guardrails

- The transaction count and balance in the printed row are computed from the database.
- Balances are integer cents formatted to two decimal places; no floating point is used.
- A rejected add changes nothing.
