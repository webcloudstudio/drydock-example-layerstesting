# FEATURE: Load Categories

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger load categories <csv>` as an all-or-nothing bulk load. |
| Depends On | FEATURE-LoadCsvReader.md, FEATURE-Validation.md, DATABASE.md |
| Provides | ledger load categories |
| Consumes | ledger_core.csvio, ledger_core.validation, cli.registry |

## Purpose

Load categories from a CSV file whose header is `category,description`, applying the same
validate-everything-then-write rule as the accounts load.

## Behavior

1. `ledger load categories <csv>` takes exactly one file argument; other counts exit 2.
2. Read the file with `ledger_core.csvio.read_rows(path, ("category", "description"))`. An
   unreadable file exits 1; a wrong header or wrong field count exits 3.
3. Validate every row before any write: the code is 1 to 12 characters of `A-Z0-9`, the description
   is 1 to 40 characters with no comma or newline, the code does not repeat within the file, and the
   code is not already stored.
4. Insert every row in one atomic unit; a rejection stores none of them.
5. Print `table,loaded` then `categories,<rows>`.
6. Any rejection exits 3 with nothing on standard output and one diagnostic line on standard error.

## Database Interface

- `FEATURE-CATEGORY-005` — read: list stored categories to detect duplicate keys - supplies: — - returns: `category`, `description`
- `FEATURE-CATEGORY-001` — write: create a category - supplies: `category`, `description` - returns: `category`, `description`

## Programmatic Acceptance

=== AC load-categories-success ===
Intent: a valid categories file loads every row, prints the declared two CSV rows with the loaded count, and the rows are readable afterward.
Requires: executable=python3; scope=test

import csv
import io
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

rows = [["ZZKA1", "Cat One"], ["ZZKA2", "Cat Two"], ["ZZKA3", "Cat Three"]]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "categories.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["category", "description"])
        w.writerows(rows)
    with db_session() as db:
        code, out, err = cli_runner("load", "categories", path)
        print(out, err)
        assert code == 0
        parsed = list(csv.reader(io.StringIO(out)))
        assert parsed == [["table", "loaded"], ["categories", str(len(rows))]]
        for cat, text in rows:
            row = db.categories.get(category=cat)
            assert row is not None
            got = row["description"] if isinstance(row, dict) else row.description
            assert got == text
=== END AC load-categories-success ===

=== AC load-categories-rejected-row-stores-nothing ===
Intent: when a later row is invalid, exit 3 is returned, stdout is empty, and none of the earlier valid rows is stored.
Requires: executable=python3; scope=test

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

good = [["ZZKB%d" % i, "Good %d" % i] for i in range(1, 6)]
bad = ["ZZKBBAD", "x" * 41]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "categories.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["category", "description"])
        w.writerows(good)
        w.writerow(bad)
    with db_session() as db:
        before = len(db.categories.list())
        code, out, err = cli_runner("load", "categories", path)
        assert code == 3
        assert out == ""
        assert len(db.categories.list()) == before
        for cat, _ in good:
            assert db.categories.get(category=cat) is None
=== END AC load-categories-rejected-row-stores-nothing ===

=== AC load-categories-invalid-fields ===
Intent: each invalid code or description (bad characters, empty, over length, comma) rejects the whole file with exit 3 and stores no row.
Requires: executable=python3; scope=test

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

first = ["ZZKCOK", "Valid First"]
bad_rows = [
    ["zzkc1", "Lowercase"],
    ["ABCDEFGHIJKLM", "Too Long Code"],
    ["", "Empty Code"],
    ["ZZKC2", ""],
    ["ZZKC3", "has,comma"],
]
with tempfile.TemporaryDirectory() as d:
    with db_session() as db:
        for i, bad in enumerate(bad_rows):
            path = os.path.join(d, "c%d.csv" % i)
            with open(path, "w", newline="") as fh:
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(["category", "description"])
                w.writerow(first)
                w.writerow(bad)
            code, out, err = cli_runner("load", "categories", path)
            assert code == 3, bad
            assert out == ""
            assert db.categories.get(category=first[0]) is None
=== END AC load-categories-invalid-fields ===

=== AC load-categories-duplicates-rejected ===
Intent: a code repeated inside the file, and a code already stored, each reject the whole file with exit 3 and leave the stored row unchanged.
Requires: executable=python3; scope=test

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

def write(path, rows):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["category", "description"])
        w.writerows(rows)

with tempfile.TemporaryDirectory() as d:
    with db_session() as db:
        p1 = os.path.join(d, "dup_in_file.csv")
        write(p1, [["ZZKD1", "One"], ["ZZKD1", "One Again"]])
        code, out, err = cli_runner("load", "categories", p1)
        assert code == 3
        assert out == ""
        assert db.categories.get(category="ZZKD1") is None

        stored = "ZZKD2"
        stored_text = "Already Stored"
        db.categories.create(category=stored, description=stored_text)
        p2 = os.path.join(d, "dup_stored.csv")
        write(p2, [["ZZKD3", "Fresh"], [stored, "Replacement"]])
        code, out, err = cli_runner("load", "categories", p2)
        assert code == 3
        assert out == ""
        assert db.categories.get(category="ZZKD3") is None
        row = db.categories.get(category=stored)
        got = row["description"] if isinstance(row, dict) else row.description
        assert got == stored_text
=== END AC load-categories-duplicates-rejected ===

=== AC load-categories-header-and-usage ===
Intent: a wrong header exits 3 with nothing stored, and a missing file argument is a usage error with exit 2.
Requires: executable=python3; scope=test

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "wrong_header.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["category", "name"])
        w.writerow(["ZZKE1", "Wrong Header"])
    with db_session() as db:
        code, out, err = cli_runner("load", "categories", path)
        assert code == 3
        assert out == ""
        assert db.categories.get(category="ZZKE1") is None
        code, out, err = cli_runner("load", "categories")
        assert code == 2
        assert out == ""
=== END AC load-categories-header-and-usage ===

## User Acceptance

- None.

## Guardrails

- No row is written until every row in the file has been validated.
- Seed files are never read by application code; the file path comes only from the command line.
- A failing command writes nothing to standard output.
