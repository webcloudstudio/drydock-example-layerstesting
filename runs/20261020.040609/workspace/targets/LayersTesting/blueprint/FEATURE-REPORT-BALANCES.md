# FEATURE: Balances Report

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Reports each account's transaction count and balance, then a TOTAL row, computed from the database. |
| Depends On  | FEATURE-LOAD-TRANSACTIONS.md, FEATURE-TRANSFER.md, FEATURE-TXN-DELETE.md, FEATURE-CSV-OUTPUT.md |
| Provides    | ledger report balances |

## Purpose

`ledger report balances` writes `account,name,transactions,balance` for every account ordered by code, followed by `TOTAL,,<count>,<sum>`. The balance of an account is the sum of its transaction amounts.

## Behavior

1. Read every account and every transaction from the database.
2. For each account, count its transactions and sum their amounts in integer cents.
3. Write one row per account ordered by code, then the TOTAL row over all transactions.
4. Write amounts with exactly two decimal places.

When no accounts exist, only the header and the TOTAL row are written, with count `0` and sum `0.00`.

## Programmatic Acceptance

=== AC report-balances-match-database ===
Intent: Each balances row and the TOTAL row equal values computed from the accounts and transactions read back from the database.

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
accounts = list(db.accounts.list())
transactions = list(db.transactions.list())

code, out, err = cli_runner("report", "balances")
assert code == 0, err
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["account", "name", "transactions", "balance"]
body, total = rows[1:-1], rows[-1]

codes = [row[0] for row in body]
assert codes == sorted(codes)
assert codes == sorted(account.account for account in accounts)
for row in body:
    account = next(item for item in accounts if item.account == row[0])
    mine = [txn for txn in transactions if txn.account == row[0]]
    assert row[1] == account.name
    assert int(row[2]) == len(mine)
    assert int(Decimal(row[3]).scaleb(2)) == sum(txn.amount for txn in mine)

assert total[0] == "TOTAL" and total[1] == ""
assert int(total[2]) == len(transactions)
assert int(Decimal(total[3]).scaleb(2)) == sum(txn.amount for txn in transactions)
=== END AC report-balances-match-database ===

=== AC report-balances-empty-ledger ===
Intent: With no accounts, the balances report writes only the header and a TOTAL row with zero count and zero sum.

import csv
import io
import os
import tempfile
from decimal import Decimal

from cli.testing import cli_runner

os.environ["DATABASE_URL"] = os.path.join(tempfile.mkdtemp(), "ledger.db")
code, out, err = cli_runner("init")
assert code == 0, err

code, out, err = cli_runner("report", "balances")
assert code == 0, err
rows = list(csv.reader(io.StringIO(out)))
assert len(rows) == 2
assert rows[0] == ["account", "name", "transactions", "balance"]
assert rows[1][0] == "TOTAL"
assert int(rows[1][2]) == 0
assert int(Decimal(rows[1][3]).scaleb(2)) == 0
=== END AC report-balances-empty-ledger ===

## User Acceptance

- None.

## Guardrails

- Every value in the report is computed from a database query; no account, count, or total is hardcoded.
- Amounts are integer cents internally and are formatted only at the output boundary.
