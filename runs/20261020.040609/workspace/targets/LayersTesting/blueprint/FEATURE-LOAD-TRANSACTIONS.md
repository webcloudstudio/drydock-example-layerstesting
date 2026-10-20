# FEATURE: Load Transactions

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Loads transactions from a CSV file, keeping each file txn_id and applying the balance rule before commit. |
| Depends On  | FEATURE-LOAD-ACCOUNTS.md, FEATURE-LOAD-CATEGORIES.md, FEATURE-NONNEGATIVE-BALANCE.md, FEATURE-VALIDATE-TEXT.md, FEATURE-VALIDATE-AMOUNT.md, FEATURE-VALIDATE-DATE.md, FEATURE-EXIT-CODES.md, FEATURE-TEST-RUNNER.md, DATABASE.md |
| Provides    | ledger load transactions <csv> |

## Purpose

`ledger load transactions <csv>` reads a file whose header is
`txn_id,date,account,category,amount,memo`, validates each row, and inserts every row with its
file `txn_id` in one transaction. The balance rule is applied after all rows are written and before
commit. Output is `table,loaded` then `transactions,<rows>`.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC load-transactions-keeps-file-ids ===
Intent: A valid transactions file loads every row under its file txn_id and writes table,loaded then transactions,<rows>.

import os
import tempfile
from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
accounts = os.path.join(work, "accounts.csv")
with open(accounts, "w") as handle:
    handle.write("account,name\nCASH1,Cash Box\n")
categories = os.path.join(work, "categories.csv")
with open(categories, "w") as handle:
    handle.write("category,description\nSALES,Sales receipts\n")
transactions = os.path.join(work, "transactions.csv")
with open(transactions, "w") as handle:
    handle.write(
        "txn_id,date,account,category,amount,memo\n"
        "7,2026-01-02,CASH1,SALES,10.00,sale a\n"
        "8,2026-01-03,CASH1,SALES,-4.00,refund\n"
    )
row_count = 2
file_id = 7
amount_text = "10.00"

assert cli_runner("init")[0] == 0
assert cli_runner("load", "accounts", accounts)[0] == 0
assert cli_runner("load", "categories", categories)[0] == 0
code, out, err = cli_runner("load", "transactions", transactions)
assert code == 0
lines = out.splitlines()
assert lines[0] == "table,loaded"
assert lines[1].split(",") == ["transactions", str(row_count)]
code, out, err = cli_runner("txn", "get", str(file_id))
assert code == 0
row = out.splitlines()[1].split(",")
assert row[0] == str(file_id)
assert row[4] == amount_text
assert cli_runner("txn", "get", "8")[0] == 0
=== END AC load-transactions-keeps-file-ids ===

=== AC load-transactions-overdraft-rejected ===
Intent: A file whose rows would leave an account below zero exits 3 and stores none of its rows.

import os
import tempfile
from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
accounts = os.path.join(work, "accounts.csv")
with open(accounts, "w") as handle:
    handle.write("account,name\nCASH1,Cash Box\n")
categories = os.path.join(work, "categories.csv")
with open(categories, "w") as handle:
    handle.write("category,description\nSALES,Sales receipts\n")
transactions = os.path.join(work, "transactions.csv")
with open(transactions, "w") as handle:
    handle.write("txn_id,date,account,category,amount,memo\n9,2026-01-04,CASH1,SALES,-50.00,too big\n")
empty = 0

assert cli_runner("init")[0] == 0
assert cli_runner("load", "accounts", accounts)[0] == 0
assert cli_runner("load", "categories", categories)[0] == 0
assert cli_runner("load", "transactions", transactions)[0] == 3
assert cli_runner("txn", "get", "9")[0] == 4
rows = int(cli_runner("count")[1].splitlines()[3].split(",")[1])
assert rows == empty
=== END AC load-transactions-overdraft-rejected ===

=== AC load-transactions-unknown-account-rejected ===
Intent: A file row naming an unknown account exits 3 and stores none of its rows.

import os
import tempfile
from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
accounts = os.path.join(work, "accounts.csv")
with open(accounts, "w") as handle:
    handle.write("account,name\nCASH1,Cash Box\n")
categories = os.path.join(work, "categories.csv")
with open(categories, "w") as handle:
    handle.write("category,description\nSALES,Sales receipts\n")
transactions = os.path.join(work, "transactions.csv")
with open(transactions, "w") as handle:
    handle.write(
        "txn_id,date,account,category,amount,memo\n"
        "11,2026-01-05,CASH1,SALES,5.00,ok row\n"
        "12,2026-01-05,NOSUCH,SALES,5.00,unknown account\n"
    )
empty = 0

assert cli_runner("init")[0] == 0
assert cli_runner("load", "accounts", accounts)[0] == 0
assert cli_runner("load", "categories", categories)[0] == 0
assert cli_runner("load", "transactions", transactions)[0] == 3
assert cli_runner("txn", "get", "11")[0] == 4
rows = int(cli_runner("count")[1].splitlines()[3].split(",")[1])
assert rows == empty
=== END AC load-transactions-unknown-account-rejected ===

## User Acceptance

- None.

## Guardrails

- Every row keeps its file `txn_id`; the loader never reassigns ids.
- The balance rule is evaluated after the file's rows are staged and before commit, never per row.
- Amounts are stored as integer cents and never pass through floating point.
