# FEATURE: Account Get

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Print one account with its transaction count and balance through `ledger account get <code>`. |
| Depends On  | DATABASE.md, FEATURE-Code-Validation.md, FEATURE-Amount-Format.md, FEATURE-Command-Transaction.md, FEATURE-CLI-Output.md, FEATURE-CLI-Dispatch.md |
| Provides    | ledger account get <code> |
| Consumes    | accounts.get, transactions.list |

## Purpose

Reads one row from the `accounts` table and prints it with its derived transaction count and balance.

## Behavior

- On success, stdout is the account header row followed by `<code>,<name>,<transactions>,<balance>`.
- `transactions` counts the account's rows in the transactions table.
- `balance` is the sum of those rows' amounts, formatted with two decimals.
- An absent code exits 4 and prints nothing to standard output.
- The command is read-only: repeated calls return identical output.

## Programmatic Acceptance

=== AC account-get-matches-loaded-seed ===
Intent: After the seed accounts, categories, and transactions load, account get for each seed account returns its name and the seed transaction count, and matches the balances report row.

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


with open("sources/seed_accounts.csv", newline="") as handle:
    _, *account_rows = list(csv.reader(handle))
with open("sources/seed_transactions.csv", newline="") as handle:
    _, *txn_rows = list(csv.reader(handle))

assert run("init")[0] == 0
assert run("load", "accounts", "sources/seed_accounts.csv")[0] == 0
assert run("load", "categories", "sources/seed_categories.csv")[0] == 0
assert run("load", "transactions", "sources/seed_transactions.csv")[0] == 0

code, out, err = run("report", "balances")
assert code == 0
balances = {row[0]: row for row in list(csv.reader(io.StringIO(out)))[1:]}

for account, name in account_rows:
    expected_count = sum(1 for row in txn_rows if row[2] == account)
    code, out, err = run("account", "get", account)
    assert code == 0
    row = list(csv.reader(io.StringIO(out)))[1]
    assert row[0] == account
    assert row[1] == name
    assert row[2] == str(expected_count)
    assert row == balances[account]
=== END AC account-get-matches-loaded-seed ===

=== AC account-get-absent-code ===
Intent: Getting an account code that does not exist exits 4 and prints nothing to standard output.

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


assert run("init")[0] == 0
code, out, err = run("account", "get", "NOSUCH")
assert code == 4
assert out == ""
=== END AC account-get-absent-code ===

=== AC account-get-repeatable ===
Intent: Two consecutive account get calls on the same code return identical output and exit 0, showing the command changes nothing.

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


with open("sources/seed_accounts.csv", newline="") as handle:
    _, *account_rows = list(csv.reader(handle))
account = account_rows[0][0]

assert run("init")[0] == 0
assert run("load", "accounts", "sources/seed_accounts.csv")[0] == 0

first_code, first_out, first_err = run("account", "get", account)
second_code, second_out, second_err = run("account", "get", account)
assert first_code == 0
assert second_code == 0
assert first_out == second_out
=== END AC account-get-repeatable ===

## User Acceptance

- None.

## Guardrails

- Application code reaches the accounts and transactions tables only through the `persistence` package operations.
- The balance is computed from the database rows at read time and is never stored or cached.
- An absent code is reported only as exit 4; no row is created as a side effect.
