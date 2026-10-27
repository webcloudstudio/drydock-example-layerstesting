# FEATURE: Transaction Post

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger txn post`, validating every input and the balance rule before inserting one transaction. |
| Depends On | FEATURE-CliEntry.md, FEATURE-Validation.md, FEATURE-BalanceRule.md, DATABASE.md |
| Provides | ledger txn post, ledger_core.transactions |
| Consumes | ledger_core.validation, ledger_core.money, ledger_core.balances, cli.registry |

## Purpose

`ledger txn post <account> <category> <amount> <date> [<memo>]` records one transaction and prints the header row `txn_id,date,account,category,amount,memo` followed by the new row. `ledger_core.transactions` exports `txn_row` (formats a stored transaction as an output row) and `next_txn_id` (largest stored `txn_id` plus one, or 1 in an empty table), used by the other transaction commands and by transfer.

## Behavior

- Four or five arguments are required; otherwise exit 2. An omitted memo is stored as the empty string.
- Everything is checked before the write, in this order: amount, date, and memo validation; account exists; category exists; no resulting balance below zero. Any violation exits 3 and writes nothing.
- The amount is parsed to integer cents with no floating point and printed with exactly two decimals.
- The new `txn_id` is the largest present plus one, or 1 when none exist.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: check the account exists - supplies: `account` - returns: `account`
- `FEATURE-CATEGORY-002` — read: check the category exists - supplies: `category` - returns: `category`
- `FEATURE-TXN-005` — read: list transactions for balance and next id - supplies: `account` - returns: `txn_id`, `amount`
- `FEATURE-TXN-001` — write: create the transaction - supplies: `txn_id`, `date`, `account`, `category`, `amount`, `memo` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC txn-post-success ===
Intent: A valid post prints the new row with the next id, the supplied values, and a two-decimal amount, and a separate read shows the stored cents.
Requires: executable=python3; scope=test

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

acct, cat = "ZZTP1", "ZZTPC1"
amount, cents = "45.50", 4550
day, memo = "2026-04-01", "walk in sale"
with db_session() as db:
    db.accounts.create(account=acct, name="Post Probe")
    db.categories.create(category=cat, description="Post Category")
    expected_id = max([f(r, "txn_id") for r in db.transactions.list()], default=0) + 1
    rc, out, err = cli_runner("txn", "post", acct, cat, amount, day, memo)
    print(out)
    print(err)
    assert rc == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert rows[1] == [str(expected_id), day, acct, cat, amount, memo]
    back = db.transactions.get(txn_id=expected_id)
    assert back is not None
    assert f(back, "amount") == cents
    assert f(back, "memo") == memo
=== END AC txn-post-success ===

=== AC txn-post-default-memo ===
Intent: Omitting the memo stores an empty memo and the row still prints with six fields.
Requires: executable=python3; scope=test

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

acct, cat = "ZZTP2", "ZZTPC2"
amount, day = "10.00", "2026-04-02"
with db_session() as db:
    db.accounts.create(account=acct, name="Post Probe")
    db.categories.create(category=cat, description="Post Category")
    expected_id = max([f(r, "txn_id") for r in db.transactions.list()], default=0) + 1
    rc, out, err = cli_runner("txn", "post", acct, cat, amount, day)
    print(out)
    print(err)
    assert rc == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[1] == [str(expected_id), day, acct, cat, amount, ""]
    assert f(db.transactions.get(txn_id=expected_id), "memo") == ""
=== END AC txn-post-default-memo ===

=== AC txn-post-next-id ===
Intent: Two consecutive posts receive consecutive ids, the second one more than the first.
Requires: executable=python3; scope=test

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

acct, cat = "ZZTP3", "ZZTPC3"
with db_session() as db:
    db.accounts.create(account=acct, name="Post Probe")
    db.categories.create(category=cat, description="Post Category")
    ids = []
    for amount in ["5.00", "6.00"]:
        rc, out, err = cli_runner("txn", "post", acct, cat, amount, "2026-04-03")
        print(err)
        assert rc == 0
        ids.append(int(list(csv.reader(io.StringIO(out)))[1][0]))
    assert ids[1] == ids[0] + 1
=== END AC txn-post-next-id ===

=== AC txn-post-rejections ===
Intent: Unknown category, unknown account, three-decimal amount, zero amount, and an impossible calendar date each exit 3 and leave the transaction count unchanged.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

acct, cat = "ZZTP4", "ZZTPC4"
with db_session() as db:
    db.accounts.create(account=acct, name="Post Probe")
    db.categories.create(category=cat, description="Post Category")
    before = len(db.transactions.list())
    cases = [
        (acct, "ZZNOCAT", "1.00", "2026-04-01"),
        ("ZZNOACCT", cat, "1.00", "2026-04-01"),
        (acct, cat, "1.234", "2026-04-01"),
        (acct, cat, "0", "2026-04-01"),
        (acct, cat, "1.00", "2026-02-30"),
    ]
    for case in cases:
        rc, out, err = cli_runner("txn", "post", *case)
        print(case, rc, err)
        assert rc == 3
        assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txn-post-rejections ===

=== AC txn-post-negative-balance ===
Intent: A withdrawal larger than the account balance exits 3 and stores nothing, while a withdrawal within the balance succeeds.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

acct, cat = "ZZTP5", "ZZTPC5"
funds = 1000
with db_session() as db:
    db.accounts.create(account=acct, name="Post Probe")
    db.categories.create(category=cat, description="Post Category")
    db.transactions.create(txn_id=900001501, date="2026-04-01", account=acct, category=cat, amount=funds, memo="")
    before = len(db.transactions.list())
    rc, out, err = cli_runner("txn", "post", acct, cat, "-10.01", "2026-04-02")
    print(err)
    assert rc == 3
    assert out == ""
    assert len(db.transactions.list()) == before
    rc, out, err = cli_runner("txn", "post", acct, cat, "-10.00", "2026-04-02")
    print(err)
    assert rc == 0
    assert len(db.transactions.list()) == before + 1
=== END AC txn-post-negative-balance ===

=== AC txn-post-usage ===
Intent: Too few or too many arguments are usage errors with exit 2 and no standard output.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    rc, out, err = cli_runner("txn", "post", "ZZTP6", "ZZTPC6", "1.00")
    assert rc == 2
    assert out == ""
    rc, out, err = cli_runner("txn", "post", "A", "B", "1.00", "2026-04-01", "m", "extra")
    assert rc == 2
    assert out == ""
=== END AC txn-post-usage ===

## User Acceptance

- None.

## Guardrails

- Every input and the balance rule are checked before the first write; a rejected post stores nothing.
- Amounts are integer cents at every layer; floating point is never used for money.
- The next `txn_id` is computed from stored rows, never hardcoded.
- Failures write nothing to standard output.
