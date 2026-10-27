# FEATURE: Report Monthly

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger report monthly`, the per-month transaction, inflow, outflow, and net totals computed from stored transactions. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-CliEntry.md, FEATURE-Validation.md |
| Provides | ledger report monthly |
| Consumes | ledger_core.money, cli.registry |

## Purpose

Give the shop a report of cash movement by calendar month. Every value is computed from the
database at call time; no total is embedded.

## Interface

`ledger report monthly` takes no further arguments. Extra arguments are a usage error (exit 2).

Output on success (CSV, `\n` endings, no quoting, no trailing spaces):

- Header: `month,transactions,inflow,outflow,net`
- One row per `YYYY-MM` that has at least one transaction, ascending by month. The month is the
  first seven characters of the stored date.
- `transactions` is the count of that month's transactions.
- `inflow` is the sum of positive amounts, `outflow` the sum of the absolute values of negative
  amounts (written positive), `net` is `inflow - outflow`.
- Final row `TOTAL,<count>,<inflow>,<outflow>,<net>` over all transactions.
- Amounts are computed in integer cents and written with exactly two decimals via `ledger_core.money`.
  A month with no transactions is absent. An empty ledger prints the header and a TOTAL row of zeros.

## Behavior

1. Read all transactions with `db.transactions.list(...)`.
2. Group by the first seven characters of `date` in integer cents; never use floating point.
3. Emit rows in ascending month order, then the TOTAL row.

## Database Interface

- `FEATURE-TXN-005` — read: list transactions for aggregation - supplies: — - returns: `date`, `amount`

## Programmatic Acceptance

=== AC report-monthly-rows ===
Intent: Monthly rows, ordering, and the TOTAL row are computed from posted transactions; expected counts and sums are derived from the supplied amounts with Decimal.

import csv
import io
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

def parse(out):
    return list(csv.reader(io.StringIO(out)))

acct = "ZZRM1"
cat = "ZZRMC"
with db_session() as db:
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Monthly Probe")
code, out, err = cli_runner("account", "add", acct, "Monthly Probe")
print(out, err)
assert code == 0
postings = [("2099-01-05", "100.50"), ("2099-01-20", "40.25"), ("2099-01-21", "-30.10"), ("2099-03-02", "10.00")]
for day, amount in postings:
    code, out, err = cli_runner("txn", "post", acct, cat, amount, day, "m")
    print(out, err)
    assert code == 0

code, out, err = cli_runner("report", "monthly")
print(out, err)
assert code == 0
table = parse(out)
assert table[0] == ["month", "transactions", "inflow", "outflow", "net"]
body = table[1:-1]
months = [r[0] for r in body]
assert months == sorted(months)
by_month = {r[0]: r for r in body}
assert "2099-02" not in by_month
for month in ("2099-01", "2099-03"):
    amounts = [Decimal(a) for d, a in postings if d[:7] == month]
    inflow = sum((a for a in amounts if a > 0), Decimal(0))
    outflow = sum((-a for a in amounts if a < 0), Decimal(0))
    row = by_month[month]
    assert int(row[1]) == len(amounts)
    assert Decimal(row[2]) == inflow
    assert Decimal(row[3]) == outflow
    assert Decimal(row[4]) == inflow - outflow
    for cell in row[2:]:
        assert len(cell.split(".")[1]) == 2
total = table[-1]
assert total[0] == "TOTAL" and len(total) == 5
assert int(total[1]) == sum(int(r[1]) for r in body)
assert Decimal(total[2]) == sum(Decimal(r[2]) for r in body)
assert Decimal(total[3]) == sum(Decimal(r[3]) for r in body)
assert Decimal(total[4]) == Decimal(total[2]) - Decimal(total[3])
=== END AC report-monthly-rows ===

=== AC report-monthly-usage ===
Intent: Extra arguments to report monthly are a usage error with exit 2 and nothing on standard output.

from cli.testing import cli_runner

code, out, err = cli_runner("report", "monthly", "extra")
print(out, err)
assert code == 2
assert out == ""
=== END AC report-monthly-usage ===

=== AC report-monthly-reflects-changes ===
Intent: The report is recomputed from the database: posting one more transaction in a new month adds exactly one month row with the posted amount as inflow.

import csv
import io
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

def parse(out):
    return list(csv.reader(io.StringIO(out)))

acct = "ZZRM2"
cat = "ZZRMD"
month = "2098-07"
amount = "12.34"
with db_session() as db:
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Monthly Probe")
code, out, err = cli_runner("account", "add", acct, "Monthly Probe 2")
assert code == 0
code, out, err = cli_runner("report", "monthly")
assert code == 0
before = {r[0] for r in parse(out)[1:-1]}
assert month not in before
code, out, err = cli_runner("txn", "post", acct, cat, amount, month + "-10", "m")
print(out, err)
assert code == 0
code, out, err = cli_runner("report", "monthly")
assert code == 0
rows = {r[0]: r for r in parse(out)[1:-1]}
assert set(rows) == before | {month}
assert int(rows[month][1]) == 1
assert Decimal(rows[month][2]) == Decimal(amount)
assert Decimal(rows[month][3]) == Decimal(0)
=== END AC report-monthly-reflects-changes ===

## User Acceptance

- None.

## Guardrails

- Every value comes from a database query; no row, count, or total is hardcoded.
- Money is integer cents at every layer; floating point is never used.
- A failing command writes nothing to standard output.
