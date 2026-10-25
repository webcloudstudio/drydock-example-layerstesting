# FEATURE: Report Monthly

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger report monthly`, listing transaction count, inflow, outflow, and net per calendar month plus a TOTAL row. |
| Depends On | FEATURE-LoadTransactions.md, FEATURE-CliEntry.md, FEATURE-LedgerCore.md, DATABASE.md |
| Provides | ledger report monthly |

## Purpose

`ledger report monthly` prints one row per `YYYY-MM` that has at least one transaction, in ascending
order, with that month's transaction count, inflow, outflow, and net, followed by a TOTAL row. Every
value is computed from the database at run time.

## Behavior

- Header row: `month,transactions,inflow,outflow,net`.
- The month of a transaction is the first seven characters of its `YYYY-MM-DD` date.
- Only months with transactions appear, ascending.
- `inflow` is the sum of positive amounts. `outflow` is the sum of the absolute values of negative
  amounts, written as a positive number. `net` is `inflow - outflow`.
- Final row: `TOTAL,<count>,<inflow>,<outflow>,<net>`.
- Amounts are written with exactly two decimal places, a leading `-` when negative, and no
  thousands separator. Output is unquoted CSV with `\n` line endings; exit `0`.

## Database Interface

- `FEATURE-TXN-002` — read: list every transaction to group by month - supplies: `account`, `category` - returns: `date`, `amount`

## Programmatic Acceptance

=== AC report-monthly-rows ===
Intent: Each month row's count, inflow, outflow, and net match the stored transactions grouped by date, ascending, followed by a consistent TOTAL row.

import csv
import io
import re
from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

def cents(text):
    assert re.fullmatch(r"-?\d+\.\d{2}", text), text
    return int(Decimal(text) * 100)

with db_session() as db:
    acct = "ACPTMR1"
    cat = "ACPTMRC"
    db.accounts.create(account=acct, name="Monthly Report")
    db.categories.create(category=cat, description="Monthly Category")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    db.transactions.create(txn_id=base + 1, date="2031-07-01", account=acct, category=cat, amount=50000, memo="")
    db.transactions.create(txn_id=base + 2, date="2031-07-15", account=acct, category=cat, amount=-1999, memo="")
    db.transactions.create(txn_id=base + 3, date="2031-09-02", account=acct, category=cat, amount=-2001, memo="")
    code, out, err = cli_runner("report", "monthly")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["month", "transactions", "inflow", "outflow", "net"]
    data = rows[1:-1]
    total = rows[-1]
    txns = db.transactions.list()
    months = sorted({t.date[:7] for t in txns})
    assert [r[0] for r in data] == months
    sums = [0, 0, 0, 0]
    for row, month in zip(data, months):
        assert len(row) == 5
        group = [t for t in txns if t.date[:7] == month]
        inflow = sum(t.amount for t in group if t.amount > 0)
        outflow = sum(-t.amount for t in group if t.amount < 0)
        assert int(row[1]) == len(group)
        assert cents(row[2]) == inflow
        assert cents(row[3]) == outflow
        assert cents(row[4]) == inflow - outflow
        sums[0] += len(group)
        sums[1] += inflow
        sums[2] += outflow
        sums[3] += inflow - outflow
    assert total[0] == "TOTAL"
    assert len(total) == 5
    assert int(total[1]) == sums[0]
    assert cents(total[2]) == sums[1]
    assert cents(total[3]) == sums[2]
    assert cents(total[4]) == sums[3]
=== END AC report-monthly-rows ===

=== AC report-monthly-skips-empty-months ===
Intent: A month between two months with transactions but with none of its own does not appear.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "ACPTMS1"
    cat = "ACPTMSC"
    db.accounts.create(account=acct, name="Gap Report")
    db.categories.create(category=cat, description="Gap Category")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    db.transactions.create(txn_id=base + 1, date="2032-01-10", account=acct, category=cat, amount=1000, memo="")
    db.transactions.create(txn_id=base + 2, date="2032-03-10", account=acct, category=cat, amount=1000, memo="")
    code, out, err = cli_runner("report", "monthly")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    months = [r[0] for r in rows[1:-1]]
    stored = sorted({t.date[:7] for t in db.transactions.list()})
    assert months == stored
    assert "2032-01" in months
    assert "2032-03" in months
    assert "2032-02" not in months
=== END AC report-monthly-skips-empty-months ===

=== AC report-monthly-reflects-changes ===
Intent: The report is computed from the database, so a new transaction in a month raises that month's count by one.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

def count_for(out, month):
    rows = list(csv.reader(io.StringIO(out)))
    mine = [r for r in rows[1:-1] if r[0] == month]
    return int(mine[0][1]) if mine else 0

with db_session() as db:
    acct = "ACPTMC1"
    cat = "ACPTMCC"
    month = "2033-05"
    db.accounts.create(account=acct, name="Changing Monthly")
    db.categories.create(category=cat, description="Changing Monthly Category")
    code, out, err = cli_runner("report", "monthly")
    print(out)
    print(err)
    assert code == 0
    first = count_for(out, month)
    tid = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=tid, date="2033-05-20", account=acct, category=cat, amount=700, memo="")
    code, out, err = cli_runner("report", "monthly")
    print(out)
    print(err)
    assert code == 0
    assert count_for(out, month) == first + 1
=== END AC report-monthly-reflects-changes ===

## User Acceptance

- None.

## Guardrails

- No month, count, or amount is hard-coded; every value comes from a query at run time.
- Amounts are integer cents internally and never floating point.
- Months without transactions are never listed.
- The report writes nothing to the database.
