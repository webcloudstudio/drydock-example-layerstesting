# FEATURE: Load Categories

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | Implements `ledger load categories <csv>` with all-or-nothing validation of the whole file. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-CliFoundation.md |
| Provides    | ledger load categories |
| Consumes    | categories.create, categories.get |

## Purpose

Bulk-load categories from a CSV file whose header is exactly `category,description`. The command
checks every row and every rule before its first write, so one invalid row stores nothing.

## Trigger

`./ledger load categories <csv>`

## Sequence

1. Reject a wrong argument count with exit 2.
2. Read the file. An unreadable file exits 1.
3. Require the header `category,description`; any other header exits 3.
4. Validate every data row: the code is 1 to 12 characters from `A-Z` and `0-9`; the description is
   1 to 40 characters with no comma or newline; a row with the wrong number of fields is invalid.
5. Reject (exit 3) a code that repeats within the file or already exists in `categories`.
6. After every row passed, write all rows through `categories.create`.
7. Print `table,loaded` and `categories,<rows>`.

A failing command writes nothing to standard output and one diagnostic line to standard error.

## Reads

- `categories.get` for each code in the file, to detect duplicates with stored rows.

## Writes

- `categories.create` once per validated row, after all validation has passed.

## Database Interface

- `FEATURE-CATEGORIES-001` — write: create a category - supplies: `category`, `description` - returns: `category`, `description`
- `FEATURE-CATEGORIES-002` — read: find a stored category by code - supplies: `category` - returns: `category`, `description`

## Programmatic Acceptance

=== AC load-categories-valid ===
Intent: A valid categories file loads, reports the loaded count, and every row reads back from the store.

import csv
import io
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

rows = [["UTKA1", "Cat One"], ["UTKA2", "Cat Two"]]
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "categories.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["category", "description"])
        w.writerows(rows)
    with db_session() as db:
        code, out, err = cli_runner("load", "categories", path)
        print(out)
        print(err)
        assert code == 0
        parsed = list(csv.reader(io.StringIO(out)))
        assert parsed == [["table", "loaded"], ["categories", str(len(rows))]]
        for category, description in rows:
            stored = db.categories.get(category=category)
            assert stored is not None
            assert stored.description == description
=== END AC load-categories-valid ===

=== AC load-categories-atomic-invalid-row ===
Intent: A file with an invalid last row exits 3, prints nothing to stdout, and stores none of the preceding valid rows.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

good = [["UTKB1", "Good One"], ["UTKB2", "Good Two"]]
bad = ["UTK-B3", "Hyphen Code"]
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "categories.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["category", "description"])
        w.writerows(good)
        w.writerow(bad)
    with db_session() as db:
        code, out, err = cli_runner("load", "categories", path)
        print(err)
        assert code == 3
        assert out == ""
        for category, _ in good:
            assert db.categories.get(category=category) is None
=== END AC load-categories-atomic-invalid-row ===

=== AC load-categories-field-rules ===
Intent: Over-long codes, empty descriptions, and over-long descriptions each reject the whole file with exit 3.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

anchor = ["UTKC0", "Anchor"]
variants = [
    ["K" * 13, "Long Code"],
    ["UTKC1", ""],
    ["UTKC2", "D" * 41],
]
with tempfile.TemporaryDirectory() as tmp:
    with db_session() as db:
        for index, variant in enumerate(variants):
            path = os.path.join(tmp, f"categories{index}.csv")
            with open(path, "w", newline="") as fh:
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(["category", "description"])
                w.writerow(anchor)
                w.writerow(variant)
            code, out, err = cli_runner("load", "categories", path)
            print(err)
            assert code == 3
            assert out == ""
            assert db.categories.get(category=anchor[0]) is None
=== END AC load-categories-field-rules ===

=== AC load-categories-duplicates ===
Intent: A code repeated inside the file, or already stored, rejects the whole file with exit 3 and stores nothing new.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

stored_code = "UTKD1"
fresh = "UTKD2"
repeated = "UTKD3"
with tempfile.TemporaryDirectory() as tmp:
    with db_session() as db:
        db.categories.create(category=stored_code, description="Already Here")

        against_store = os.path.join(tmp, "store.csv")
        with open(against_store, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["category", "description"])
            w.writerow([fresh, "Fresh"])
            w.writerow([stored_code, "Clash"])
        code, out, err = cli_runner("load", "categories", against_store)
        print(err)
        assert code == 3
        assert out == ""
        assert db.categories.get(category=fresh) is None

        within = os.path.join(tmp, "within.csv")
        with open(within, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["category", "description"])
            w.writerow([repeated, "First"])
            w.writerow([repeated, "Second"])
        code, out, err = cli_runner("load", "categories", within)
        print(err)
        assert code == 3
        assert out == ""
        assert db.categories.get(category=repeated) is None
=== END AC load-categories-duplicates ===

=== AC load-categories-header-and-usage ===
Intent: A mismatched header exits 3, a missing file exits 1, and a missing file argument exits 2.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with tempfile.TemporaryDirectory() as tmp:
    wrong = os.path.join(tmp, "wrong.csv")
    with open(wrong, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["account", "name"])
        w.writerow(["UTKE1", "Wrong Header"])
    missing = os.path.join(tmp, "absent.csv")
    with db_session() as db:
        code, out, err = cli_runner("load", "categories", wrong)
        assert code == 3 and out == ""
        assert db.categories.get(category="UTKE1") is None
        code, out, err = cli_runner("load", "categories", missing)
        assert code == 1 and out == ""
        code, out, err = cli_runner("load", "categories")
        assert code == 2 and out == ""
=== END AC load-categories-header-and-usage ===

## User Acceptance

- None.

## Guardrails

- Validate every row and rule before the first write; a rejected load changes nothing.
- Do not read `sources/` seed files from application code.
- Open no database driver outside the shipped persistence library.
- Diagnostics go to standard error only and are never compared.
