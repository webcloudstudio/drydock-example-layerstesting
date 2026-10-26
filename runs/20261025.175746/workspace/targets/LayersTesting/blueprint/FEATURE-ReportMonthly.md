# FEATURE: Report Monthly

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger report monthly`, which prints inflow, outflow, and net per calendar month computed from stored transactions. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-CliFoundation.md |
| Provides | ledger report monthly |
| Consumes | transactions.list |

## Purpose

`ledger report monthly` summarizes cash movement by month. Every value is computed at run time from the stored transactions; no row, count, or total is embedded.

## Trigger

`./ledger report monthly` with no further arguments.

## Behavior

1. List all transactions through `transactions.list` (no account filter).
2. Group by the `YYYY-MM` prefix of `date`.
3. For each month that has at least one transaction, in ascending month order, compute in integer cents:
   - `transactions`: the number of transactions in the month
   - `inflow`: sum of positive amounts
   - `outflow`: sum of absolute values of negative amounts, written as a positive number
   - `net`: `inflow - outflow`
4. Write the header `month,transactions,inflow,outflow,net`, one row per month, then `TOTAL,<count>,<inflow>,<outflow>,<net>` summed over all transactions.
5. Amounts are written with exactly two decimal places, a leading `-` when negative, and no thousands separator. No floating point is used.
6. Months with no transactions are omitted. With no transactions at all, only the header and a zero `TOTAL` row are written.

## Exit Codes

| Code | Condition |
|------|-----------|
| 0 | Report written |
| 1 | Database unreachable or tables missing |
| 2 | Wrong argument count after `report monthly` |

## Database Interface

- `FEATURE-TRANSACTIONS-003` — read: list transactions - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC report-monthly-rows ===
Intent: The monthly report computes count, inflow, outflow, and net for a month from stored rows and places the month row in ascending order before TOTAL.

import csv
import io
from decimal import Decimal

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "UTRMA1"
cat = "UTRMC1"
early = "2098-05"
late = "2098-06"
early_amounts = [10000, -2550]
late_amounts = [4001]
with db_session() as db:
    db.accounts.create(account=acct, name="Monthly Probe")
    db.categories.create(category=cat, description="Monthly Probe")
    next_id = 920001
    for month, amounts in ((early, early_amounts), (late, late_amounts)):
        for cents in amounts:
            db.transactions.create(
                txn_id=next_id, date=month + "-10", account=acct,
                category=cat, amount=cents, memo="m",
            )
            next_id += 1
    code, out, err = cli_runner("report", "monthly")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["month", "transactions", "inflow", "outflow", "net"]
    assert rows[-1][0] == "TOTAL"
    body = rows[1:-1]
    months = [r[0] for r in body]
    assert months == sorted(months)
    by_month = {r[0]: r for r in body}
    for month, amounts in ((early, early_amounts), (late, late_amounts)):
        row = by_month[month]
        inflow = sum(a for a in amounts if a > 0)
        outflow = sum(-a for a in amounts if a < 0)
        assert int(row[1]) == len(amounts)
        assert Decimal(row[2]) == Decimal(inflow) / 100
        assert Decimal(row[3]) == Decimal(outflow) / 100
        assert Decimal(row[4]) == Decimal(inflow - outflow) / 100
        for cell in row[2:]:
            assert len(cell.split(".")[1]) == 2
=== END AC report-monthly-rows ===

=== AC report-monthly-total ===
Intent: The TOTAL row equals the sum of the month rows for count, inflow, outflow, and net.

import csv
import io
from decimal import Decimal

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "UTRMA2"
cat = "UTRMC2"
with db_session() as db:
    db.accounts.create(account=acct, name="Monthly Total")
    db.categories.create(category=cat, description="Monthly Total")
    db.transactions.create(
        txn_id=920101, date="2098-07-01", account=acct, category=cat, amount=12345, memo="a"
    )
    db.transactions.create(
        txn_id=920102, date="2098-08-01", account=acct, category=cat, amount=-345, memo="b"
    )
    code, out, err = cli_runner("report", "monthly")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    body, total = rows[1:-1], rows[-1]
    assert total[0] == "TOTAL"
    assert int(total[1]) == sum(int(r[1]) for r in body)
    for col in (2, 3, 4):
        assert Decimal(total[col]) == sum(Decimal(r[col]) for r in body)
    assert Decimal(total[4]) == Decimal(total[2]) - Decimal(total[3])
=== END AC report-monthly-total ===

=== AC report-monthly-total-count ===
Intent: The TOTAL transaction count equals the number of stored transactions read back from the database.

import csv
import io

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    code, out, err = cli_runner("report", "monthly")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[-1][0] == "TOTAL"
    assert int(rows[-1][1]) == len(db.transactions.list())
=== END AC report-monthly-total-count ===

=== AC report-monthly-usage ===
Intent: Extra arguments and an unknown report name exit 2 with nothing on standard output.

from cli.testing import cli_runner

code, out, err = cli_runner("report", "monthly", "extra")
assert code == 2
assert out == ""
code, out, err = cli_runner("report", "nosuchreport")
assert code == 2
assert out == ""
=== END AC report-monthly-usage ===

## User Acceptance

- None.

## Guardrails

- Every value is computed from stored rows; no month, count, or total is hardcoded.
- Amounts are integer cents internally; floating point is never used.
- Failures write nothing to standard output.
