# FEATURE: Account Rename

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger account rename`, which changes an account's name and prints the updated row. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-CliFoundation.md, FEATURE-BalanceRules.md |
| Provides | ledger account rename |
| Consumes | accounts.update, accounts.get, account_summary |

## Purpose

Correct or change the display name of an existing account without touching its code or transactions.

## Trigger

`./ledger account rename <code> <name>`

## Behavior

1. Require exactly two arguments after `account rename`; otherwise exit 2.
2. Validate the name (1 to 40 characters, no comma or newline). Invalid input exits 3.
3. Look up the account with `accounts.get`. An absent code exits 4.
4. Update the name with `accounts.update`. Only the name changes.
5. Print `account,name,transactions,balance` and the updated row from `account_summary`.

All checks complete before the single write.

## Exit Codes

| Code | Condition |
|------|-----------|
| 0 | Account renamed |
| 1 | Database unreachable |
| 2 | Wrong argument count |
| 3 | Invalid name |
| 4 | Account absent |

## Database Interface

- `FEATURE-ACCOUNTS-002` — read: get an account by code - supplies: `account` - returns: `account`, `name`
- `FEATURE-ACCOUNTS-004` — write: rename an account - supplies: `account`, `name` - returns: `account`, `name`

## Programmatic Acceptance

=== AC account-rename-updates ===
Intent: Renaming prints the row with the new name and persists it, leaving the transaction count unchanged.

import csv
import io

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "UTREN1"
cat = "UTRENC1"
before = "Event Float"
after = "Event Cash Box"
with db_session() as db:
    db.accounts.create(account=acct, name=before)
    db.categories.create(category=cat, description="Rename Probe")
    db.transactions.create(
        txn_id=940001, date="2098-01-01", account=acct, category=cat, amount=500, memo="r"
    )
    code, out, err = cli_runner("account", "rename", acct, after)
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["account", "name", "transactions", "balance"]
    assert rows[1][0] == acct
    assert rows[1][1] == after
    assert int(rows[1][2]) == 1
    assert db.accounts.get(account=acct).name == after
    assert db.transactions.get(txn_id=940001).account == acct
=== END AC account-rename-updates ===

=== AC account-rename-absent ===
Intent: Renaming an absent account exits 4, prints nothing, and creates no account.

from cli.testing import cli_runner
from persistence.testing import db_session

absent = "UTRENNONE"
with db_session() as db:
    code, out, err = cli_runner("account", "rename", absent, "New Name")
    assert code == 4
    assert out == ""
    assert db.accounts.get(account=absent) is None
=== END AC account-rename-absent ===

=== AC account-rename-invalid-name ===
Intent: An empty, over-long, or comma-containing name exits 3 and leaves the stored name unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "UTREN2"
original = "Keep Me"
with db_session() as db:
    db.accounts.create(account=acct, name=original)
    for bad in ["", "N" * 41, "has,comma"]:
        code, out, err = cli_runner("account", "rename", acct, bad)
        assert code == 3, bad
        assert out == ""
        assert db.accounts.get(account=acct).name == original
=== END AC account-rename-invalid-name ===

=== AC account-rename-usage ===
Intent: A wrong argument count exits 2 and changes nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "UTREN3"
original = "Usage Probe"
with db_session() as db:
    db.accounts.create(account=acct, name=original)
    code, out, err = cli_runner("account", "rename", acct)
    assert code == 2
    assert out == ""
    code, out, err = cli_runner("account", "rename", acct, "New", "extra")
    assert code == 2
    assert db.accounts.get(account=acct).name == original
=== END AC account-rename-usage ===

## User Acceptance

- None.

## Guardrails

- Only the name changes; code and transactions are untouched.
- All validation completes before the write.
- A failing command writes nothing to standard output.
