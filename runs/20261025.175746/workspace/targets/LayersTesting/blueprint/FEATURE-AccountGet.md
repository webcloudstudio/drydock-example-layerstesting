# FEATURE: Account Get

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger account get`, which prints one account row with its transaction count and balance. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-CliFoundation.md, FEATURE-BalanceRules.md |
| Provides | ledger account get |
| Consumes | accounts.get, account_summary |

## Purpose

Look up a single account and show its current transaction count and balance.

## Trigger

`./ledger account get <code>`

## Behavior

1. Require exactly one argument after `account get`; otherwise exit 2.
2. Look up the account with `accounts.get`. An absent code exits 4.
3. Print `account,name,transactions,balance` and the account row. The transaction count and balance come from `account_summary`, computed from stored transactions in integer cents, with the balance written with two decimals.

## Exit Codes

| Code | Condition |
|------|-----------|
| 0 | Row printed |
| 1 | Database unreachable |
| 2 | Wrong argument count |
| 4 | Account absent |

## Database Interface

- `FEATURE-ACCOUNTS-002` — read: get an account by code - supplies: `account` - returns: `account`, `name`

## Programmatic Acceptance

=== AC account-get-row ===
Intent: Getting an existing account prints its name, transaction count, and a balance computed from its stored transactions.

import csv
import io
from decimal import Decimal

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "UTGET1"
cat = "UTGETC1"
name = "Get Probe"
amounts = [10000, -2550]
with db_session() as db:
    db.accounts.create(account=acct, name=name)
    db.categories.create(category=cat, description="Get Probe")
    next_id = 930001
    for cents in amounts:
        db.transactions.create(
            txn_id=next_id, date="2098-01-01", account=acct,
            category=cat, amount=cents, memo="g",
        )
        next_id += 1
    code, out, err = cli_runner("account", "get", acct)
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["account", "name", "transactions", "balance"]
    assert len(rows) == 2
    assert rows[1][0] == acct
    assert rows[1][1] == name
    assert int(rows[1][2]) == len(amounts)
    assert Decimal(rows[1][3]) == Decimal(sum(amounts)) / 100
    assert len(rows[1][3].split(".")[1]) == 2
=== END AC account-get-row ===

=== AC account-get-empty ===
Intent: An account with no transactions reports zero transactions and a zero balance.

import csv
import io
from decimal import Decimal

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "UTGET2"
with db_session() as db:
    db.accounts.create(account=acct, name="Empty Probe")
    code, out, err = cli_runner("account", "get", acct)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert int(rows[1][2]) == 0
    assert Decimal(rows[1][3]) == 0
=== END AC account-get-empty ===

=== AC account-get-absent ===
Intent: An absent account exits 4 with nothing on standard output.

from cli.testing import cli_runner
from persistence.testing import db_session

absent = "UTGETNONE"
with db_session() as db:
    assert db.accounts.get(account=absent) is None
    code, out, err = cli_runner("account", "get", absent)
    assert code == 4
    assert out == ""
=== END AC account-get-absent ===

=== AC account-get-usage ===
Intent: A wrong argument count exits 2.

from cli.testing import cli_runner

code, out, err = cli_runner("account", "get")
assert code == 2
assert out == ""
code, out, err = cli_runner("account", "get", "A", "B")
assert code == 2
assert out == ""
=== END AC account-get-usage ===

## User Acceptance

- None.

## Guardrails

- Read-only: this command never writes.
- Balances are computed from stored rows in integer cents.
- A failing command writes nothing to standard output.
