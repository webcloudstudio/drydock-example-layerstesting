# FEATURE: Report Categories

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger report categories`, per-category transaction counts with inflow, outflow, and net computed from stored transactions. |
| Depends On | FEATURE-ReportBalances.md, FEATURE-LedgerCli.md, DATABASE.md |
| Provides | ledger report categories |
| Consumes | ledger, categories, transactions |

## Purpose

Show how cash moved by category, including categories that have no transactions.

## Interface

`ledger report categories`

Standard output on success (exit 0):

- header `category,description,transactions,inflow,outflow,net`
- one row per category ordered by code ascending, including categories with no transactions
- final row `TOTAL,,<count>,<inflow>,<outflow>,<net>`

## Behavior

1. Read categories with `db.categories.list` and transactions with `db.transactions.list`.
2. `inflow` is the sum of positive amounts; `outflow` is the sum of the absolute values of negative amounts, written as a positive number; `net` is `inflow - outflow`.
3. All amounts are integer cents, written with exactly two decimals and no thousands separator.
4. The TOTAL count is the number of transactions; its inflow, outflow, and net are the column sums.
5. With no categories the output is the header and `TOTAL,,0,0.00,0.00,0.00`.
6. The command is read-only.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC report-categories-rows ===
Intent: Each category row carries count, inflow, outflow, and net derived from the stored transactions, categories are ordered by code, a category without transactions still appears with zeros, and the TOTAL row sums the columns.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQG0"
money = r"-?\d+\.\d{2}"
with db_session() as db:
    db.accounts.create(account=acct, name="Cat Account")
    db.categories.create(category="ZQG3", description="Third Category")
    db.categories.create(category="ZQG1", description="First Category")
    db.categories.create(category="ZQG2", description="Unused Category")
    base = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(txn_id=base, date="2026-06-01", account=acct, category="ZQG1", amount=100000, memo="")
    db.transactions.create(txn_id=base + 1, date="2026-06-02", account=acct, category="ZQG1", amount=25050, memo="")
    db.transactions.create(txn_id=base + 2, date="2026-06-03", account=acct, category="ZQG1", amount=-4000, memo="")
    db.transactions.create(txn_id=base + 3, date="2026-06-04", account=acct, category="ZQG3", amount=-10000, memo="")
    count_before = len(db.transactions.list())
    code, out, err = cli_runner("report", "categories")
    print(out)
    print(err)
    assert code == 0
    assert "\r" not in out
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["category", "description", "transactions", "inflow", "outflow", "net"]
    all_txns = db.transactions.list()
    expected = []
    for c in sorted(db.categories.list(), key=lambda r: r.category):
        mine = [t.amount for t in all_txns if t.category == c.category]
        inflow = sum(a for a in mine if a > 0)
        outflow = sum(-a for a in mine if a < 0)
        expected.append((c.category, c.description, len(mine), inflow, outflow))
    data = rows[1:-1]
    assert len(data) == len(expected)
    for row, (cat_code, desc, n, inflow, outflow) in zip(data, expected):
        assert row[0] == cat_code
        assert row[1] == desc
        assert int(row[2]) == n
        assert Decimal(row[3]) == Decimal(inflow).scaleb(-2)
        assert Decimal(row[4]) == Decimal(outflow).scaleb(-2)
        assert Decimal(row[5]) == Decimal(inflow - outflow).scaleb(-2)
        for cell in row[3:]:
            assert re.fullmatch(money, cell)
    codes = [r[0] for r in data]
    assert codes.index("ZQG1") < codes.index("ZQG2") < codes.index("ZQG3")
    unused = data[codes.index("ZQG2")]
    assert int(unused[2]) == 0
    assert Decimal(unused[3]) == 0 and Decimal(unused[4]) == 0 and Decimal(unused[5]) == 0
    total = rows[-1]
    assert total[0] == "TOTAL" and total[1] == ""
    assert int(total[2]) == sum(e[2] for e in expected)
    assert Decimal(total[3]) == Decimal(sum(e[3] for e in expected)).scaleb(-2)
    assert Decimal(total[4]) == Decimal(sum(e[4] for e in expected)).scaleb(-2)
    assert Decimal(total[5]) == Decimal(sum(e[3] - e[4] for e in expected)).scaleb(-2)
    assert len(db.transactions.list()) == count_before
=== END AC report-categories-rows ===

=== AC report-categories-no-categories ===
Intent: With no categories the report writes only its header and a zero TOTAL row.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.transactions.delete_all(min_txn_id=0)
    db.categories.delete_all(min_category="")
    db.accounts.delete_all(min_account="")
    code, out, err = cli_runner("report", "categories")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows == [
        ["category", "description", "transactions", "inflow", "outflow", "net"],
        ["TOTAL", "", "0", "0.00", "0.00", "0.00"],
    ]
=== END AC report-categories-no-categories ===

=== AC report-categories-net-negative ===
Intent: A category with only withdrawals reports zero inflow, a positive outflow, and a negative net with a leading minus sign and two decimals.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQG5"
cat = "ZQG5"
spent = 1275
with db_session() as db:
    db.accounts.create(account=acct, name="Spend Account")
    db.categories.create(category=cat, description="Spend Category")
    base = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(txn_id=base, date="2026-06-01", account=acct, category=cat, amount=-spent, memo="")
    code, out, err = cli_runner("report", "categories")
    print(out)
    print(err)
    assert code == 0
    by_code = {r[0]: r for r in csv.reader(io.StringIO(out))}
    row = by_code[cat]
    assert Decimal(row[3]) == 0
    assert Decimal(row[4]) == Decimal(spent).scaleb(-2)
    assert Decimal(row[5]) == -Decimal(spent).scaleb(-2)
    assert re.fullmatch(r"-\d+\.\d{2}", row[5])
    assert not row[4].startswith("-")
=== END AC report-categories-net-negative ===

## User Acceptance

- None.

## Guardrails

- Every value comes from a query; no row, count, or total is hardcoded.
- Amounts are integer cents; no floating point.
- The report writes nothing to the store.
