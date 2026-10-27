# FEATURE: Account Rename

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger account rename <code> <name>`, changing only an account's name and printing the updated row. |
| Depends On | FEATURE-AccountAdd.md, FEATURE-CliEntry.md, FEATURE-Validation.md, DATABASE.md |
| Provides | ledger account rename |
| Consumes | ledger_core.accounts, ledger_core.validation, cli.registry |

## Purpose

`ledger account rename <code> <name>` validates the new name, updates only the name column, and prints the header row and the updated account row `account,name,transactions,balance`.

## Behavior

- Exactly two arguments are required; otherwise exit 2.
- Name validation (1 to 40 characters, no comma, no newline) happens first; a violation exits 3 and changes nothing.
- An absent code exits 4 and changes nothing.
- On success only `name` changes; the transaction count and balance in the output are computed live.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: check the account exists - supplies: `account` - returns: `account`, `name`
- `FEATURE-ACCOUNT-003` — write: rename an account - supplies: `account`, `name` - returns: `account`, `name`

## Programmatic Acceptance

=== AC account-rename-success ===
Intent: Renaming prints the updated row and a separate read shows the new name persisted.
Requires: executable=python3; scope=test

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

code, before, after = "ZZAR1", "Old Name", "New Name"
with db_session() as db:
    db.accounts.create(account=code, name=before)
    rc, out, err = cli_runner("account", "rename", code, after)
    print(out)
    print(err)
    assert rc == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["account", "name", "transactions", "balance"]
    assert rows[1] == [code, after, str(0), "0.00"]
    back = db.accounts.get(account=code)
    assert back is not None
    name = back["name"] if isinstance(back, dict) else back.name
    assert name == after
=== END AC account-rename-success ===

=== AC account-rename-absent ===
Intent: Renaming an absent account exits 4 with no standard output and creates nothing.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

code = "ZZARNONE"
with db_session() as db:
    rc, out, err = cli_runner("account", "rename", code, "Any Name")
    print(err)
    assert rc == 4
    assert out == ""
    assert db.accounts.get(account=code) is None
=== END AC account-rename-absent ===

=== AC account-rename-invalid-name ===
Intent: A name containing a comma, an empty name, and an over-length name each exit 3 and leave the stored name unchanged.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

code, original = "ZZAR2", "Keep Me"
bad_names = ["has,comma", "", "x" * 41]
with db_session() as db:
    db.accounts.create(account=code, name=original)
    for bad in bad_names:
        rc, out, err = cli_runner("account", "rename", code, bad)
        print(err)
        assert rc == 3
        assert out == ""
        back = db.accounts.get(account=code)
        name = back["name"] if isinstance(back, dict) else back.name
        assert name == original
=== END AC account-rename-invalid-name ===

=== AC account-rename-usage ===
Intent: A wrong argument count is a usage error with exit 2 and no standard output.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    rc, out, err = cli_runner("account", "rename", "ZZAR3")
    assert rc == 2
    assert out == ""
=== END AC account-rename-usage ===

## User Acceptance

- None.

## Guardrails

- Only the name column changes; the code, transactions, and balance are untouched.
- Every input is validated before the first write.
- Failures write nothing to standard output.
