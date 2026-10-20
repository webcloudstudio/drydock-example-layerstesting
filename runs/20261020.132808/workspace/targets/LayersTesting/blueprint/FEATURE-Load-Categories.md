# FEATURE: Load Categories

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Load the categories CSV all or nothing through `ledger load categories <csv>`. |
| Depends On  | DATABASE.md, FEATURE-Code-Validation.md, FEATURE-Command-Transaction.md, FEATURE-CLI-Output.md, FEATURE-CLI-Dispatch.md |
| Provides    | ledger load categories <csv> |
| Consumes    | categories.get, categories.create, categories.list |

## Purpose

Loads the `categories` table from a CSV file whose header is `category,description`.

## Behavior

- The header must equal `category,description` in that order. Otherwise the command exits 3 and stores nothing.
- Each code is validated by the code rules. Each description is 1 to 40 characters with no comma or newline. A violation exits 3 and stores nothing.
- A code repeated within the file, or a code already present, exits 3 and stores nothing.
- A header-only file loads zero rows and exits 0.
- On success, stdout is `table,loaded` then `categories,<rows>`.
- The command runs in one command transaction. An unreadable file exits 1 with no change.

## Programmatic Acceptance

=== AC load-categories-seed-round-trip ===
Intent: Loading the seed categories file reports its row count, and every loaded category appears in the categories report with its description.

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


seed_path = "sources/seed_categories.csv"
with open(seed_path, newline="") as handle:
    seed_header, *seed_rows = list(csv.reader(handle))
assert seed_header == ["category", "description"]

assert run("init")[0] == 0
code, out, err = run("load", "categories", seed_path)
assert code == 0
loaded = list(csv.reader(io.StringIO(out)))
assert loaded[0] == ["table", "loaded"]
assert loaded[-1] == ["categories", str(len(seed_rows))]

code, out, err = run("report", "categories")
assert code == 0
report = {row[0]: row for row in list(csv.reader(io.StringIO(out)))[1:]}
for category, description in seed_rows:
    assert report[category][1] == description
=== END AC load-categories-seed-round-trip ===

=== AC load-categories-header-only ===
Intent: A header-only categories file loads zero rows, reports categories,0, and exits 0.

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


with open("sources/seed_categories.csv", newline="") as handle:
    seed_header = next(csv.reader(handle))

header_only = os.path.join(tempfile.mkdtemp(), "categories.csv")
with open(header_only, "w", newline="") as handle:
    csv.writer(handle, lineterminator="\n").writerow(seed_header)

assert run("init")[0] == 0
code, out, err = run("load", "categories", header_only)
assert code == 0
assert list(csv.reader(io.StringIO(out)))[-1] == ["categories", "0"]

code, out, err = run("count")
assert code == 0
counts = {row[0]: row[1] for row in list(csv.reader(io.StringIO(out)))[1:]}
assert counts["categories"] == "0"
=== END AC load-categories-header-only ===

=== AC load-categories-header-mismatch ===
Intent: A categories file whose header columns are out of order exits 3 and leaves the categories table empty.

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


with open("sources/seed_categories.csv", newline="") as handle:
    seed_header, *seed_rows = list(csv.reader(handle))

reordered = os.path.join(tempfile.mkdtemp(), "categories.csv")
with open(reordered, "w", newline="") as handle:
    writer = csv.writer(handle, lineterminator="\n")
    writer.writerow(list(reversed(seed_header)))
    writer.writerows(seed_rows)

assert run("init")[0] == 0
code, out, err = run("load", "categories", reordered)
assert code == 3
assert out == ""

code, out, err = run("count")
counts = {row[0]: row[1] for row in list(csv.reader(io.StringIO(out)))[1:]}
assert counts["categories"] == "0"
=== END AC load-categories-header-mismatch ===

=== AC load-categories-duplicate-key ===
Intent: A categories file that repeats a code exits 3 and stores none of its rows.

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


with open("sources/seed_categories.csv", newline="") as handle:
    seed_header, *seed_rows = list(csv.reader(handle))

duplicated = os.path.join(tempfile.mkdtemp(), "categories.csv")
with open(duplicated, "w", newline="") as handle:
    writer = csv.writer(handle, lineterminator="\n")
    writer.writerow(seed_header)
    writer.writerows(seed_rows)
    writer.writerow(seed_rows[0])

assert run("init")[0] == 0
code, out, err = run("load", "categories", duplicated)
assert code == 3
assert out == ""

code, out, err = run("count")
counts = {row[0]: row[1] for row in list(csv.reader(io.StringIO(out)))[1:]}
assert counts["categories"] == "0"
=== END AC load-categories-duplicate-key ===

=== AC load-categories-invalid-description-all-or-none ===
Intent: A categories file with one description longer than 40 characters exits 3 and stores none of the valid rows before it.

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


with open("sources/seed_categories.csv", newline="") as handle:
    seed_header, *seed_rows = list(csv.reader(handle))

invalid_rows = [list(row) for row in seed_rows]
invalid_rows[-1][1] = "D" * 41

invalid = os.path.join(tempfile.mkdtemp(), "categories.csv")
with open(invalid, "w", newline="") as handle:
    writer = csv.writer(handle, lineterminator="\n")
    writer.writerow(seed_header)
    writer.writerows(invalid_rows)

assert run("init")[0] == 0
code, out, err = run("load", "categories", invalid)
assert code == 3
assert out == ""

code, out, err = run("count")
counts = {row[0]: row[1] for row in list(csv.reader(io.StringIO(out)))[1:]}
assert counts["categories"] == "0"
=== END AC load-categories-invalid-description-all-or-none ===

## User Acceptance

- None.

## Guardrails

- Application code reaches the categories table only through the `persistence` package operations.
- A rejected categories load stores no rows, including rows that were individually valid.
- Diagnostics go to standard error only; standard output stays empty on failure.
