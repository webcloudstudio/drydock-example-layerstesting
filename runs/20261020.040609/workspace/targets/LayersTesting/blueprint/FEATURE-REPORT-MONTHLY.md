# FEATURE: Monthly Report

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Reports transaction count, inflow, outflow, and net per calendar month, then a TOTAL row, computed from the database. |
| Depends On  | FEATURE-LOAD-TRANSACTIONS.md, FEATURE-TRANSFER.md, FEATURE-TXN-DELETE.md, FEATURE-CSV-OUTPUT.md |
| Provides    | ledger report monthly |

## Purpose

`ledger report monthly` writes `month,transactions,inflow,outflow,net` for every `YYYY-MM` that has transactions, in ascending order, followed by `TOTAL,<count>,<inflow>,<outflow>,<net>`.

## Behavior

1. Read every transaction from the database.
2. Group transactions by the `YYYY-MM` prefix of their date.
3. For each month, count its transactions, sum positive amounts as `inflow`, sum the absolute values of negative amounts as `outflow`, and compute `net` as `inflow - outflow`.
4. Write one row per month ascending, then the TOTAL row over all transactions.

When no transactions exist, only the header and the TOTAL row are written, with zeros in every numeric column.

## Programmatic Acceptance

=== AC report-monthly-match-database ===
Intent: Each monthly row and the TOTAL row equal values computed from the transactions read back from the database, with months ascending.

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
transactions = list(db.transactions.list())

code, out, err = cli_runner("report", "monthly")
assert code == 0, err
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["month", "transactions", "inflow", "outflow", "net"]
body, total = rows[1:-1], rows[-1]

months = [row[0] for row in body]
assert months == sorted({txn.date[:7] for txn in transactions})
for row in body:
    mine = [txn for txn in transactions if txn.date[:7] == row[0]]
    inflow = sum(txn.amount for txn in mine if txn.amount > 0)
    outflow = sum(-txn.amount for txn in mine if txn.amount < 0)
    assert int(row[1]) == len(mine)
    assert int(Decimal(row[2]).scaleb(2)) == inflow
    assert int(Decimal(row[3]).scaleb(2)) == outflow
    assert int(Decimal(row[4]).scaleb(2)) == inflow - outflow

all_inflow = sum(txn.amount for txn in transactions if txn.amount > 0)
all_outflow = sum(-txn.amount for txn in transactions if txn.amount < 0)
assert total[0] == "TOTAL"
assert int(total[1]) == len(transactions)
assert int(Decimal(total[2]).scaleb(2)) == all_inflow
assert int(Decimal(total[3]).scaleb(2)) == all_outflow
assert int(Decimal(total[4]).scaleb(2)) == all_inflow - all_outflow
=== END AC report-monthly-match-database ===

=== AC report-monthly-empty-ledger ===
Intent: With no transactions, the monthly report writes only the header and a TOTAL row of zeros.

import csv
import io
import os
import tempfile
from decimal import Decimal

from cli.testing import cli_runner

os.environ["DATABASE_URL"] = os.path.join(tempfile.mkdtemp(), "ledger.db")
code, out, err = cli_runner("init")
assert code == 0, err

code, out, err = cli_runner("report", "monthly")
assert code == 0, err
rows = list(csv.reader(io.StringIO(out)))
assert len(rows) == 2
assert rows[0] == ["month", "transactions", "inflow", "outflow", "net"]
assert rows[1][0] == "TOTAL"
assert int(rows[1][1]) == 0
assert int(Decimal(rows[1][2]).scaleb(2)) == 0
assert int(Decimal(rows[1][3]).scaleb(2)) == 0
assert int(Decimal(rows[1][4]).scaleb(2)) == 0
=== END AC report-monthly-empty-ledger ===

## User Acceptance

- None.

## Guardrails

- Every value in the report is computed from a database query; no month, count, or total is hardcoded.
- Months with no transactions are omitted rather than written with zeros.
