# FEATURE: Categories Report

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Reports inflow, outflow, and net per category, including categories with no transactions, then a TOTAL row, computed from the database. |
| Depends On  | FEATURE-LOAD-TRANSACTIONS.md, FEATURE-TRANSFER.md, FEATURE-TXN-DELETE.md, FEATURE-CSV-OUTPUT.md |
| Provides    | ledger report categories |

## Purpose

`ledger report categories` writes `category,description,transactions,inflow,outflow,net` for every category ordered by code, followed by `TOTAL,,<count>,<inflow>,<outflow>,<net>`.

## Behavior

1. Read every category and every transaction from the database.
2. For each category, count its transactions, sum positive amounts as `inflow`, and sum the absolute values of negative amounts as `outflow`.
3. Compute `net` as `inflow - outflow`.
4. Write one row per category ordered by code, including categories with no transactions, then the TOTAL row.

When no categories exist, only the header and the TOTAL row are written, with zeros in every numeric column.

## Programmatic Acceptance

=== AC report-categories-match-database ===
Intent: Each categories row and the TOTAL row equal values computed from the categories and transactions read back from the database.

import csv
import io
import os
import tempfile
from decimal import Decimal

from cli.testing import cli_runner
from persistence import open_database

os.environ["DATABASE_URL"] = os.path.join(tempfile.mkdtemp(), "ledger.db")
for args in (
    ("init",),
    ("load", "accounts", "sources/seed_accounts.csv"),
    ("load", "categories", "sources/seed_categories.csv"),
    ("load", "transactions", "sources/seed_transactions.csv"),
):
    code, out, err = cli_runner(*args)
    assert code == 0, err

db = open_database(os.environ["DATABASE_URL"])
categories = list(db.categories.list())
transactions = list(db.transactions.list())

code, out, err = cli_runner("report", "categories")
assert code == 0, err
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["category", "description", "transactions", "inflow", "outflow", "net"]
body, total = rows[1:-1], rows[-1]

codes = [row[0] for row in body]
assert codes == sorted(codes)
assert codes == sorted(category.category for category in categories)
for row in body:
    category = next(item for item in categories if item.category == row[0])
    mine = [txn for txn in transactions if txn.category == row[0]]
    inflow = sum(txn.amount for txn in mine if txn.amount > 0)
    outflow = sum(-txn.amount for txn in mine if txn.amount < 0)
    assert row[1] == category.description
    assert int(row[2]) == len(mine)
    assert int(Decimal(row[3]).scaleb(2)) == inflow
    assert int(Decimal(row[4]).scaleb(2)) == outflow
    assert int(Decimal(row[5]).scaleb(2)) == inflow - outflow

all_inflow = sum(txn.amount for txn in transactions if txn.amount > 0)
all_outflow = sum(-txn.amount for txn in transactions if txn.amount < 0)
assert total[0] == "TOTAL" and total[1] == ""
assert int(total[2]) == len(transactions)
assert int(Decimal(total[3]).scaleb(2)) == all_inflow
assert int(Decimal(total[4]).scaleb(2)) == all_outflow
assert int(Decimal(total[5]).scaleb(2)) == all_inflow - all_outflow
=== END AC report-categories-match-database ===

=== AC report-categories-lists-empty-categories ===
Intent: A category with no transactions still appears in the categories report with zero counts and sums.

import csv
import io
import os
import tempfile
from decimal import Decimal

from cli.testing import cli_runner
from persistence import open_database

os.environ["DATABASE_URL"] = os.path.join(tempfile.mkdtemp(), "ledger.db")
for args in (
    ("init",),
    ("load", "categories", "sources/seed_categories.csv"),
):
    code, out, err = cli_runner(*args)
    assert code == 0, err

db = open_database(os.environ["DATABASE_URL"])
categories = list(db.categories.list())

code, out, err = cli_runner("report", "categories")
assert code == 0, err
rows = list(csv.reader(io.StringIO(out)))
body, total = rows[1:-1], rows[-1]
assert len(body) == len(categories)
for row in body:
    assert int(row[2]) == 0
    assert int(Decimal(row[3]).scaleb(2)) == 0
    assert int(Decimal(row[4]).scaleb(2)) == 0
    assert int(Decimal(row[5]).scaleb(2)) == 0
assert total[0] == "TOTAL"
assert int(total[2]) == 0
=== END AC report-categories-lists-empty-categories ===

=== AC report-categories-empty-ledger ===
Intent: With no categories, the categories report writes only the header and a TOTAL row of zeros.

import csv
import io
import os
import tempfile
from decimal import Decimal

from cli.testing import cli_runner

os.environ["DATABASE_URL"] = os.path.join(tempfile.mkdtemp(), "ledger.db")
code, out, err = cli_runner("init")
assert code == 0, err

code, out, err = cli_runner("report", "categories")
assert code == 0, err
rows = list(csv.reader(io.StringIO(out)))
assert len(rows) == 2
assert rows[0] == ["category", "description", "transactions", "inflow", "outflow", "net"]
assert rows[1][0] == "TOTAL"
assert int(rows[1][2]) == 0
assert int(Decimal(rows[1][3]).scaleb(2)) == 0
assert int(Decimal(rows[1][4]).scaleb(2)) == 0
assert int(Decimal(rows[1][5]).scaleb(2)) == 0
=== END AC report-categories-empty-ledger ===

## User Acceptance

- None.

## Guardrails

- Every value in the report is computed from a database query; no category, count, or total is hardcoded.
- Outflow is written as a positive number.
