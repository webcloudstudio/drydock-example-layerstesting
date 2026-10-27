# FEATURE: Report Monthly

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger report monthly`, per-month transaction counts with inflow, outflow, and net computed from stored transactions. |
| Depends On | FEATURE-ReportBalances.md, FEATURE-LedgerCli.md, DATABASE.md |
| Provides | ledger report monthly |
| Consumes | ledger, transactions |

## Purpose

Show how cash moved month by month.

## Interface

`ledger report monthly`

Standard output on success (exit 0):

- header `month,transactions,inflow,outflow,net`
- one row per `YYYY-MM` that has at least one transaction, ascending
- final row `TOTAL,<count>,<inflow>,<outflow>,<net>`

## Behavior

1. Read transactions with `db.transactions.list` and group them by the first seven characters of `date`.
2. `inflow` is the sum of positive amounts; `outflow` the sum of absolute values of negative amounts, written positive; `net` is `inflow - outflow`.
3. All amounts are integer cents written with exactly two decimals and no thousands separator.
4. Months without transactions produce no row.
5. With no transactions the output is the header and `TOTAL,0,0.00,0.00,0.00`.
6. The command is read-only.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC report-monthly-rows ===
Intent: Months are grouped from the stored transaction dates, listed ascending with count, inflow, outflow, and net, and the TOTAL row sums the columns; the fixtures are inserted out of date order and skip a month.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQM1"
cat = "ZQM1"
with db_session() as db:
    db.accounts.create(account=acct, name="Month Account")
    db.categories.create(category=cat, description="Month Category")
    base = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(txn_id=base, date="2031-09-01", account=acct, category=cat, amount=30000, memo="")
    db.transactions.create(txn_id=base + 1, date="2031-07-31", account=acct, category=cat, amount=50025, memo="")
    db.transactions.create(txn_id=base + 2, date="2031-09-20", account=acct, category=cat, amount=-1250, memo="")
    db.transactions.create(txn_id=base + 3, date="2031-07-05", account=acct, category=cat, amount=-300, memo="")
    count_before = len(db.transactions.list())
    code, out, err = cli_runner("report", "monthly")
    print(out)
    print(err)
    assert code == 0
    assert "\r" not in out
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["month", "transactions", "inflow", "outflow", "net"]
    all_txns = db.transactions.list()
    months = sorted({t.date[:7] for t in all_txns})
    data = rows[1:-1]
    assert [r[0] for r in data] == months
    assert "2031-08" not in months
    total_n = total_in = total_out = 0
    for row, month in zip(data, months):
        mine = [t.amount for t in all_txns if t.date[:7] == month]
        inflow = sum(a for a in mine if a > 0)
        outflow = sum(-a for a in mine if a < 0)
        assert int(row[1]) == len(mine)
        assert Decimal(row[2]) == Decimal(inflow).scaleb(-2)
        assert Decimal(row[3]) == Decimal(outflow).scaleb(-2)
        assert Decimal(row[4]) == Decimal(inflow - outflow).scaleb(-2)
        for cell in row[2:]:
            assert re.fullmatch(r"-?\d+\.\d{2}", cell)
        total_n += len(mine)
        total_in += inflow
        total_out += outflow
    total = rows[-1]
    assert total[0] == "TOTAL"
    assert int(total[1]) == total_n == len(all_txns)
    assert Decimal(total[2]) == Decimal(total_in).scaleb(-2)
    assert Decimal(total[3]) == Decimal(total_out).scaleb(-2)
    assert Decimal(total[4]) == Decimal(total_in - total_out).scaleb(-2)
    assert len(db.transactions.list()) == count_before
=== END AC report-monthly-rows ===

=== AC report-monthly-empty-ledger ===
Intent: With no transactions the report writes only its header and a zero TOTAL row.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.transactions.delete_all(min_txn_id=0)
    code, out, err = cli_runner("report", "monthly")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows == [
        ["month", "transactions", "inflow", "outflow", "net"],
        ["TOTAL", "0", "0.00", "0.00", "0.00"],
    ]
=== END AC report-monthly-empty-ledger ===

=== AC report-monthly-negative-net ===
Intent: A month containing only withdrawals reports zero inflow, a positive outflow, and a negative net.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQM2"
cat = "ZQM2"
spent = 987
with db_session() as db:
    db.transactions.delete_all(min_txn_id=0)
    db.accounts.create(account=acct, name="Month Account")
    db.categories.create(category=cat, description="Month Category")
    db.transactions.create(txn_id=1, date="2032-01-15", account=acct, category=cat, amount=-spent, memo="")
    code, out, err = cli_runner("report", "monthly")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert len(rows) == 3
    month_row = rows[1]
    assert month_row[0] == db.transactions.get(txn_id=1).date[:7]
    assert int(month_row[1]) == 1
    assert Decimal(month_row[2]) == 0
    assert Decimal(month_row[3]) == Decimal(spent).scaleb(-2)
    assert Decimal(month_row[4]) == -Decimal(spent).scaleb(-2)
    assert re.fullmatch(r"-\d+\.\d{2}", month_row[4])
=== END AC report-monthly-negative-net ===

## User Acceptance

- None.

## Guardrails

- Every value comes from a query; no row, count, or total is hardcoded.
- Amounts are integer cents; no floating point.
- The report writes nothing to the store.
