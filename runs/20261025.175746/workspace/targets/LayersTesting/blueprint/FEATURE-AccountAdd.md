# FEATURE: Account Add

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger account add`, which validates and stores a new account and prints its row. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-CliFoundation.md, FEATURE-BalanceRules.md |
| Provides | ledger account add |
| Consumes | accounts.create, accounts.get, account_summary |

## Purpose

Add a cash account (drawer, safe, petty cash) to the ledger.

## Trigger

`./ledger account add <code> <name>`

## Behavior

1. Require exactly two arguments after `account add`; otherwise exit 2.
2. Validate the code (1 to 12 characters from `A-Z` and `0-9`) and the name (1 to 40 characters, no comma or newline). Invalid input exits 3.
3. If `accounts.get` finds the code, exit 3 (duplicate key). Nothing is written.
4. Store the account with `accounts.create`.
5. Print the account row from `account_summary`: header `account,name,transactions,balance`, then the code, name, transaction count, and balance. A new account has zero transactions and balance written with two decimals.

All checks complete before the single write.

## Exit Codes

| Code | Condition |
|------|-----------|
| 0 | Account stored |
| 1 | Database unreachable |
| 2 | Wrong argument count |
| 3 | Invalid code or name, or duplicate code |

## Database Interface

- `FEATURE-ACCOUNTS-001` — write: create an account - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-ACCOUNTS-002` — read: get an account by code - supplies: `account` - returns: `account`, `name`

## Programmatic Acceptance

=== AC account-add-stores ===
Intent: Adding an account exits 0, prints the account row with zero transactions, and persists the account.

import csv
import io
from decimal import Decimal

from cli.testing import cli_runner
from persistence.testing import db_session

code_ = "UTADD1"
name = "Event Float"
with db_session() as db:
    assert db.accounts.get(account=code_) is None
    code, out, err = cli_runner("account", "add", code_, name)
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["account", "name", "transactions", "balance"]
    assert len(rows) == 2
    assert rows[1][0] == code_
    assert rows[1][1] == name
    assert int(rows[1][2]) == 0
    assert Decimal(rows[1][3]) == 0
    assert len(rows[1][3].split(".")[1]) == 2
    stored = db.accounts.get(account=code_)
    assert stored is not None
    assert stored.name == name
=== END AC account-add-stores ===

=== AC account-add-duplicate ===
Intent: Adding an existing code exits 3, prints nothing on standard output, and leaves the stored name unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

code_ = "UTADD2"
original = "Original Name"
with db_session() as db:
    db.accounts.create(account=code_, name=original)
    code, out, err = cli_runner("account", "add", code_, "Other Name")
    assert code == 3
    assert out == ""
    assert db.accounts.get(account=code_).name == original
=== END AC account-add-duplicate ===

=== AC account-add-invalid-code ===
Intent: Codes that are lowercase, too long, or empty are rejected with exit 3 and nothing is stored.

from cli.testing import cli_runner
from persistence.testing import db_session

bad_codes = ["lower1", "ABCDEFGHIJKLM", "BAD-CODE", ""]
with db_session() as db:
    before = len(db.accounts.list())
    for bad in bad_codes:
        code, out, err = cli_runner("account", "add", bad, "Valid Name")
        assert code == 3, bad
        assert out == ""
    assert len(db.accounts.list()) == before
=== END AC account-add-invalid-code ===

=== AC account-add-invalid-name ===
Intent: Names that are empty, over 40 characters, or contain a comma are rejected with exit 3 and nothing is stored.

from cli.testing import cli_runner
from persistence.testing import db_session

code_ = "UTADD3"
bad_names = ["", "N" * 41, "has,comma"]
with db_session() as db:
    for bad in bad_names:
        code, out, err = cli_runner("account", "add", code_, bad)
        assert code == 3, bad
        assert out == ""
    assert db.accounts.get(account=code_) is None
=== END AC account-add-invalid-name ===

=== AC account-add-usage ===
Intent: A wrong argument count exits 2 and stores nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

code_ = "UTADD4"
with db_session() as db:
    code, out, err = cli_runner("account", "add", code_)
    assert code == 2
    assert out == ""
    code, out, err = cli_runner("account", "add", code_, "A Name", "extra")
    assert code == 2
    assert out == ""
    assert db.accounts.get(account=code_) is None
=== END AC account-add-usage ===

## User Acceptance

- None.

## Guardrails

- All validation and the duplicate check complete before the write.
- A failing command writes nothing to standard output.
- Balances are computed from stored rows in integer cents.
