# FEATURE: Load Accounts

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Load the accounts CSV all or nothing through `ledger load accounts <csv>`. |
| Depends On  | DATABASE.md, FEATURE-Code-Validation.md, FEATURE-Command-Transaction.md, FEATURE-CLI-Output.md, FEATURE-CLI-Dispatch.md |
| Provides    | ledger load accounts <csv> |
| Consumes    | accounts.get, accounts.create |

## Purpose

Loads the `accounts` table from a CSV file whose header is `account,name`.

## Behavior

- The header must equal `account,name` in that order. Otherwise the command exits 3 and stores nothing.
- Each code is validated by the code rules. Each name is 1 to 40 characters with no comma or newline. A violation exits 3 and stores nothing.
- A code repeated within the file, or a code already present, exits 3 and stores nothing.
- A header-only file loads zero rows and exits 0.
- On success, stdout is `table,loaded` then `accounts,<rows>`.
- The command runs in one command transaction. An unreadable file exits 1 with no change.

## Programmatic Acceptance

=== AC load-accounts-seed-round-trip ===
Intent: Loading the seed accounts file reports its row count, and each loaded account reads back with its code and name.

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


seed_path = "sources/seed_accounts.csv"
with open(seed_path, newline="") as handle:
    seed_header, *seed_rows = list(csv.reader(handle))
assert seed_header == ["account", "name"]

assert run("init")[0] == 0
code, out, err = run("load", "accounts", seed_path)
assert code == 0
loaded = list(csv.reader(io.StringIO(out)))
assert loaded[0] == ["table", "loaded"]
assert loaded[-1] == ["accounts", str(len(seed_rows))]

for account, name in seed_rows:
    code, out, err = run("account", "get", account)
    assert code == 0
    row = list(csv.reader(io.StringIO(out)))[1]
    assert row[0] == account
    assert row[1] == name
=== END AC load-accounts-seed-round-trip ===

=== AC load-accounts-header-only ===
Intent: A header-only accounts file loads zero rows, reports accounts,0, and exits 0.

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
    seed_header = next(csv.reader(handle))

header_only = os.path.join(tempfile.mkdtemp(), "accounts.csv")
with open(header_only, "w", newline="") as handle:
    csv.writer(handle, lineterminator="\n").writerow(seed_header)

assert run("init")[0] == 0
code, out, err = run("load", "accounts", header_only)
assert code == 0
assert list(csv.reader(io.StringIO(out)))[-1] == ["accounts", "0"]

code, out, err = run("count")
assert code == 0
counts = {row[0]: row[1] for row in list(csv.reader(io.StringIO(out)))[1:]}
assert counts["accounts"] == "0"
=== END AC load-accounts-header-only ===

=== AC load-accounts-header-mismatch ===
Intent: An accounts file whose header columns are out of order exits 3 and leaves the accounts table empty.

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
    seed_header, *seed_rows = list(csv.reader(handle))

reordered = os.path.join(tempfile.mkdtemp(), "accounts.csv")
with open(reordered, "w", newline="") as handle:
    writer = csv.writer(handle, lineterminator="\n")
    writer.writerow(list(reversed(seed_header)))
    writer.writerows(seed_rows)

assert run("init")[0] == 0
code, out, err = run("load", "accounts", reordered)
assert code == 3
assert out == ""

code, out, err = run("count")
counts = {row[0]: row[1] for row in list(csv.reader(io.StringIO(out)))[1:]}
assert counts["accounts"] == "0"
=== END AC load-accounts-header-mismatch ===

=== AC load-accounts-duplicate-key ===
Intent: An accounts file that repeats a code exits 3 and stores none of its rows.

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
    seed_header, *seed_rows = list(csv.reader(handle))

duplicated = os.path.join(tempfile.mkdtemp(), "accounts.csv")
with open(duplicated, "w", newline="") as handle:
    writer = csv.writer(handle, lineterminator="\n")
    writer.writerow(seed_header)
    writer.writerows(seed_rows)
    writer.writerow(seed_rows[0])

assert run("init")[0] == 0
code, out, err = run("load", "accounts", duplicated)
assert code == 3
assert out == ""

code, out, err = run("count")
counts = {row[0]: row[1] for row in list(csv.reader(io.StringIO(out)))[1:]}
assert counts["accounts"] == "0"
=== END AC load-accounts-duplicate-key ===

=== AC load-accounts-invalid-row-all-or-none ===
Intent: An accounts file with one name longer than 40 characters exits 3 and stores none of the valid rows before it.

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
    seed_header, *seed_rows = list(csv.reader(handle))

invalid_rows = [list(row) for row in seed_rows]
invalid_rows[-1][1] = "N" * 41

invalid = os.path.join(tempfile.mkdtemp(), "accounts.csv")
with open(invalid, "w", newline="") as handle:
    writer = csv.writer(handle, lineterminator="\n")
    writer.writerow(seed_header)
    writer.writerows(invalid_rows)

assert run("init")[0] == 0
code, out, err = run("load", "accounts", invalid)
assert code == 3
assert out == ""

code, out, err = run("count")
counts = {row[0]: row[1] for row in list(csv.reader(io.StringIO(out)))[1:]}
assert counts["accounts"] == "0"
=== END AC load-accounts-invalid-row-all-or-none ===

## User Acceptance

- None.

## Guardrails

- Application code reaches the accounts table only through the `persistence` package operations.
- A rejected accounts load stores no rows, including rows that were individually valid.
- Diagnostics go to standard error only; standard output stays empty on failure.
