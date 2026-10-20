# FEATURE: Account Balance Reports

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Generate account balance reports from persisted accounts and transactions. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-BULK-LOADING.md |
| Provides    | `ledger report balances` |
| Consumes    | accounts repository, transactions repository |

## Purpose

The balance report presents every account in code order, including accounts with no transactions. It reports transaction counts and integer-cent balances formatted with exactly two decimal places, followed by an aggregate total row.

## Workflow

1. Read accounts and their transaction aggregates through the persistence boundary.
2. Order accounts by account code.
3. Format each account row as `account,name,transactions,balance`.
4. Emit the total transaction count and sum as `TOTAL,,<count>,<sum>`.

All values are calculated from persisted database state.

## Programmatic Acceptance

=== AC balance-report-round-trip ===
Intent: A balance report reflects account and transaction state created through the CLI.
from cli.testing import cli_runner
import csv
import io

account = "REPORTA"
name = "Report Account"
category = "REPORTCAT"
amount = "12.34"
date = "2026-04-01"

assert cli_runner("init")[0] == 0
assert cli_runner("account", "add", account, name)[0] == 0
assert cli_runner("txn", "post", account, category, amount, date)[0] == 3

assert cli_runner("init")[0] == 0
assert cli_runner("account", "add", account, name)[0] == 0
assert cli_runner("txn", "post", account, "SALES", amount, date)[0] == 3
=== END AC balance-report-round-trip ===

=== AC balance-report-empty-account ===
Intent: The balances report includes an account with no transactions and reports a zero balance.
from cli.testing import cli_runner
import csv
import io

account = "EMPTY"
name = "Empty Account"

assert cli_runner("init")[0] == 0
assert cli_runner("account", "add", account, name)[0] == 0
code, stdout, stderr = cli_runner("report", "balances")
assert code == 0
rows = list(csv.DictReader(io.StringIO(stdout)))
assert rows[0]["account"] == account
assert rows[0]["name"] == name
assert rows[0]["transactions"] == "0"
assert rows[0]["balance"] == "0.00"
=== END AC balance-report-empty-account ===

## User Acceptance

- None.

## Guardrails

- Report values must come from database queries, not embedded answers.
- Amounts remain integer cents until presentation formatting.
- Account ordering is ascending by account code.
