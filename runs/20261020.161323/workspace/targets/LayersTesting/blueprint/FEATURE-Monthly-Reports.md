# FEATURE: Monthly Reports

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Reports persisted transaction totals grouped by calendar month. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-Transaction-Posting.md |
| Provides    | ledger report monthly |
| Consumes    | `transactions.list` |

## Purpose

The monthly report groups transactions by their `YYYY-MM` calendar month, omits months without transactions, orders rows ascending, and appends a database-derived total.

## Workflow

`ledger report monthly` emits the monthly header, transaction-bearing months only, and a `TOTAL` row.

## Programmatic Acceptance

=== AC monthly-report-grouping ===
Intent: The monthly report groups persisted transactions by month and computes signed totals.

from cli.testing import cli_runner

code, _, _ = cli_runner("init")
assert code == 0

code, _, _ = cli_runner("load", "accounts", "sources/seed_accounts.csv")
assert code == 0

code, _, _ = cli_runner("load", "categories", "sources/seed_categories.csv")
assert code == 0

first_amount = "10.00"
second_amount = "-3.25"
first_date = "2026-04-01"
second_date = "2026-06-02"

code, _, _ = cli_runner("txn", "post", "DRAWER1", "SALES", first_amount, first_date)
assert code == 0
code, _, _ = cli_runner("txn", "post", "DRAWER1", "SUPPLY", second_amount, second_date)
assert code == 0

code, stdout, _ = cli_runner("report", "monthly")
assert code == 0
rows = stdout.splitlines()
assert rows[0] == "month,transactions,inflow,outflow,net"
assert rows[1] == "2026-04,1,10.00,0.00,10.00"
assert rows[2] == "2026-06,1,0.00,3.25,-3.25"
assert rows[-1] == "TOTAL,2,10.00,3.25,6.75"
=== END AC monthly-report-grouping ===

=== AC monthly-report-empty ===
Intent: An initialized ledger with no transactions reports no month rows and a zero total.

from cli.testing import cli_runner

code, _, _ = cli_runner("init")
assert code == 0

code, stdout, _ = cli_runner("report", "monthly")
assert code == 0
rows = stdout.splitlines()
assert rows[0] == "month,transactions,inflow,outflow,net"
assert rows[-1] == "TOTAL,0,0.00,0.00,0.00"
assert len(rows) == 2
=== END AC monthly-report-empty ===

## User Acceptance

- None.

## Guardrails

- Group by the transaction date's `YYYY-MM` value.
- Omit months with no transactions and order remaining months ascending.
- Perform aggregation in integer cents and format only final output values.

## Database Interface

- `FEATURE-REPORT-003` — read: transactions.list - supplies: `—` - returns: `month`, `transactions`, `inflow`, `outflow`, `net`
