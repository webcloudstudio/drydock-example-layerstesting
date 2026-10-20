# FEATURE: Load Transactions

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Load the transactions CSV all or nothing under the balance rule through `ledger load transactions <csv>`. |
| Depends On  | DATABASE.md, FEATURE-Load-Accounts.md, FEATURE-Load-Categories.md, FEATURE-Balance-Rule.md, FEATURE-Amount-Format.md, FEATURE-Date-Validation.md, FEATURE-Command-Transaction.md, FEATURE-CLI-Output.md, FEATURE-CLI-Dispatch.md |
| Provides    | ledger load transactions <csv> |
| Consumes    | transactions.create, transactions.get, transactions.list, accounts.get, categories.get |

## Purpose

Loads the `transactions` table from a CSV file whose header is `txn_id,date,account,category,amount,memo`. Each file row keeps its own `txn_id`.

## Behavior

- The header must equal the transaction columns in that order. Otherwise the command exits 3 and stores nothing.
- Every row's account and category must already exist. An unknown account or category exits 3.
- Each row's amount, date, and memo are validated by their rules.
- The balance rule is checked for the whole file after its changes and before commit. Any negative balance exits 3.
- Any rejection stores none of the file's rows.
- On success, stdout is `table,loaded` then `transactions,<rows>`.

## Programmatic Acceptance

=== AC load-transactions-seed-round-trip ===
Intent: After accounts and categories load, the seed transactions file loads its full row count, and the first and last seed rows read back unchanged with their file txn_id values.

import csv
import io
import os
import sys
import tempfile

from cli.testing import cli_runner

os.environ["DATABASE_URL"] = os.path.join(tempfile.mkdtemp(), "ledger.db")


def run(*args):
    code, out, err = cli_runner(*args)
    print(out)
    print(err, file=sys.stderr)
    return code, out, err


with open("sources/seed_transactions.csv", newline="") as handle:
    txn_header, *txn_rows = list(csv.reader(handle))
assert txn_header == ["txn_id", "date", "account", "category", "amount", "memo"]

assert run("init")[0] == 0
assert run("load", "accounts", "sources/seed_accounts.csv")[0] == 0
assert run("load", "categories", "sources/seed_categories.csv")[0] == 0

code, out, err = run("load", "transactions", "sources/seed_transactions.csv")
assert code == 0
loaded = list(csv.reader(io.StringIO(out)))
assert loaded[-1] == ["transactions", str(len(txn_rows))]

for seed_row in (txn_rows[0], txn_rows[-1]):
    code, out, err = run("txn", "get", seed_row[0])
    assert code == 0
    assert list(csv.reader(io.StringIO(out)))[1] == seed_row

code, out, err = run("count")
counts = {row[0]: row[1] for row in list(csv.reader(io.StringIO(out)))[1:]}
assert counts["transactions"] == str(len(txn_rows))
=== END AC load-transactions-seed-round-trip ===

=== AC load-transactions-unknown-reference ===
Intent: A transactions file naming an unknown account, or an unknown category, exits 3 and stores none of its rows.

import csv
import io
import os
import sys
import tempfile

from cli.testing import cli_runner

os.environ["DATABASE_URL"] = os.path.join(tempfile.mkdtemp(), "ledger.db")


def run(*args):
    code, out, err = cli_runner(*args)
    print(out)
    print(err, file=sys.stderr)
    return code, out, err


with open("sources/seed_transactions.csv", newline="") as handle:
    txn_header, *txn_rows = list(csv.reader(handle))

unknown_category_rows = [list(row) for row in txn_rows]
unknown_category_rows[0][3] = "NOSUCHCAT"
unknown_category = os.path.join(tempfile.mkdtemp(), "transactions.csv")
with open(unknown_category, "w", newline="") as handle:
    writer = csv.writer(handle, lineterminator="\n")
    writer.writerow(txn_header)
    writer.writerows(unknown_category_rows)

assert run("init")[0] == 0
assert run("load", "accounts", "sources/seed_accounts.csv")[0] == 0
assert run("load", "categories", "sources/seed_categories.csv")[0] == 0

for path in ("sources/seed_transactions_bad.csv", unknown_category):
    code, out, err = run("load", "transactions", path)
    assert code == 3
    assert out == ""

code, out, err = run("count")
counts = {row[0]: row[1] for row in list(csv.reader(io.StringIO(out)))[1:]}
assert counts["transactions"] == "0"
=== END AC load-transactions-unknown-reference ===

=== AC load-transactions-balance-breach ===
Intent: A transactions file that would leave an account below zero exits 3 and stores none of its rows.

import csv
import io
import os
import sys
import tempfile

from cli.testing import cli_runner

os.environ["DATABASE_URL"] = os.path.join(tempfile.mkdtemp(), "ledger.db")


def run(*args):
    code, out, err = cli_runner(*args)
    print(out)
    print(err, file=sys.stderr)
    return code, out, err


with open("sources/seed_transactions.csv", newline="") as handle:
    txn_header, *txn_rows = list(csv.reader(handle))

breach = os.path.join(tempfile.mkdtemp(), "transactions.csv")
with open(breach, "w", newline="") as handle:
    writer = csv.writer(handle, lineterminator="\n")
    writer.writerow(txn_header)
    writer.writerow(["9001", "2026-04-01", "DRAWER1", "SALES", "-100000.00", "overdraw"])

assert run("init")[0] == 0
assert run("load", "accounts", "sources/seed_accounts.csv")[0] == 0
assert run("load", "categories", "sources/seed_categories.csv")[0] == 0

code, out, err = run("load", "transactions", breach)
assert code == 3
assert out == ""

code, out, err = run("count")
counts = {row[0]: row[1] for row in list(csv.reader(io.StringIO(out)))[1:]}
assert counts["transactions"] == "0"
=== END AC load-transactions-balance-breach ===

=== AC load-transactions-header-mismatch ===
Intent: A transactions file whose header columns are out of order exits 3 and leaves the transactions table empty.

import csv
import io
import os
import sys
import tempfile

from cli.testing import cli_runner

os.environ["DATABASE_URL"] = os.path.join(tempfile.mkdtemp(), "ledger.db")


def run(*args):
    code, out, err = cli_runner(*args)
    print(out)
    print(err, file=sys.stderr)
    return code, out, err


with open("sources/seed_transactions.csv", newline="") as handle:
    txn_header, *txn_rows = list(csv.reader(handle))

reordered = os.path.join(tempfile.mkdtemp(), "transactions.csv")
with open(reordered, "w", newline="") as handle:
    writer = csv.writer(handle, lineterminator="\n")
    writer.writerow(list(reversed(txn_header)))
    writer.writerows(txn_rows)

assert run("init")[0] == 0
assert run("load", "accounts", "sources/seed_accounts.csv")[0] == 0
assert run("load", "categories", "sources/seed_categories.csv")[0] == 0

code, out, err = run("load", "transactions", reordered)
assert code == 3
assert out == ""

code, out, err = run("count")
counts = {row[0]: row[1] for row in list(csv.reader(io.StringIO(out)))[1:]}
assert counts["transactions"] == "0"
=== END AC load-transactions-header-mismatch ===

## User Acceptance

- None.

## Guardrails

- Application code reaches the transactions table only through the `persistence` package operations.
- A rejected transactions load stores none of its rows, including rows that were individually valid.
- The balance rule is checked after all file rows are applied and before commit, never per row.
- Diagnostics go to standard error only; standard output stays empty on failure.
