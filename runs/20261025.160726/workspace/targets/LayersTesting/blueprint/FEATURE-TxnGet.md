# FEATURE: Txn Get

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger txn get <id>`, printing one transaction row or exiting 4 when absent. |
| Depends On | FEATURE-TxnPost.md, FEATURE-CliEntry.md, FEATURE-LedgerCore.md, DATABASE.md |
| Provides | ledger txn get |
| Consumes | cli.main, format_amount |

## Purpose

Read a single transaction by id and print it in the transaction CSV shape. The command never writes.

## Trigger and Interface

`ledger txn get <id>` takes exactly one argument. The id is a base-10 integer.

| Condition | Exit | Stdout |
|-----------|------|--------|
| Row found | 0 | Header `txn_id,date,account,category,amount,memo`, then the row |
| No row with that id | 4 | Nothing |
| Wrong argument count, or an id that is not an integer | 2 | Nothing |
| Database unreachable or tables missing | 1 | Nothing |

One diagnostic line goes to standard error on every failure.

## Sequence

1. Check the argument count and parse the id; failure is a usage error.
2. Read the row through `transactions.get`.
3. If the result is `None`, fail with the not-found exit code.
4. Print the header and one row. The amount is formatted from integer cents with `format_amount`: exactly two decimals, a leading `-` when negative, no thousands separator. An empty memo prints as an empty trailing field.

## Reads

The `transactions` row for the id. Nothing else.

## Writes

None.

## Database Interface

- `FEATURE-TXN-001` — read: get a transaction by id - supplies: `txn_id` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC txnget-present ===
Intent: txn get prints the header and the stored row with a two-decimal amount.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TGACCT1"
    cat = "TGCAT1"
    day = "2026-04-01"
    memo = "walk in sale"
    db.accounts.create(account=acct, name="Get Account")
    db.categories.create(category=cat, description="Get Category")
    new_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=new_id, date=day, account=acct, category=cat, amount=4550, memo=memo)
    code, out, err = cli_runner("txn", "get", str(new_id))
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert len(rows) == 2
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert rows[1] == [str(new_id), day, acct, cat, "45.50", memo]
=== END AC txnget-present ===

=== AC txnget-negative-empty-memo ===
Intent: A negative amount prints with a leading minus and an empty memo prints as an empty field.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TGACCT2"
    cat = "TGCAT2"
    day = "2026-04-02"
    memo = ""
    db.accounts.create(account=acct, name="Get Account Two")
    db.categories.create(category=cat, description="Get Category Two")
    new_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=new_id, date=day, account=acct, category=cat, amount=-1250, memo=memo)
    code, out, err = cli_runner("txn", "get", str(new_id))
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert len(rows) == 2
    assert rows[1] == [str(new_id), day, acct, cat, "-12.50", memo]
=== END AC txnget-negative-empty-memo ===

=== AC txnget-absent ===
Intent: txn get of an absent id exits 4 with nothing on standard output.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    absent_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1000
    code, out, err = cli_runner("txn", "get", str(absent_id))
    print(out)
    print(err)
    assert code == 4
    assert out == ""
=== END AC txnget-absent ===

=== AC txnget-usage ===
Intent: Wrong argument counts and a non-integer id are usage errors with exit 2 and no output.

from cli.testing import cli_runner

for args in (("txn", "get"), ("txn", "get", "1", "2"), ("txn", "get", "abc")):
    code, out, err = cli_runner(*args)
    print(args, code, out, err)
    assert code == 2
    assert out == ""
=== END AC txnget-usage ===

=== AC txnget-read-only ===
Intent: txn get leaves the stored row and the table size unchanged.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TGACCT3"
    cat = "TGCAT3"
    db.accounts.create(account=acct, name="Get Account Three")
    db.categories.create(category=cat, description="Get Category Three")
    new_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=new_id, date="2026-04-03", account=acct, category=cat, amount=700, memo="keep")
    before_row = db.transactions.get(txn_id=new_id)
    before_count = len(db.transactions.list())
    code, out, err = cli_runner("txn", "get", str(new_id))
    assert code == 0
    after_row = db.transactions.get(txn_id=new_id)
    assert after_row == before_row
    assert len(db.transactions.list()) == before_count
=== END AC txnget-read-only ===

## User Acceptance

- None.

## Guardrails

- The command never writes to any table.
- Amounts are read as integer cents and formatted without floating point.
- Standard output carries only the documented CSV; failures write one diagnostic line to standard error and nothing to standard output.
- Only the generated persistence package reaches the database.
