# FEATURE: Balance Reports

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Reports persisted account balances, transaction counts, and ledger totals. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-Accounts.md, FEATURE-Transaction-Posting.md, FEATURE-Transaction-Mutation.md, FEATURE-Transfers.md |
| Provides    | ledger report balances |
| Consumes    | `accounts.list`, `transactions.list` |

## Purpose

The balances report reads every account and its persisted transactions, orders accounts by code, formats balances as decimal currency, and appends a database-derived total row.

## Workflow

`ledger report balances` emits the header, one row per account ordered by account code, and `TOTAL,,<transaction count>,<sum>`.

Empty ledgers still emit the header and zero-valued total row.

## Programmatic Acceptance

=== AC balances-report-round-trip ===
Intent: The balances command reports accounts, counts, balances, and a total from persisted state.

from cli.testing import cli_runner

code, _, _ = cli_runner("init")
assert code == 0

account_code = "REPORT1"
account_name = "Report Drawer"
category_code = "SALES"
amount = "12.34"
date = "2026-04-01"

code, _, _ = cli_runner("load", "accounts", "sources/seed_accounts.csv")
assert code == 0

code, _, _ = cli_runner("load", "categories", "sources/seed_categories.csv")
assert code == 0

code, _, _ = cli_runner("account", "add", account_code, account_name)
assert code == 0

code, _, _ = cli_runner("txn", "post", account_code, category_code, amount, date)
assert code == 0

code, stdout, _ = cli_runner("report", "balances")
assert code == 0
rows = stdout.splitlines()
assert rows[0] == "account,name,transactions,balance"
assert any(row.startswith(f"{account_code},{account_name},1,") for row in rows)
assert rows[-1].startswith("TOTAL,,")
=== END AC balances-report-round-trip ===

=== AC balances-report-empty ===
Intent: An initialized empty ledger produces a valid zero-row balances report.

from cli.testing import cli_runner

code, _, _ = cli_runner("init")
assert code == 0

code, stdout, _ = cli_runner("report", "balances")
assert code == 0
rows = stdout.splitlines()
assert rows[0] == "account,name,transactions,balance"
assert rows[-1] == "TOTAL,,0,0.00"
=== END AC balances-report-empty ===

## User Acceptance

- None.

## Guardrails

- Compute every value from persisted queries; do not hardcode report rows or totals.
- Use integer cents for all aggregation and format currency only at the CLI boundary.
- Emit accounts ordered by account code and include the total row.

## Database Interface

- `FEATURE-REPORT-001` — read: accounts.list - supplies: `—` - returns: `account`, `name`, `transactions`, `balance`
