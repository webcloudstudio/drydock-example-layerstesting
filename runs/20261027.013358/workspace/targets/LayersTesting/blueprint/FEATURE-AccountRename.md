# FEATURE: Account Rename

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger account rename <code> <name>` changing only an account's name. |
| Depends On | FEATURE-AccountGet.md, FEATURE-Validation.md, DATABASE.md |
| Provides | ledger account rename |
| Consumes | ledger account get, ledgerlib.validation |

## Purpose

Rename an existing account and print its updated row.

## Interface

`ledger account rename <code> <name>`. Output is the header `account,name,transactions,balance` and the updated account row read back from storage.

## Behavior

1. `rename` with other than exactly two arguments is a usage error (exit 2).
2. `name` is 1 to 40 characters with no comma or newline, else exit 3 and the stored name is unchanged.
3. An absent code is not found (exit 4) and nothing is created.
4. Only the name changes; the transaction count and balance of the printed row are computed from stored transactions.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC acct-rename-success ===
Intent: Renaming prints the updated row, keeps the transaction count and balance, and the new name reads back from the store.

import csv
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZAR1"
cat = "ZZARC1"
old_name = "Rename Before"
new_name = "Rename After"
amount = 4250
with db_session() as db:
    db.accounts.create(account=acct, name=old_name)
    db.categories.create(category=cat, description="Rename Cat")
    db.transactions.create(txn_id=860001, date="2026-04-01", account=acct, category=cat, amount=amount, memo="m")
    expected_balance = f"{amount // 100}.{amount % 100:02d}"
    code, out, err = cli_runner("account", "rename", acct, new_name)
    print(out, err)
    assert code == 0
    parsed = list(csv.reader(out.splitlines()))
    assert parsed[0] == ["account", "name", "transactions", "balance"]
    assert parsed[1] == [acct, new_name, "1", expected_balance]
    row = db.accounts.get(account=acct)
    assert row is not None
    assert row.name == new_name
    assert db.transactions.get(txn_id=860001).amount == amount
=== END AC acct-rename-success ===

=== AC acct-rename-not-found ===
Intent: Renaming an absent account exits 4, prints nothing to standard output, and creates no account.

from cli.testing import cli_runner
from persistence.testing import db_session

missing = "ZZAR2"
with db_session() as db:
    assert db.accounts.get(account=missing) is None
    code, out, err = cli_runner("account", "rename", missing, "Some Name")
    print(out, err)
    assert code == 4
    assert out == ""
    assert db.accounts.get(account=missing) is None
=== END AC acct-rename-not-found ===

=== AC acct-rename-invalid-name ===
Intent: Empty, over-long, comma-containing and newline-containing names are rejected with exit 3 and the stored name is unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZAR3"
original = "Keep This Name"
bad_names = ["", "n" * 41, "has, comma", "has\nnewline"]
with db_session() as db:
    db.accounts.create(account=acct, name=original)
    for bad in bad_names:
        code, out, err = cli_runner("account", "rename", acct, bad)
        print(repr(bad), code, out, err)
        assert code == 3
        assert out == ""
        row = db.accounts.get(account=acct)
        assert row is not None
        assert row.name == original
=== END AC acct-rename-invalid-name ===

=== AC acct-rename-boundary-name ===
Intent: A 40-character name is the accepted maximum and is stored exactly.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZAR4"
new_name = "m" * 40
with db_session() as db:
    db.accounts.create(account=acct, name="Short")
    code, out, err = cli_runner("account", "rename", acct, new_name)
    print(out, err)
    assert code == 0
    row = db.accounts.get(account=acct)
    assert row is not None
    assert row.name == new_name
=== END AC acct-rename-boundary-name ===

=== AC acct-rename-usage ===
Intent: Wrong argument counts for rename are usage errors with exit 2 and change nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZAR5"
original = "Usage Name"
with db_session() as db:
    db.accounts.create(account=acct, name=original)
    for args in [
        ("account", "rename"),
        ("account", "rename", acct),
        ("account", "rename", acct, "New", "extra"),
    ]:
        code, out, err = cli_runner(*args)
        print(args, code, out, err)
        assert code == 2
        assert out == ""
    assert db.accounts.get(account=acct).name == original
=== END AC acct-rename-usage ===

## User Acceptance

- None.

## Guardrails

- Rename changes only the account name; no transaction row is touched.
- A rejected rename writes nothing.
- Only the generated persistence package touches the database.
