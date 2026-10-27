# FEATURE: Account Get

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger account get <code>`, printing the current account row with live transaction count and balance. |
| Depends On | FEATURE-AccountAdd.md, FEATURE-CliEntry.md, DATABASE.md |
| Provides | ledger account get |
| Consumes | ledger_core.accounts, cli.registry |

## Purpose

`ledger account get <code>` prints the account's header row and data row `account,name,transactions,balance`. The transaction count and balance are computed from the account's stored transactions using the `account_row` helper exported by `ledger_core.accounts`. The balance is the sum of integer cents, formatted with exactly two decimals.

## Behavior

- Exactly one argument is required; any other count is a usage error, exit 2.
- An absent code exits 4 with one stderr line and nothing on stdout.
- Success exits 0 and writes the CSV with `\n` line endings.
- The command never writes to the database.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: get an account by code - supplies: `account` - returns: `account`, `name`
- `FEATURE-TXN-005` — read: list an account's transactions - supplies: `account` - returns: `amount`

## Programmatic Acceptance

=== AC account-get-existing ===
Intent: An account with two stored transactions is printed with its live count and its balance, both derived from the fixture amounts.
Requires: executable=python3; scope=test

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

def money(c):
    sign = "-" if c < 0 else ""
    q, r = divmod(abs(c), 100)
    return f"{sign}{q}.{r:02d}"

code, label, cat = "ZZAG1", "Get Probe", "ZZAGC1"
amounts = [1000, -250]
with db_session() as db:
    db.accounts.create(account=code, name=label)
    db.categories.create(category=cat, description="Get Category")
    base = 900001001
    for i, cents in enumerate(amounts):
        db.transactions.create(txn_id=base + i, date="2026-04-01", account=code, category=cat, amount=cents, memo="")
    rc, out, err = cli_runner("account", "get", code)
    print(out)
    print(err)
    assert rc == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["account", "name", "transactions", "balance"]
    assert rows[1] == [code, label, str(len(amounts)), money(sum(amounts))]
    assert len(rows) == 2
=== END AC account-get-existing ===

=== AC account-get-empty-account ===
Intent: An account with no transactions prints a zero count and a zero balance.
Requires: executable=python3; scope=test

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

code, label = "ZZAG2", "Empty Probe"
with db_session() as db:
    db.accounts.create(account=code, name=label)
    rc, out, err = cli_runner("account", "get", code)
    print(out)
    print(err)
    assert rc == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[1] == [code, label, str(0), "0.00"]
=== END AC account-get-empty-account ===

=== AC account-get-absent ===
Intent: An absent account code exits 4 and writes nothing to standard output.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

code = "ZZAGNONE"
with db_session() as db:
    assert db.accounts.get(account=code) is None
    rc, out, err = cli_runner("account", "get", code)
    print(out)
    print(err)
    assert rc == 4
    assert out == ""
=== END AC account-get-absent ===

=== AC account-get-usage ===
Intent: A missing or surplus argument is a usage error with exit 2 and no standard output.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    rc, out, err = cli_runner("account", "get")
    assert rc == 2
    assert out == ""
    rc, out, err = cli_runner("account", "get", "ZZAG3", "EXTRA")
    assert rc == 2
    assert out == ""
=== END AC account-get-usage ===

## User Acceptance

- None.

## Guardrails

- The command is read-only and never writes to the database.
- Count and balance are computed from stored transactions, never cached or embedded.
- Amounts are integer cents; no floating point is used for money.
- Failures write nothing to standard output.
