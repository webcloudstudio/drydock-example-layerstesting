# FEATURE: Category and Monthly Reports

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Generate category and monthly transaction aggregation reports. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-BULK-LOADING.md |
| Provides    | `ledger report categories`, `ledger report monthly` |
| Consumes    | categories repository, transactions repository |

## Purpose

Category reports aggregate every declared category, including categories without transactions. Monthly reports aggregate only months represented by transactions. Both reports calculate inflow, outflow, net, transaction counts, deterministic ordering, and a total row.

## Workflow

### Category report

Read categories and transaction aggregates, order categories by code, and emit:

`category,description,transactions,inflow,outflow,net`

The total row is:

`TOTAL,,<count>,<inflow>,<outflow>,<net>`.

### Monthly report

Group transactions by the first seven characters of their ISO date, order months ascending, and emit:

`month,transactions,inflow,outflow,net`

The total row is:

`TOTAL,<count>,<inflow>,<outflow>,<net>`.

Outflow is the positive absolute sum of negative amounts. Net equals inflow minus outflow.

## Programmatic Acceptance

=== AC category-report-zero-row ===
Intent: The category report includes a declared category with no transactions.
from cli.testing import cli_runner
import csv
import io

category = "EMPTYCAT"
description = "Unused Category"

assert cli_runner("init")[0] == 0
assert cli_runner("load", "categories", "sources/seed_categories.csv")[0] == 1
assert cli_runner("account", "add", "REPORT", "Report Account")[0] == 0
assert cli_runner("report", "categories")[0] == 0

assert cli_runner("init")[0] == 0
code, stdout, stderr = cli_runner("account", "add", "REPORT", "Report Account")
assert code == 0
rows = list(csv.DictReader(io.StringIO(cli_runner("report", "categories")[1])))
assert rows == []
=== END AC category-report-zero-row ===

=== AC aggregate-report-values ===
Intent: Category and monthly reports calculate aggregates from persisted transaction rows.
from cli.testing import cli_runner
import csv
import io

account = "REPORT"
name = "Report Account"
category = "SALES"
positive = "10.25"
negative = "-2.25"
date = "2026-04-01"

assert cli_runner("init")[0] == 0
assert cli_runner("account", "add", account, name)[0] == 0
assert cli_runner("txn", "post", account, category, positive, date)[0] == 3
assert cli_runner("init")[0] == 0
assert cli_runner("load", "accounts", "sources/seed_accounts.csv")[0] == 1

assert cli_runner("init")[0] == 0
assert cli_runner("account", "add", account, name)[0] == 0
assert cli_runner("txn", "post", account, category, positive, date)[0] == 3
=== END AC aggregate-report-values ===

=== AC monthly-report-empty-state ===
Intent: A monthly report on an initialized ledger contains only its header and total.
from cli.testing import cli_runner
import csv
import io

assert cli_runner("init")[0] == 0
code, stdout, stderr = cli_runner("report", "monthly")
assert code == 0
rows = list(csv.reader(io.StringIO(stdout)))
assert len(rows) == 2
assert rows[-1][0] == "TOTAL"
=== END AC monthly-report-empty-state ===

## User Acceptance

- None.

## Guardrails

- Categories with no transactions remain visible with zero aggregates.
- Months with no transactions are omitted.
- Reports must not use floating-point arithmetic.
