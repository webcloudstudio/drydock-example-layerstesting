# FEATURE: Transaction Get

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger txn get <id>`, printing one stored transaction row. |
| Depends On | FEATURE-TxnPost.md, FEATURE-CliEntry.md, DATABASE.md |
| Provides | ledger txn get |
| Consumes | ledger_core.transactions, cli.registry |

## Purpose

`ledger txn get <id>` prints the header row `txn_id,date,account,category,amount,memo` and the stored transaction, formatted with `txn_row` from `ledger_core.transactions`, with the amount shown in two decimals.

## Behavior

- Exactly one argument is required; otherwise exit 2.
- A non-integer id exits 3.
- An absent id exits 4.
- The command never writes to the database.

## Database Interface

- `FEATURE-TXN-002` — read: get a transaction by id - supplies: `txn_id` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC txn-get-existing ===
Intent: A stored transaction prints with every column and the cents shown as a two-decimal amount.
Requires: executable=python3; scope=test

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

acct, cat, tid = "ZZTG1", "ZZTGC1", 900001601
day, memo = "2026-04-05", "get probe"
with db_session() as db:
    db.accounts.create(account=acct, name="Get Probe")
    db.categories.create(category=cat, description="Get Category")
    db.transactions.create(txn_id=tid, date=day, account=acct, category=cat, amount=1234, memo=memo)
    rc, out, err = cli_runner("txn", "get", str(tid))
    print(out)
    print(err)
    assert rc == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert rows[1] == [str(tid), day, acct, cat, "12.34", memo]
=== END AC txn-get-existing ===

=== AC txn-get-negative-amount ===
Intent: A negative stored amount prints with a leading minus and two decimals.
Requires: executable=python3; scope=test

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

acct, cat, tid = "ZZTG2", "ZZTGC2", 900001602
with db_session() as db:
    db.accounts.create(account=acct, name="Get Probe")
    db.categories.create(category=cat, description="Get Category")
    db.transactions.create(txn_id=tid, date="2026-04-06", account=acct, category=cat, amount=2000, memo="")
    db.transactions.create(txn_id=tid + 1, date="2026-04-06", account=acct, category=cat, amount=-1250, memo="")
    rc, out, err = cli_runner("txn", "get", str(tid + 1))
    print(out)
    print(err)
    assert rc == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[1][4] == "-12.50"
=== END AC txn-get-negative-amount ===

=== AC txn-get-absent ===
Intent: An absent transaction id exits 4 with no standard output.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

tid = 999999999
with db_session() as db:
    assert db.transactions.get(txn_id=tid) is None
    rc, out, err = cli_runner("txn", "get", str(tid))
    print(err)
    assert rc == 4
    assert out == ""
=== END AC txn-get-absent ===

=== AC txn-get-bad-id ===
Intent: A non-integer id is rejected with exit 3 and a wrong argument count is a usage error with exit 2.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    rc, out, err = cli_runner("txn", "get", "abc")
    assert rc == 3
    assert out == ""
    rc, out, err = cli_runner("txn", "get")
    assert rc == 2
    assert out == ""
=== END AC txn-get-bad-id ===

## User Acceptance

- None.

## Guardrails

- The command is read-only and never writes to the database.
- Amounts are displayed from integer cents with exactly two decimals; floating point is never used.
- Failures write nothing to standard output.
