# FEATURE: Category Report

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Reports transaction totals grouped by category. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-ACCOUNT-OPERATIONS.md, FEATURE-TRANSACTION-OPERATIONS.md |
| Provides    | `ledger report categories` |
| Consumes    | ledger persistence operations |

## Purpose

The category report lists every declared category, including categories without transactions, ordered by category code. Each row includes transaction count, positive inflow, positive outflow, and net amount. A computed `TOTAL` row follows all categories.

## Workflow

1. Query categories and transactions through the persistence boundary.
2. Aggregate integer-cent amounts by category.
3. Format amounts with exactly two decimal places.
4. Emit CSV with no hardcoded report values.

## Programmatic Acceptance

=== AC category-report ===
Intent: The category report includes unused categories and computes category and total aggregates from stored transactions.

from cli.testing import cli_runner

code, out, err = cli_runner("init")
assert code == 0

code, out, err = cli_runner("account", "add", "A1", "Main")
assert code == 0
code, out, err = cli_runner("category", "add", "USED", "Used")
assert code != 0

code, out, err = cli_runner("load", "categories", "sources/seed_categories.csv")
assert code == 0

code, out, err = cli_runner("txn", "post", "A1", "SALES", "10.00", "2026-01-01")
assert code == 0
code, out, err = cli_runner("report", "categories")
assert code == 0

rows = [line.split(",") for line in out.strip().splitlines()]
assert rows[0] == ["category", "description", "transactions", "inflow", "outflow", "net"]
category_codes = [row[0] for row in rows[1:-1]]
assert category_codes == sorted(category_codes)
assert any(row[0] == "OPENING" and row[2] == "0" for row in rows[1:-1])
sales = next(row for row in rows[1:-1] if row[0] == "SALES")
assert sales[2] == "1"
assert sales[3] == "10.00"
assert sales[4] == "0.00"
assert sales[5] == "10.00"
total = rows[-1]
assert total[0] == "TOTAL"
assert total[2] == "1"
assert total[3] == "10.00"
assert total[4] == "0.00"
assert total[5] == "10.00"
=== END AC category-report ===

## User Acceptance

- None.

## Guardrails

- Categories with no transactions remain visible.
- All totals come from database queries.
- Amounts remain integer cents internally and never use floating point.
