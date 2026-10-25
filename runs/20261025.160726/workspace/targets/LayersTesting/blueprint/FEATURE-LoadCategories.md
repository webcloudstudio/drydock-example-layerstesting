# FEATURE: Load Categories

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger load categories <csv>`, which loads categories from a CSV file all-or-nothing. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-CliEntry.md, FEATURE-LedgerCore.md, FEATURE-Init.md, FEATURE-Count.md |
| Provides | ledger load categories |
| Consumes | cli.main, validate_code, validate_text |

## Purpose

Bulk-load category rows so transactions can be classified. The command either stores every row or
stores nothing.

## Command Contract

`ledger load categories <csv>` registers under the `load` command in the cli command table.

| Condition | Result |
|---|---|
| File readable, header equals `category,description`, every row valid | Exit 0. Stdout is `table,loaded` then `categories,<rows>`. |
| Missing `<csv>` argument or extra arguments | Exit 2, nothing on stdout. |
| File missing or unreadable | Exit 1, nothing on stdout. |
| Header differs from the table columns in name or order | Exit 3, nothing stored. |
| A row has an invalid code or description | Exit 3, nothing stored. |
| A code repeats within the file or already exists in the table | Exit 3, nothing stored. |

## Behavior

1. Read the whole file with the standard `csv` module and check the header.
2. Validate every row (code 1 to 12 characters of `A-Z0-9`; description 1 to 40 characters with no
   comma or newline) and both duplicate rules before the first write.
3. Write all rows in one transaction, then print the result.
4. A failing command writes one diagnostic line to standard error and nothing to standard output.

## Database Interface

- `FEATURE-CATEGORY-003` — write: create a category - supplies: `category`, `description` - returns: `category`, `description`
- `FEATURE-CATEGORY-002` — read: detect codes already stored - supplies: `category` - returns: `category`, `description`

## Programmatic Acceptance

=== AC load-categories-valid ===
Intent: A valid categories file loads, reports the loaded count, and every row reads back.

import csv
import io
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

def counts():
    rc, out, err = cli_runner("count")
    assert rc == 0
    return {r[0]: int(r[1]) for r in list(csv.reader(io.StringIO(out)))[1:]}

codes = ["LDCAT1", "LDCAT2", "LDCAT3", "LDCAT4"]
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "categories.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["category", "description"])
        w.writerows([[c, "Desc " + c] for c in codes])
    before = counts()
    rc, out, err = cli_runner("load", "categories", path)
print(out)
print(err)
assert rc == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows == [["table", "loaded"], ["categories", str(len(codes))]]
assert counts()["categories"] == before["categories"] + len(codes)
with db_session() as db:
    for c in codes:
        got = db.categories.get(category=c)
        assert got is not None
        assert got.description == "Desc " + c
=== END AC load-categories-valid ===

=== AC load-categories-header ===
Intent: A file whose header does not match the table columns is rejected with exit 3 and stores nothing.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

code = "LDCHD1"
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "categories.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["description", "category"])
        w.writerow(["Swapped Header", code])
    rc, out, err = cli_runner("load", "categories", path)
print(out)
print(err)
assert rc == 3
assert out == ""
with db_session() as db:
    assert db.categories.get(category=code) is None
=== END AC load-categories-header ===

=== AC load-categories-atomic ===
Intent: An invalid row rejects the whole file so no earlier row is stored.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

good = "LDCAT9"
too_long = "X" * 13
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "categories.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["category", "description"])
        w.writerow([good, "Good Row"])
        w.writerow([too_long, "Code too long"])
    rc, out, err = cli_runner("load", "categories", path)
print(out)
print(err)
assert rc == 3
assert out == ""
with db_session() as db:
    assert db.categories.get(category=good) is None
=== END AC load-categories-atomic ===

=== AC load-categories-duplicates ===
Intent: A code repeated inside the file, or already stored, is rejected with exit 3 and nothing is added.

import csv
import io
import os
import tempfile
from cli.testing import cli_runner

def counts():
    rc, out, err = cli_runner("count")
    assert rc == 0
    return {r[0]: int(r[1]) for r in list(csv.reader(io.StringIO(out)))[1:]}

def write(path, rows):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["category", "description"])
        w.writerows(rows)

with tempfile.TemporaryDirectory() as tmp:
    dup_file = os.path.join(tmp, "dup.csv")
    write(dup_file, [["LDCDP1", "One"], ["LDCDP1", "Two"]])
    before = counts()
    rc, out, err = cli_runner("load", "categories", dup_file)
    print(out, err)
    assert rc == 3
    assert out == ""
    assert counts() == before

    once = os.path.join(tmp, "once.csv")
    write(once, [["LDCDP2", "Only"]])
    rc, out, err = cli_runner("load", "categories", once)
    assert rc == 0
    after_first = counts()
    rc, out, err = cli_runner("load", "categories", once)
    print(out, err)
    assert rc == 3
    assert out == ""
    assert counts() == after_first
=== END AC load-categories-duplicates ===

=== AC load-categories-usage-and-io ===
Intent: A missing argument is a usage error (exit 2) and an unreadable file is an operational failure (exit 1).

import os
import tempfile
from cli.testing import cli_runner

rc, out, err = cli_runner("load", "categories")
print(out, err)
assert rc == 2
assert out == ""

with tempfile.TemporaryDirectory() as tmp:
    missing = os.path.join(tmp, "absent.csv")
    rc, out, err = cli_runner("load", "categories", missing)
print(out, err)
assert rc == 1
assert out == ""
=== END AC load-categories-usage-and-io ===

## User Acceptance

- None.

## Guardrails

- No category is stored unless every row of the file is valid.
- Application code never reads `sources/` seed files; the file path comes only from the command line.
- All database access goes through the shipped persistence library.
