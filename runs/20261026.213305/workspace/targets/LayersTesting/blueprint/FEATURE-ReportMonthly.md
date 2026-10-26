# FEATURE: Report Monthly

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | The `ledger report monthly` command that reports inflow, outflow and net per calendar month from stored data. |
| Depends On | FEATURE-LoadTransactions.md, FEATURE-Transfer.md, FEATURE-CsvOutput.md, DATABASE.md |
| Provides | ledger report monthly |
| Consumes | ledger.register_command, persistence.open_database, csv_output.write_rows, csv_output.format_cents |

## Purpose

`ledger report monthly` writes one row per `YYYY-MM` that has transactions, in ascending order, then a total row. Every value is computed from stored transactions in integer cents.

## Behavior

- Header: `month,transactions,inflow,outflow,net`.
- The month is the first seven characters of each transaction date. Months with no transactions are not listed.
- `inflow` sums positive amounts, `outflow` sums the absolute values of negative amounts as a positive number, `net` is `inflow - outflow`.
- Final row: `TOTAL,<count>,<inflow>,<outflow>,<net>`. A zero amount is written `0.00`, never `-0.00`.
- On an empty ledger the output is the header and `TOTAL,0,0.00,0.00,0.00`.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC report-monthly-seeded ===
Intent: Monthly totals over the loaded seed data match values derived from the seed files in ascending month order.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner

with open("sources/seed_transactions.csv", newline="") as fh:
    txns = list(csv.DictReader(fh))

for args in (
    ("init",),
    ("load", "accounts", "sources/seed_accounts.csv"),
    ("load", "categories", "sources/seed_categories.csv"),
    ("load", "transactions", "sources/seed_transactions.csv"),
):
    code, out, err = cli_runner(*args)
    print(out, err)
    assert code == 0

stats = {}
for t in txns:
    cents = int(Decimal(t["amount"]) * 100)
    s = stats.setdefault(t["date"][:7], [0, 0, 0])
    s[0] += 1
    if cents > 0:
        s[1] += cents
    else:
        s[2] += -cents

def money(field):
    assert re.fullmatch(r"-?\d+\.\d\d", field)
    return Decimal(field) * 100

code, out, err = cli_runner("report", "monthly")
print(out, err)
assert code == 0
assert "\r" not in out and out.endswith("\n")
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["month", "transactions", "inflow", "outflow", "net"]
months = sorted(stats)
assert [r[0] for r in rows[1:-1]] == months
for r in rows[1:-1]:
    count, inflow, outflow = stats[r[0]]
    assert int(r[1]) == count
    assert money(r[2]) == inflow
    assert money(r[3]) == outflow
    assert money(r[4]) == inflow - outflow
total = rows[-1]
assert total[0] == "TOTAL"
assert int(total[1]) == len(txns)
assert money(total[2]) == sum(s[1] for s in stats.values())
assert money(total[3]) == sum(s[2] for s in stats.values())
assert money(total[4]) == sum(s[1] - s[2] for s in stats.values())
=== END AC report-monthly-seeded ===

=== AC report-monthly-empty ===
Intent: On an empty ledger the report writes its header and an all-zero total row.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner

code, out, err = cli_runner("init")
assert code == 0
code, out, err = cli_runner("report", "monthly")
print(out, err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["month", "transactions", "inflow", "outflow", "net"]
assert len(rows) == 2
assert rows[1][0] == "TOTAL"
assert int(rows[1][1]) == 0
for field in rows[1][2:]:
    assert re.fullmatch(r"0\.00", field)
    assert Decimal(field) == 0
=== END AC report-monthly-empty ===

=== AC report-monthly-after-transfer ===
Intent: A transfer in a new month adds that month with two transactions, equal inflow and outflow and zero net.

import csv
import io
from decimal import Decimal
from cli.testing import cli_runner

amount = "500.00"
new_month = "2026-04"
day = new_month + "-03"

for args in (
    ("init",),
    ("load", "accounts", "sources/seed_accounts.csv"),
    ("load", "categories", "sources/seed_categories.csv"),
    ("load", "transactions", "sources/seed_transactions.csv"),
):
    code, out, err = cli_runner(*args)
    assert code == 0

def monthly():
    code, out, err = cli_runner("report", "monthly")
    print(out, err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    return rows[1:-1], rows[-1]

before_rows, before_total = monthly()
assert new_month not in [r[0] for r in before_rows]

code, out, err = cli_runner("transfer", "DRAWER1", "SAFE", amount, day)
print(out, err)
assert code == 0

after_rows, after_total = monthly()
months = [r[0] for r in after_rows]
assert months == sorted(months)
assert months[-1] == new_month
row = after_rows[-1]
assert int(row[1]) == 2
assert Decimal(row[2]) == Decimal(amount)
assert Decimal(row[3]) == Decimal(amount)
assert Decimal(row[4]) == 0
assert int(after_total[1]) == int(before_total[1]) + 2
assert Decimal(after_total[4]) == Decimal(before_total[4])
=== END AC report-monthly-after-transfer ===

## User Acceptance

- None.

## Guardrails

- Every value is computed from stored data; no month row or total is embedded.
- Money is integer cents; no floating point at any layer.
- Only months that have transactions are listed.
