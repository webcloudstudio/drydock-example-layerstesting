# FEATURE: Account Add

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | The `ledger account add` command that creates a new account with zero transactions and a zero balance. |
| Depends On | FEATURE-LoadAccounts.md, FEATURE-LedgerCli.md, DATABASE.md |
| Provides | ledger account add |
| Consumes | ledger, accounts, transactions |

## Purpose

Register the `account` command group with its `add <code> <name>` subcommand.

## Behavior

- Exactly two arguments after `add`; any other count is a usage error, exit 2.
- The code follows the shared code rule and the name the shared name rule (1 to 40 characters, no
  comma or newline); a violation exits 3.
- A code that already exists exits 3 and leaves the stored row unchanged.
- Success stores the row and writes `account,name,transactions,balance` then the new row with `0`
  transactions and balance `0.00`. A failing command writes nothing to standard output.

## Database Interface

- `FEATURE-ACCOUNT-001` — write: store the new account - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-ACCOUNT-002` — read: detect a duplicate code - supplies: `account` - returns: `account`, `name`

## Programmatic Acceptance

=== AC account-add-success ===
Intent: Adding an account exits 0, writes the account header and the new row with zero transactions and balance 0.00, and the row is readable afterward.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

code_val = "ZQAD1"
name = "Event Float"
with db_session() as db:
    code, out, err = cli_runner("account", "add", code_val, name)
    print(out, err)
    assert code == 0
    parsed = list(csv.reader(io.StringIO(out)))
    assert parsed == [
        ["account", "name", "transactions", "balance"],
        [code_val, name, "0", "0.00"],
    ]
    stored = db.accounts.get(account=code_val)
    assert stored is not None
    assert stored.name == name
=== END AC account-add-success ===

=== AC account-add-duplicate ===
Intent: Adding a code that already exists exits 3 with empty stdout and the stored name unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

code_val = "ZQAD2"
original = "Original Name"
with db_session() as db:
    db.accounts.create(account=code_val, name=original)
    before = len(db.accounts.list())
    code, out, err = cli_runner("account", "add", code_val, "Other Name")
    print(out, err)
    assert code == 3
    assert out == ""
    assert len(db.accounts.list()) == before
    assert db.accounts.get(account=code_val).name == original
=== END AC account-add-duplicate ===

=== AC account-add-invalid-input ===
Intent: Lowercase code, over-long code, empty name, over-long name, and a comma in the name each exit 3 with empty stdout and store nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

cases = [
    ("zqad3", "Lowercase"),
    ("Z" * 13, "Long code"),
    ("ZQAD4", ""),
    ("ZQAD5", "N" * 41),
    ("ZQAD6", "has,comma"),
]
with db_session() as db:
    before = len(db.accounts.list())
    for acct, name in cases:
        code, out, err = cli_runner("account", "add", acct, name)
        print(acct, code, out, err)
        assert code == 3
        assert out == ""
        assert db.accounts.get(account=acct) is None
    assert len(db.accounts.list()) == before
=== END AC account-add-invalid-input ===

=== AC account-add-usage ===
Intent: Missing or surplus arguments to account add exit 2 with empty stdout and store nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    before = len(db.accounts.list())
    for args in (("account", "add"), ("account", "add", "ZQAD7"), ("account", "add", "ZQAD7", "Name", "extra")):
        code, out, err = cli_runner(*args)
        print(args, code, out, err)
        assert code == 2
        assert out == ""
    assert len(db.accounts.list()) == before
    assert db.accounts.get(account="ZQAD7") is None
=== END AC account-add-usage ===

## User Acceptance

- None.

## Guardrails

- A rejected add changes no stored record.
- Balances are formatted from integer cents with exactly two decimals.
- Persistence is reached only through the `persistence` package.
