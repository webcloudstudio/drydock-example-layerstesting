# FEATURE: Account Add

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger account add <code> <name>` and the shared `account_row` helper. |
| Depends On | FEATURE-CliEntry.md, FEATURE-Validation.md, DATABASE.md |
| Provides | ledger account add, ledger_core.accounts |
| Consumes | ledger_core.validation, ledger_core.money, cli.registry |

## Purpose

Create one account and print its row. The module `ledger_core.accounts` also exports the helper the
other account commands use to build an account row from live data.

## Behavior

1. `ledger account add <code> <name>` takes exactly two arguments; other counts exit 2.
2. Validate the code (1 to 12 characters of `A-Z0-9`) and the name (1 to 40 characters, no comma or
   newline). A violation exits 3.
3. A code that is already stored exits 3 and leaves the stored account unchanged.
4. Insert the account, then print CSV: the header `account,name,transactions,balance` and one row
   with the new account, its name, `0` transactions, and balance `0.00`.
5. A failing command writes nothing to standard output.

## Interface

`ledger_core.accounts.account_row(db, code)` returns `None` when the account is absent, otherwise
the tuple `(account, name, transactions, balance_cents)` where `transactions` is the number of that
account's stored transactions and `balance_cents` is the integer sum of their amounts. Both are
computed from the database on every call. Formatting the balance as text is done by
`ledger_core.money.format_cents` in the command, not in the helper.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: get an account by code - supplies: `account` - returns: `account`, `name`
- `FEATURE-ACCOUNT-001` — write: create an account - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-TXN-005` — read: list an account's transactions to count and sum them - supplies: `account` - returns: `amount`

## Programmatic Acceptance

=== AC account-add-success ===
Intent: adding a new account exits 0, prints the header and one row with zero transactions and a zero balance, and the account reads back from the store.
Requires: executable=python3; scope=test

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZNA1"
name = "Add Probe"
with db_session() as db:
    code, out, err = cli_runner("account", "add", acct, name)
    print(out, err)
    assert code == 0
    parsed = list(csv.reader(io.StringIO(out)))
    assert parsed[0] == ["account", "name", "transactions", "balance"]
    assert parsed[1] == [acct, name, "0", "0.00"]
    assert len(parsed) == 2
    row = db.accounts.get(account=acct)
    assert row is not None
    got = row["name"] if isinstance(row, dict) else row.name
    assert got == name
=== END AC account-add-success ===

=== AC account-add-duplicate-rejected ===
Intent: adding a code that already exists exits 3, prints nothing, and leaves the stored name unchanged.
Requires: executable=python3; scope=test

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZNB1"
original = "Original Name"
with db_session() as db:
    code, out, err = cli_runner("account", "add", acct, original)
    assert code == 0
    code, out, err = cli_runner("account", "add", acct, "Different Name")
    assert code == 3
    assert out == ""
    row = db.accounts.get(account=acct)
    got = row["name"] if isinstance(row, dict) else row.name
    assert got == original
=== END AC account-add-duplicate-rejected ===

=== AC account-add-invalid-code ===
Intent: lowercase letters, a code longer than 12 characters, a bad character, and an empty code each exit 3 with no output and store no account.
Requires: executable=python3; scope=test

from cli.testing import cli_runner
from persistence.testing import db_session

bad_codes = ["zznc1", "ABCDEFGHIJKLM", "ZZ-NC", "ZZ NC", ""]
with db_session() as db:
    before = len(db.accounts.list())
    for bad in bad_codes:
        code, out, err = cli_runner("account", "add", bad, "Valid Name")
        assert code == 3, bad
        assert out == ""
    assert len(db.accounts.list()) == before
=== END AC account-add-invalid-code ===

=== AC account-add-invalid-name ===
Intent: an empty name, a name over 40 characters, and a name containing a comma each exit 3 with no output and store no account.
Requires: executable=python3; scope=test

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZND1"
bad_names = ["", "n" * 41, "has,comma"]
with db_session() as db:
    for bad in bad_names:
        code, out, err = cli_runner("account", "add", acct, bad)
        assert code == 3, bad
        assert out == ""
        assert db.accounts.get(account=acct) is None
=== END AC account-add-invalid-name ===

=== AC account-add-boundary-lengths ===
Intent: a 12-character code and a 40-character name are the largest accepted values and are stored whole.
Requires: executable=python3; scope=test

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "Z" * 12
name = "n" * 40
with db_session() as db:
    code, out, err = cli_runner("account", "add", acct, name)
    assert code == 0
    row = db.accounts.get(account=acct)
    assert row is not None
    got = row["name"] if isinstance(row, dict) else row.name
    assert got == name
=== END AC account-add-boundary-lengths ===

=== AC account-add-usage-errors ===
Intent: the wrong number of arguments is a usage error with exit 2 and no output.
Requires: executable=python3; scope=test

from cli.testing import cli_runner

for args in (("account", "add"), ("account", "add", "ZZNE1"), ("account", "add", "ZZNE1", "Name", "Extra")):
    code, out, err = cli_runner(*args)
    assert code == 2, args
    assert out == ""
=== END AC account-add-usage-errors ===

=== AC account-row-helper ===
Intent: account_row reports the live transaction count and the integer-cent balance computed from stored transactions, and None for an absent account.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from ledger_core.accounts import account_row

acct, cat = "ZZNF1", "ZZNFC"
name = "Helper Probe"
amounts = [10000, -2550, 1]
with db_session() as db:
    db.accounts.create(account=acct, name=name)
    db.categories.create(category=cat, description="Helper Category")
    for i, cents in enumerate(amounts):
        db.transactions.create(txn_id=930000000 + i, date="2026-03-01", account=acct,
                               category=cat, amount=cents, memo="")
    row = account_row(db, acct)
    assert row is not None
    assert tuple(row) == (acct, name, len(amounts), sum(amounts))
    assert account_row(db, "ZZNFNONE") is None
=== END AC account-row-helper ===

## User Acceptance

- None.

## Guardrails

- Validation completes before the insert; a rejected add changes nothing.
- The balance is integer cents in the helper and is formatted only for output.
- A failing command writes nothing to standard output.
