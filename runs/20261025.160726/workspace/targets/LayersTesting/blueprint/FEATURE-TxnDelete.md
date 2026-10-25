# FEATURE: Txn Delete

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger txn delete <id>`, removing one transaction while keeping every balance non-negative. |
| Depends On | FEATURE-TxnGet.md, FEATURE-LedgerCore.md, FEATURE-CliEntry.md, DATABASE.md |
| Provides | ledger txn delete |
| Consumes | cli.main, balance_guard, ledger txn get |

## Purpose

Remove an existing transaction. The delete is rejected before any write if removing the row would leave the owning account's balance below zero.

## Trigger and Interface

`ledger txn delete <id>` takes exactly one argument.

| Condition | Exit | Stdout |
|-----------|------|--------|
| Deleted | 0 | Two lines: `deleted`, then the id |
| Removal would leave the owning account balance below zero | 3 | Nothing |
| No transaction with that id | 4 | Nothing |
| Wrong argument count, or an id that is not an integer | 2 | Nothing |
| Database unreachable or tables missing | 1 | Nothing |

One diagnostic line goes to standard error on every failure.

## Sequence

1. Check the argument count and parse the id (usage error otherwise).
2. Locate the transaction by listing transactions; if absent, fail with not found.
3. List the owning account's transactions and ask `balance_guard` for the balance that results from removing this row; if it is below zero, reject.
4. Only after the checks pass, remove the row through `transactions.delete` and print `deleted` and the id.

## Reads

All transactions, to locate the row, and the owning account's transactions, to compute the projected balance.

## Writes

Removal of exactly one `transactions` row.

## Database Interface

- `FEATURE-TXN-005` — write: delete a transaction - supplies: `txn_id` - returns: `txn_id`
- `FEATURE-TXN-002` — read: list transactions to locate the row and compute the projected balance - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC txndelete-success ===
Intent: txn delete prints deleted and the id, and the row is gone on read back.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TDACCT1"
    cat = "TDCAT1"
    db.accounts.create(account=acct, name="Delete Account")
    db.categories.create(category=cat, description="Delete Category")
    new_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=new_id, date="2026-04-01", account=acct, category=cat, amount=5450, memo="gone")
    before = len(db.transactions.list())
    code, out, err = cli_runner("txn", "delete", str(new_id))
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows == [["deleted"], [str(new_id)]]
    assert db.transactions.get(txn_id=new_id) is None
    assert len(db.transactions.list()) == before - 1
=== END AC txndelete-success ===

=== AC txndelete-absent ===
Intent: txn delete of an absent id exits 4 and removes nothing.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    absent_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1000
    before = len(db.transactions.list())
    code, out, err = cli_runner("txn", "delete", str(absent_id))
    print(out)
    print(err)
    assert code == 4
    assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txndelete-absent ===

=== AC txndelete-negative-balance ===
Intent: Deleting a credit that funds a later debit exits 3 and keeps both rows.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TDACCT2"
    cat = "TDCAT2"
    db.accounts.create(account=acct, name="Delete Overdraw")
    db.categories.create(category=cat, description="Delete Overdraw Category")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    credit_id = base + 1
    debit_id = base + 2
    db.transactions.create(txn_id=credit_id, date="2026-04-01", account=acct, category=cat, amount=10000, memo="credit")
    db.transactions.create(txn_id=debit_id, date="2026-04-02", account=acct, category=cat, amount=-5000, memo="debit")
    before = len(db.transactions.list())
    code, out, err = cli_runner("txn", "delete", str(credit_id))
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert db.transactions.get(txn_id=credit_id) is not None
    assert db.transactions.get(txn_id=debit_id) is not None
    assert len(db.transactions.list()) == before
=== END AC txndelete-negative-balance ===

=== AC txndelete-debit-allowed ===
Intent: Deleting a debit raises the balance and is accepted.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TDACCT3"
    cat = "TDCAT3"
    db.accounts.create(account=acct, name="Delete Debit")
    db.categories.create(category=cat, description="Delete Debit Category")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    credit_id = base + 1
    debit_id = base + 2
    db.transactions.create(txn_id=credit_id, date="2026-04-01", account=acct, category=cat, amount=10000, memo="credit")
    db.transactions.create(txn_id=debit_id, date="2026-04-02", account=acct, category=cat, amount=-5000, memo="debit")
    code, out, err = cli_runner("txn", "delete", str(debit_id))
    print(out)
    print(err)
    assert code == 0
    assert db.transactions.get(txn_id=debit_id) is None
    assert db.transactions.get(txn_id=credit_id) is not None
=== END AC txndelete-debit-allowed ===

=== AC txndelete-usage ===
Intent: Wrong argument counts and a non-integer id are usage errors with exit 2.

from cli.testing import cli_runner

for args in (("txn", "delete"), ("txn", "delete", "1", "2"), ("txn", "delete", "abc")):
    code, out, err = cli_runner(*args)
    print(args, code, out, err)
    assert code == 2
    assert out == ""
=== END AC txndelete-usage ===

## User Acceptance

- None.

## Guardrails

- The balance check runs before the delete; a rejected delete leaves every table unchanged.
- Exactly one row is removed per successful command.
- Standard output carries only the documented CSV; failures write one diagnostic line to standard error and nothing to standard output.
- Only the generated persistence package reaches the database.
