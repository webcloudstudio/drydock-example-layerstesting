# FEATURE: Report Categories

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | The `ledger report categories` command that reports inflow, outflow and net per category from stored data. |
| Depends On | FEATURE-LoadTransactions.md, FEATURE-Transfer.md, FEATURE-CsvOutput.md, DATABASE.md |
| Provides | ledger report categories |
| Consumes | ledger.register_command, persistence.open_database, csv_output.write_rows, csv_output.format_cents |

## Purpose

`ledger report categories` writes one row per category with its transaction count, inflow, outflow and net, then a total row. Every value is computed from stored transactions in integer cents.

## Behavior

- Header: `category,description,transactions,inflow,outflow,net`.
- One row per category ordered by code in byte order, including categories with no transactions (count 0 and all amounts 0.00).
- `inflow` is the sum of positive amounts, `outflow` is the sum of the absolute values of negative amounts written as a positive number, and `net` is `inflow - outflow`.
- Final row: `TOTAL,,<count>,<inflow>,<outflow>,<net>` over all categories. A zero amount is written `0.00`, never `-0.00`.
- Amounts have exactly two decimals and no thousands separator.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC report-categories-seeded ===
Intent: Category totals over the loaded seed data match values derived from the seed files, including an unused category sorted first.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

with open("sources/seed_categories.csv", newline="") as fh:
    cats = {r["category"]: r["description"] for r in csv.DictReader(fh)}
with open("sources/seed_transactions.csv", newline="") as fh:
    txns = list(csv.DictReader(fh))

extra_code, extra_desc = "9UNUSED", "Unused Category"

for args in (
    ("init",),
    ("load", "accounts", "sources/seed_accounts.csv"),
    ("load", "categories", "sources/seed_categories.csv"),
    ("load", "transactions", "sources/seed_transactions.csv"),
):
    code, out, err = cli_runner(*args)
    print(out, err)
    assert code == 0

with db_session() as db:
    db.categories.create(category=extra_code, description=extra_desc)
cats[extra_code] = extra_desc

stats = {c: [0, 0, 0] for c in cats}
for t in txns:
    cents = int(Decimal(t["amount"]) * 100)
    s = stats[t["category"]]
    s[0] += 1
    if cents > 0:
        s[1] += cents
    else:
        s[2] += -cents

def money(field):
    assert re.fullmatch(r"-?\d+\.\d\d", field)
    return Decimal(field) * 100

code, out, err = cli_runner("report", "categories")
print(out, err)
assert code == 0
assert "\r" not in out and out.endswith("\n")
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["category", "description", "transactions", "inflow", "outflow", "net"]
codes = sorted(cats)
assert [r[0] for r in rows[1:-1]] == codes
assert codes[0] == extra_code
for r in rows[1:-1]:
    count, inflow, outflow = stats[r[0]]
    assert r[1] == cats[r[0]]
    assert int(r[2]) == count
    assert money(r[3]) == inflow
    assert money(r[4]) == outflow
    assert money(r[5]) == inflow - outflow
total = rows[-1]
assert total[0] == "TOTAL" and total[1] == ""
assert int(total[2]) == len(txns)
assert money(total[3]) == sum(s[1] for s in stats.values())
assert money(total[4]) == sum(s[2] for s in stats.values())
assert money(total[5]) == sum(s[1] - s[2] for s in stats.values())
=== END AC report-categories-seeded ===

=== AC report-categories-empty ===
Intent: With categories loaded and no transactions every category row and the total are zero.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner

with open("sources/seed_categories.csv", newline="") as fh:
    cats = [r["category"] for r in csv.DictReader(fh)]

for args in (("init",), ("load", "categories", "sources/seed_categories.csv")):
    code, out, err = cli_runner(*args)
    assert code == 0

code, out, err = cli_runner("report", "categories")
print(out, err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["category", "description", "transactions", "inflow", "outflow", "net"]
assert [r[0] for r in rows[1:-1]] == sorted(cats)
for r in rows[1:]:
    assert int(r[2]) == 0
    for field in r[3:]:
        assert re.fullmatch(r"0\.00", field)
        assert Decimal(field) == 0
assert rows[-1][0] == "TOTAL" and rows[-1][1] == ""
=== END AC report-categories-empty ===

=== AC report-categories-after-transfer ===
Intent: A transfer adds equal inflow and outflow to category TRANSFER and leaves its net unchanged.

import csv
import io
from decimal import Decimal
from cli.testing import cli_runner

amount = "250.00"

for args in (
    ("init",),
    ("load", "accounts", "sources/seed_accounts.csv"),
    ("load", "categories", "sources/seed_categories.csv"),
    ("load", "transactions", "sources/seed_transactions.csv"),
):
    code, out, err = cli_runner(*args)
    assert code == 0

def transfer_row():
    code, out, err = cli_runner("report", "categories")
    print(out, err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    return [r for r in rows if r[0] == "TRANSFER"][0]

before = transfer_row()
code, out, err = cli_runner("transfer", "DRAWER2", "SAFE", amount, "2026-04-03")
print(out, err)
assert code == 0
after = transfer_row()
assert int(after[2]) == int(before[2]) + 2
assert Decimal(after[3]) == Decimal(before[3]) + Decimal(amount)
assert Decimal(after[4]) == Decimal(before[4]) + Decimal(amount)
assert Decimal(after[5]) == Decimal(before[5])
=== END AC report-categories-after-transfer ===

## User Acceptance

- None.

## Guardrails

- Every value is computed from stored data; no category row or total is embedded.
- Money is integer cents; no floating point at any layer.
- Categories with no transactions still appear.
