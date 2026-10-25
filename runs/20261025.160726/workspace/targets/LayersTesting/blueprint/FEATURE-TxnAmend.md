# FEATURE: Txn Amend

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger txn amend <id> <amount>`, changing only a transaction's amount while keeping every balance non-negative. |
| Depends On | FEATURE-TxnGet.md, FEATURE-LedgerCore.md, FEATURE-CliEntry.md, DATABASE.md |
| Provides | ledger txn amend |
| Consumes | cli.main, parse_amount, format_amount, balance_guard, ledger txn get |

## Purpose

Correct the amount of an existing transaction. Date, account, category, and memo never change. The change is rejected before any write if it would leave the owning account's balance below zero.

## Trigger and Interface

`ledger txn amend <id> <amount>` takes exactly two arguments.

| Condition | Exit | Stdout |
|-----------|------|--------|
| Amended | 0 | Header `txn_id,date,account,category,amount,memo`, then the updated row |
| Amount fails `-?DIGITS[.D[D]]`, has more than two decimals, or is zero | 3 | Nothing |
| Resulting balance of the owning account would be below zero | 3 | Nothing |
| No transaction with that id | 4 | Nothing |
| Wrong argument count, or an id that is not an integer | 2 | Nothing |
| Database unreachable or tables missing | 1 | Nothing |

One diagnostic line goes to standard error on every failure.

## Sequence

1. Check the argument count and parse the id (usage error otherwise).
2. Parse the amount with `parse_amount` into integer cents (rejection otherwise).
3. Locate the transaction by listing transactions; if absent, fail with not found.
4. List the owning account's transactions and ask `balance_guard` for the balance that results from replacing this row's amount; if any resulting balance is below zero, reject.
5. Only after every check passes, write the new amount through `transactions.update`, then print the returned row.

## Reads

All transactions, to locate the row, and the owning account's transactions, to compute the projected balance.

## Writes

The `amount` column of exactly one `transactions` row.

## Database Interface

- `FEATURE-TXN-004` — write: change a transaction amount - supplies: `txn_id`, `amount` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TXN-002` — read: list transactions to locate the row and compute the projected balance - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC txnamend-success ===
Intent: txn amend prints the updated row, changes only the amount, and persists it.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TAACCT1"
    cat = "TACAT1"
    day = "2026-04-01"
    memo = "walk in sale"
    db.accounts.create(account=acct, name="Amend Account")
    db.categories.create(category=cat, description="Amend Category")
    new_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=new_id, date=day, account=acct, category=cat, amount=4550, memo=memo)
    code, out, err = cli_runner("txn", "amend", str(new_id), "54.50")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert rows[1] == [str(new_id), day, acct, cat, "54.50", memo]
    stored = db.transactions.get(txn_id=new_id)
    assert stored is not None
    assert stored.amount == 5450
    assert stored.date == day
    assert stored.account == acct
    assert stored.category == cat
    assert stored.memo == memo
=== END AC txnamend-success ===

=== AC txnamend-absent ===
Intent: txn amend of an absent id exits 4 with nothing on standard output.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    absent_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1000
    before = len(db.transactions.list())
    code, out, err = cli_runner("txn", "amend", str(absent_id), "5.00")
    print(out)
    print(err)
    assert code == 4
    assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txnamend-absent ===

=== AC txnamend-negative-balance ===
Intent: An amendment that would leave the account balance below zero exits 3 and changes nothing.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TAACCT2"
    cat = "TACAT2"
    db.accounts.create(account=acct, name="Amend Overdraw")
    db.categories.create(category=cat, description="Amend Overdraw Category")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    credit_id = base + 1
    debit_id = base + 2
    db.transactions.create(txn_id=credit_id, date="2026-04-01", account=acct, category=cat, amount=10000, memo="credit")
    db.transactions.create(txn_id=debit_id, date="2026-04-02", account=acct, category=cat, amount=-5000, memo="debit")
    code, out, err = cli_runner("txn", "amend", str(debit_id), "-200.00")
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    stored = db.transactions.get(txn_id=debit_id)
    assert stored is not None
    assert stored.amount == -5000
    assert db.transactions.get(txn_id=credit_id).amount == 10000
=== END AC txnamend-negative-balance ===

=== AC txnamend-boundary-zero-balance ===
Intent: An amendment that leaves the balance exactly zero is accepted.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TAACCT3"
    cat = "TACAT3"
    db.accounts.create(account=acct, name="Amend Boundary")
    db.categories.create(category=cat, description="Amend Boundary Category")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    credit_id = base + 1
    debit_id = base + 2
    db.transactions.create(txn_id=credit_id, date="2026-04-01", account=acct, category=cat, amount=10000, memo="credit")
    db.transactions.create(txn_id=debit_id, date="2026-04-02", account=acct, category=cat, amount=-5000, memo="debit")
    code, out, err = cli_runner("txn", "amend", str(debit_id), "-100.00")
    print(out)
    print(err)
    assert code == 0
    stored = db.transactions.get(txn_id=debit_id)
    assert stored is not None
    assert stored.amount == -10000
=== END AC txnamend-boundary-zero-balance ===

=== AC txnamend-invalid-amount ===
Intent: Malformed, over-precise, and zero amounts exit 3 and leave the row unchanged.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TAACCT4"
    cat = "TACAT4"
    db.accounts.create(account=acct, name="Amend Invalid")
    db.categories.create(category=cat, description="Amend Invalid Category")
    new_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=new_id, date="2026-04-01", account=acct, category=cat, amount=2000, memo="keep")
    for bad in ("1.234", "0", "0.00", "abc", "12."):
        code, out, err = cli_runner("txn", "amend", str(new_id), bad)
        print(bad, code, out, err)
        assert code == 3
        assert out == ""
        assert db.transactions.get(txn_id=new_id).amount == 2000
=== END AC txnamend-invalid-amount ===

=== AC txnamend-usage ===
Intent: Wrong argument counts and a non-integer id are usage errors with exit 2.

from cli.testing import cli_runner

for args in (("txn", "amend"), ("txn", "amend", "1"), ("txn", "amend", "1", "2.00", "3.00"), ("txn", "amend", "abc", "2.00")):
    code, out, err = cli_runner(*args)
    print(args, code, out, err)
    assert code == 2
    assert out == ""
=== END AC txnamend-usage ===

## User Acceptance

- None.

## Guardrails

- Only the amount changes; date, account, category, and memo are never written.
- The balance check runs before the first write; a rejected amendment leaves every table unchanged.
- Amounts are integer cents at every layer; no floating point.
- Standard output carries only the documented CSV; failures write one diagnostic line to standard error and nothing to standard output.
- Only the generated persistence package reaches the database.
