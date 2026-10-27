# FEATURE: Account Rename

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger account rename`, which changes only an account's name and writes the updated account row. |
| Depends On | FEATURE-AccountGet.md, FEATURE-LedgerCli.md, DATABASE.md |
| Provides | ledger account rename |
| Consumes | ledger, accounts |

## Purpose

Let the shop correct the display name of an existing account without touching its code or its transactions.

## Trigger

`ledger account rename <code> <name>` invoked from the command line.

## Sequence

1. Require exactly two arguments after `rename`; otherwise raise the shared usage error (exit 2).
2. Look up the account by code. An absent code exits 4. This check runs before the name is validated.
3. Validate the name: 1 to 40 characters, no comma, no newline. An invalid name exits 3 and changes nothing.
4. Update only the name through the persistence library.
5. Compute the account's transaction count and balance in integer cents from its stored transactions.
6. Write the header `account,name,transactions,balance` and the updated row, balance with exactly two decimals.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: look up the account by code - supplies: `account` - returns: `account`, `name`
- `FEATURE-ACCOUNT-003` — write: rename the account - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-TXN-005` — read: list the account's transactions to count and sum them - supplies: `account` - returns: `txn_id`, `amount`

## Behavior Rules

- Only the name changes; the code and transactions are untouched.
- A failing command writes nothing to standard output and one diagnostic line to standard error.
- Money is integer cents at every layer; no floating point.

## Programmatic Acceptance

=== AC acct-rename-success ===
Intent: Renaming an existing account exits 0, writes the account row with the new name, and a separate read shows the stored name changed.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

code = "ZRN1"
old_name = "Old Cash Box"
new_name = "Event Cash Box"
with db_session() as db:
    db.accounts.create(account=code, name=old_name)
    exit_code, out, err = cli_runner("account", "rename", code, new_name)
    print(exit_code, out, err)
    assert exit_code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["account", "name", "transactions", "balance"]
    assert rows[1] == [code, new_name, "0", "0.00"]
    back = db.accounts.get(account=code)
    assert back is not None
    assert back.name == new_name
=== END AC acct-rename-success ===

=== AC acct-rename-only-name ===
Intent: Rename changes only the name; the account keeps its transaction and the output reports its count and balance derived from the stored amount.

import csv
import io
from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

code = "ZRN2"
cat = "ZRN2"
txn_id = 910001
cents = 1250
new_name = "Renamed Account"
with db_session() as db:
    db.accounts.create(account=code, name="Before")
    db.categories.create(category=cat, description="Rename Category")
    db.transactions.create(
        txn_id=txn_id, date="2026-05-01", account=code, category=cat, amount=cents, memo="keep"
    )
    exit_code, out, err = cli_runner("account", "rename", code, new_name)
    print(exit_code, out, err)
    assert exit_code == 0
    rows = list(csv.reader(io.StringIO(out)))
    expected_balance = f"{Decimal(cents) / 100:.2f}"
    assert rows[1] == [code, new_name, "1", expected_balance]
    txn = db.transactions.get(txn_id=txn_id)
    assert txn is not None
    assert txn.amount == cents
    assert txn.account == code
    assert txn.memo == "keep"
=== END AC acct-rename-only-name ===

=== AC acct-rename-absent ===
Intent: Renaming an account that does not exist exits 4, writes nothing to standard output, and creates no account.

from persistence.testing import db_session
from cli.testing import cli_runner

code = "ZRNNONE"
with db_session() as db:
    assert db.accounts.get(account=code) is None
    exit_code, out, err = cli_runner("account", "rename", code, "Ghost")
    print(exit_code, out, err)
    assert exit_code == 4
    assert out == ""
    assert db.accounts.get(account=code) is None
=== END AC acct-rename-absent ===

=== AC acct-rename-invalid-name ===
Intent: A name that is too long or contains a comma is rejected with exit 3, nothing on standard output, and the stored name is unchanged.

from persistence.testing import db_session
from cli.testing import cli_runner

code = "ZRN3"
original = "Original Name"
too_long = "N" * 41
with_comma = "Left,Right"
with db_session() as db:
    db.accounts.create(account=code, name=original)
    for bad in (too_long, with_comma):
        exit_code, out, err = cli_runner("account", "rename", code, bad)
        print(exit_code, out, err)
        assert exit_code == 3
        assert out == ""
        back = db.accounts.get(account=code)
        assert back is not None
        assert back.name == original
=== END AC acct-rename-invalid-name ===

=== AC acct-rename-absent-before-invalid ===
Intent: For an absent code with an invalid name the not-found check runs first, so the exit code is 4 rather than 3.

from persistence.testing import db_session
from cli.testing import cli_runner

code = "ZRNNONE2"
too_long = "N" * 41
with db_session() as db:
    assert db.accounts.get(account=code) is None
    exit_code, out, err = cli_runner("account", "rename", code, too_long)
    print(exit_code, out, err)
    assert exit_code == 4
    assert out == ""
=== END AC acct-rename-absent-before-invalid ===

## User Acceptance

- None.

## Guardrails

- Only the account name may change; the code and transactions are never altered by rename.
- Persistence is reached only through the generated persistence package.
- A rejected rename writes nothing to the database.
