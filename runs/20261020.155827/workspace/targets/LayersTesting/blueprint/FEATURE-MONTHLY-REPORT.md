# FEATURE: Monthly Report

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Reports transaction totals grouped by calendar month. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-ACCOUNT-OPERATIONS.md, FEATURE-TRANSACTION-OPERATIONS.md |
| Provides    | `ledger report monthly` |
| Consumes    | ledger persistence operations |

## Purpose

The monthly report groups transactions by `YYYY-MM`, orders months ascending, and reports transaction count, inflow, outflow, and net. Months without transactions are omitted, followed by a computed `TOTAL` row.

## Workflow

1. Query transactions through the persistence boundary.
2. Group integer-cent amounts by calendar month.
3. Order months ascending.
4. Format the computed rows as CSV.

## Programmatic Acceptance

=== AC monthly-report ===
Intent: The monthly report groups transactions by month and computes the total row from stored transactions.

from cli.testing import cli_runner

code, out, err = cli_runner("init")
assert code == 0
code, out, err = cli_runner("load", "accounts", "sources/seed_accounts.csv")
assert code == 0
code, out, err = cli_runner("load", "categories", "sources/seed_categories.csv")
assert code == 0

transactions = [
    ("DRAWER1", "SALES", "10.00", "2026-01-01"),
    ("DRAWER1", "SALES", "5.50", "2026-03-01"),
]
for account, category, amount, date in transactions:
    code, out, err = cli_runner("txn", "post", account, category, amount, date)
    assert code == 0

code, out, err = cli_runner("report", "monthly")
assert code == 0
rows = [line.split(",") for line in out.strip().splitlines()]
assert rows[0] == ["month", "transactions", "inflow", "outflow", "net"]
months = [row[0] for row in rows[1:-1]]
assert months == sorted(months)
assert months == ["2026-01", "2026-03"]
assert rows[1][1:] == ["1", "10.00", "0.00", "10.00"]
assert rows[2][1:] == ["1", "5.50", "0.00", "5.50"]
assert rows[-1] == ["TOTAL", "2", "15.50", "0.00", "15.50"]
=== END AC monthly-report ===

## User Acceptance

- None.

## Guardrails

- Only months containing transactions appear.
- Month ordering is ascending.
- Report values are computed from stored integer cents.
