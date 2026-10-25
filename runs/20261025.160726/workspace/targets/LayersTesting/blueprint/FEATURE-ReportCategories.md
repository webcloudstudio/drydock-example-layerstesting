# FEATURE: Report Categories

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger report categories`, listing transaction count, inflow, outflow, and net per category plus a TOTAL row. |
| Depends On | FEATURE-LoadTransactions.md, FEATURE-CliEntry.md, FEATURE-LedgerCore.md, DATABASE.md |
| Provides | ledger report categories |

## Purpose

`ledger report categories` prints, for every category ordered by code, how many transactions it has
and its inflow, outflow, and net, followed by a TOTAL row. Categories without transactions are
included. Every value is computed from the database at run time.

## Behavior

- Header row: `category,description,transactions,inflow,outflow,net`.
- One data row per category, ordered by category code, including categories with no transactions.
- `inflow` is the sum of positive amounts. `outflow` is the sum of the absolute values of negative
  amounts, written as a positive number. `net` is `inflow - outflow`.
- Final row: `TOTAL,,<count>,<inflow>,<outflow>,<net>`.
- Amounts are written with exactly two decimal places, a leading `-` when negative, and no
  thousands separator. Output is unquoted CSV with `\n` line endings; exit `0`.

## Database Interface

- `FEATURE-CATEGORY-002` — read: list every category in code order - supplies: `category` - returns: `category`, `description`
- `FEATURE-TXN-002` — read: list a category's transactions to total them - supplies: `category` - returns: `category`, `amount`

## Programmatic Acceptance

=== AC report-categories-rows ===
Intent: Each category row's count, inflow, outflow, and net match the stored transactions, in code order, followed by a consistent TOTAL row.

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
    acct = "ACPTCR9"
    db.accounts.create(account=acct, name="Category Report")
    db.categories.create(category="ACPTCRA", description="Category A")
    db.categories.create(category="ACPTCRB", description="Category B")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    db.transactions.create(txn_id=base + 1, date="2026-06-01", account=acct, category="ACPTCRA", amount=20000, memo="")
    db.transactions.create(txn_id=base + 2, date="2026-06-02", account=acct, category="ACPTCRB", amount=-1550, memo="")
    db.transactions.create(txn_id=base + 3, date="2026-06-03", account=acct, category="ACPTCRB", amount=-450, memo="")
    code, out, err = cli_runner("report", "categories")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["category", "description", "transactions", "inflow", "outflow", "net"]
    data = rows[1:-1]
    total = rows[-1]
    categories = db.categories.list()
    assert [r[0] for r in data] == [c.category for c in categories]
    sums = [0, 0, 0, 0]
    for row, cat in zip(data, categories):
        assert len(row) == 6
        txns = db.transactions.list(category=cat.category)
        inflow = sum(t.amount for t in txns if t.amount > 0)
        outflow = sum(-t.amount for t in txns if t.amount < 0)
        assert row[1] == cat.description
        assert int(row[2]) == len(txns)
        assert cents(row[3]) == inflow
        assert cents(row[4]) == outflow
        assert cents(row[5]) == inflow - outflow
        sums[0] += len(txns)
        sums[1] += inflow
        sums[2] += outflow
        sums[3] += inflow - outflow
    assert total[0] == "TOTAL"
    assert total[1] == ""
    assert len(total) == 6
    assert int(total[2]) == sums[0]
    assert cents(total[3]) == sums[1]
    assert cents(total[4]) == sums[2]
    assert cents(total[5]) == sums[3]
=== END AC report-categories-rows ===

=== AC report-categories-unused-category ===
Intent: A category with no transactions is listed with a zero count and zero amounts.

import csv
import io
import re
from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    cat = "ACPTCRU"
    db.categories.create(category=cat, description="Unused Category")
    code, out, err = cli_runner("report", "categories")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    mine = [r for r in rows[1:-1] if r[0] == cat]
    assert len(mine) == 1
    assert int(mine[0][2]) == 0
    for cell in mine[0][3:6]:
        assert re.fullmatch(r"-?\d+\.\d{2}", cell)
        assert int(Decimal(cell) * 100) == 0
=== END AC report-categories-unused-category ===

=== AC report-categories-outflow-positive ===
Intent: A category with only withdrawals reports outflow as a positive number and a negative net with a leading minus.

import csv
import io
import re
from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "ACPTCO1"
    funding = "ACPTCOF"
    spending = "ACPTCOS"
    db.accounts.create(account=acct, name="Outflow Report")
    db.categories.create(category=funding, description="Outflow Funding")
    db.categories.create(category=spending, description="Outflow Spending")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    db.transactions.create(txn_id=base + 1, date="2026-06-01", account=acct, category=funding, amount=9000, memo="")
    db.transactions.create(txn_id=base + 2, date="2026-06-02", account=acct, category=spending, amount=-1234, memo="")
    code, out, err = cli_runner("report", "categories")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    mine = [r for r in rows[1:-1] if r[0] == spending]
    assert len(mine) == 1
    row = mine[0]
    for cell in row[3:6]:
        assert re.fullmatch(r"-?\d+\.\d{2}", cell)
    assert int(Decimal(row[3]) * 100) == 0
    assert int(Decimal(row[4]) * 100) == 1234
    assert not row[4].startswith("-")
    assert int(Decimal(row[5]) * 100) == -1234
    assert row[5].startswith("-")
=== END AC report-categories-outflow-positive ===

## User Acceptance

- None.

## Guardrails

- No count or amount is hard-coded; every value comes from a query at run time.
- Amounts are integer cents internally and never floating point.
- Categories with no transactions are never omitted.
- The report writes nothing to the database.
