# FEATURE: Category Reports

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Reports persisted transaction totals for every category, including unused categories. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-Transaction-Posting.md |
| Provides    | ledger report categories |
| Consumes    | `categories.list`, `transactions.list` |

## Purpose

The category report aggregates transactions by category while retaining categories with no transactions. It reports transaction count, inflow, outflow, and net values in integer cents formatted as currency.

## Workflow

`ledger report categories` emits categories ordered by code followed by a database-derived `TOTAL` row.

## Programmatic Acceptance

=== AC category-report-includes-unused ===
Intent: The category report includes unused categories and derives totals from persisted transactions.

from cli.testing import cli_runner

code, _, _ = cli_runner("init")
assert code == 0

code, _, _ = cli_runner("load", "accounts", "sources/seed_accounts.csv")
assert code == 0

code, _, _ = cli_runner("load", "categories", "sources/seed_categories.csv")
assert code == 0

code, _, _ = cli_runner("txn", "post", "DRAWER1", "SALES", "25.00", "2026-04-01")
assert code == 0

code, stdout, _ = cli_runner("report", "categories")
assert code == 0
rows = stdout.splitlines()
assert rows[0] == "category,description,transactions,inflow,outflow,net"
assert any(row.startswith("SALES,Sales receipts,") for row in rows)
assert any(row.startswith("OPENING,Opening balance,0,0.00,0.00,0.00") for row in rows)
assert rows[-1].startswith("TOTAL,,")
=== END AC category-report-includes-unused ===

=== AC category-report-empty ===
Intent: An initialized ledger with categories but no transactions reports zero-valued category totals.

from cli.testing import cli_runner

code, _, _ = cli_runner("init")
assert code == 0

code, _, _ = cli_runner("load", "categories", "sources/seed_categories.csv")
assert code == 0

code, stdout, _ = cli_runner("report", "categories")
assert code == 0
rows = stdout.splitlines()
assert rows[0] == "category,description,transactions,inflow,outflow,net"
assert len(rows) == 9
assert rows[-1] == "TOTAL,,0,0.00,0.00,0.00"
=== END AC category-report-empty ===

## User Acceptance

- None.

## Guardrails

- Include every persisted category, even when it has no transactions.
- Compute inflow, outflow, and net from integer-cent transaction amounts.
- Order category rows by category code and derive the total row from queried data.

## Database Interface

- `FEATURE-REPORT-002` — read: categories.list - supplies: `—` - returns: `category`, `description`, `transactions`, `inflow`, `outflow`, `net`
