# FEATURE: Account Rename

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Implements `ledger account rename <code> <name>` changing only an account's name. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-AccountAdd.md, FEATURE-Validation.md, FEATURE-CsvOutput.md, FEATURE-ErrorContract.md |
| Provides | ledger account rename |
| Consumes | ledger.register_command, persistence.open_database, validation.check_text, csv_output.write_rows, ledger_errors.NotFound, ledger_errors.Rejected |

## Purpose

`ledger account rename <code> <name>` changes the stored name of an existing account and prints the updated account row.

## Behavior

- Arguments: exactly a code and a new name; any other count is a usage error (exit 2).
- `name` is 1 to 40 characters with no comma or newline; otherwise exit 3 and nothing changes.
- An absent code exits 4 with nothing on standard output.
- Only the name changes. The output is `account,name,transactions,balance` then the updated row with its current transaction count and balance.
- Renaming to the current name succeeds and returns the unchanged row.

## Database Interface

- `FEATURE-ACCOUNT-004` — write: rename an account - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-ACCOUNT-002` — read: confirm the account exists - supplies: `account` - returns: `account`, `name`
- `FEATURE-TXN-003` — read: list the account's transactions for count and balance - supplies: `account` - returns: `txn_id`, `account`, `amount`

## Programmatic Acceptance

=== AC account-rename-success ===
Intent: Renaming prints the updated row, persists the new name and keeps the code and transactions.

import csv
import io
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct, cat = "ZAR1A", "ZAR1C"
old_name, new_name = "Old Name", "New Name"
cents = 1999
with db_session() as db:
    db.accounts.create(account=acct, name=old_name)
    db.categories.create(category=cat, description="Rename test")
    db.transactions.create(txn_id=930001, date="2026-05-01", account=acct, category=cat, amount=cents, memo="")
    code, out, err = cli_runner("account", "rename", acct, new_name)
    print(out, err)
    assert code == 0
    assert list(csv.reader(io.StringIO(out))) == [
        ["account", "name", "transactions", "balance"],
        [acct, new_name, "1", f"{Decimal(cents).scaleb(-2):.2f}"],
    ]
    assert db.accounts.get(account=acct).name == new_name
    assert db.transactions.get(txn_id=930001).amount == cents
=== END AC account-rename-success ===

=== AC account-rename-same-name ===
Intent: Renaming to the current name succeeds and returns the unchanged row.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZAR2A"
name = "Same Name"
with db_session() as db:
    db.accounts.create(account=acct, name=name)
    code, out, err = cli_runner("account", "rename", acct, name)
    print(out, err)
    assert code == 0
    assert list(csv.reader(io.StringIO(out))) == [
        ["account", "name", "transactions", "balance"],
        [acct, name, "0", "0.00"],
    ]
    assert db.accounts.get(account=acct).name == name
=== END AC account-rename-same-name ===

=== AC account-rename-absent ===
Intent: Renaming an absent account exits 4 with nothing on standard output and creates nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

absent = "ZAR3NONE"
with db_session() as db:
    before = len(db.accounts.list())
    code, out, err = cli_runner("account", "rename", absent, "Whatever")
    print(code, out, err)
    assert code == 4
    assert out == ""
    assert db.accounts.get(account=absent) is None
    assert len(db.accounts.list()) == before
=== END AC account-rename-absent ===

=== AC account-rename-invalid-name ===
Intent: Invalid names exit 3 and leave the stored name unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZAR4A"
name = "Keep Me"
with db_session() as db:
    db.accounts.create(account=acct, name=name)
    for bad in ("", "N" * 41, "has,comma"):
        code, out, err = cli_runner("account", "rename", acct, bad)
        print(repr(bad), code, out, err)
        assert code == 3
        assert out == ""
        assert db.accounts.get(account=acct).name == name
=== END AC account-rename-invalid-name ===

=== AC account-rename-wrong-argument-count ===
Intent: A wrong argument count is a usage error with exit 2.

from cli.testing import cli_runner

for args in (("account", "rename"), ("account", "rename", "ZAR5A"), ("account", "rename", "ZAR5A", "Name", "extra")):
    code, out, err = cli_runner(*args)
    print(args, code, out, err)
    assert code == 2
    assert out == ""
=== END AC account-rename-wrong-argument-count ===

## User Acceptance

- None.

## Guardrails

- Only the account name changes; the code and transactions are untouched.
- A failing command writes nothing to standard output and nothing to the database.
- Diagnostics never include a DSN or credential.
