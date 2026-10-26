# FEATURE: Load Categories

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Implements `ledger load categories <csv>`, storing every category row of a file or none. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-LedgerInit.md, FEATURE-Validation.md, FEATURE-CsvOutput.md, FEATURE-ErrorContract.md |
| Provides | ledger load categories |
| Consumes | ledger.register_command, persistence.open_database, validation.check_code, validation.check_text, csv_output.write_rows, ledger_errors.Rejected, ledger_errors.OperationalFailure |

## Purpose

`ledger load categories <csv>` loads category records from a CSV file whose header is exactly `category,description`. The whole file is parsed and every row, every duplicate key and every rule is checked before the first write, so a rejected file stores nothing.

## Behavior

- Header: must equal `category,description` in names and order; otherwise exit 3 before any row is stored.
- Each row: `category` is a code (1 to 12 characters of `A-Z0-9`); `description` is 1 to 40 characters with no comma or newline. A bad row rejects the file with exit 3.
- Duplicate `category` values inside the file, or equal to a stored category, reject the file with exit 3.
- An unreadable or missing file exits 1.
- Success writes CSV `table,loaded` then `categories,<rows>` where `<rows>` is the number of rows loaded. Exit 0.
- All inserts happen in one database transaction.

## Database Interface

- `FEATURE-CATEGORY-001` — write: create a category - supplies: `category`, `description` - returns: `category`, `description`
- `FEATURE-CATEGORY-002` — read: get a category to detect a stored duplicate - supplies: `category` - returns: `category`, `description`

## Programmatic Acceptance

=== AC load-categories-success ===
Intent: A valid categories file stores every row, reports the loaded count, and the rows read back.

import csv
import io
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

rows = [["ZLC1A", "First loaded"], ["ZLC1B", "Second loaded"], ["ZLC1C", "Third loaded"]]
with db_session() as db:
    before = len(db.categories.list())
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "cats.csv")
        with open(path, "w", newline="") as f:
            csv.writer(f, lineterminator="\n").writerows([["category", "description"]] + rows)
        code, out, err = cli_runner("load", "categories", path)
    print(out, err)
    assert code == 0
    parsed = list(csv.reader(io.StringIO(out)))
    assert parsed == [["table", "loaded"], ["categories", str(len(rows))]]
    for c, desc in rows:
        got = db.categories.get(category=c)
        assert got is not None and got.description == desc
    assert len(db.categories.list()) == before + len(rows)
=== END AC load-categories-success ===

=== AC load-categories-header-mismatch ===
Intent: A file whose header differs in name or order is rejected with exit 3 and stores nothing.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

code_value = "ZLC2A"
with db_session() as db:
    before = len(db.categories.list())
    for header in (["description", "category"], ["category", "name"], ["category"]):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "cats.csv")
            with open(path, "w", newline="") as f:
                w = csv.writer(f, lineterminator="\n")
                w.writerow(header)
                w.writerow([code_value, "Header test"][: len(header)])
            code, out, err = cli_runner("load", "categories", path)
        print(code, out, err)
        assert code == 3
        assert out == ""
    assert db.categories.get(category=code_value) is None
    assert len(db.categories.list()) == before
=== END AC load-categories-header-mismatch ===

=== AC load-categories-bad-row-atomic ===
Intent: A file with an invalid row anywhere is rejected with exit 3 and none of its valid rows are stored.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

good = [["ZLC3A", "Good one"], ["ZLC3B", "Good two"]]
bad_rows = [
    ["zlc3c", "Lowercase code"],
    ["ZLC3D" + "X" * 8, "Code too long"],
    ["ZLC3E", ""],
    ["ZLC3F", "D" * 41],
]
with db_session() as db:
    before = len(db.categories.list())
    for bad in bad_rows:
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "cats.csv")
            with open(path, "w", newline="") as f:
                csv.writer(f, lineterminator="\n").writerows(
                    [["category", "description"]] + good + [bad]
                )
            code, out, err = cli_runner("load", "categories", path)
        print(code, out, err)
        assert code == 3
        assert out == ""
        for c, _ in good:
            assert db.categories.get(category=c) is None
    assert len(db.categories.list()) == before
=== END AC load-categories-bad-row-atomic ===

=== AC load-categories-duplicates ===
Intent: A duplicate key inside the file or against a stored category rejects the file with exit 3 and stores nothing.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

stored = "ZLC4S"
fresh = "ZLC4N"
stored_desc = "Already stored"
with db_session() as db:
    db.categories.create(category=stored, description=stored_desc)
    before = len(db.categories.list())
    cases = [
        [[fresh, "One"], [fresh, "Two"]],
        [[fresh, "One"], [stored, "Replacement"]],
    ]
    for rows in cases:
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "cats.csv")
            with open(path, "w", newline="") as f:
                csv.writer(f, lineterminator="\n").writerows(
                    [["category", "description"]] + rows
                )
            code, out, err = cli_runner("load", "categories", path)
        print(code, out, err)
        assert code == 3
        assert out == ""
        assert db.categories.get(category=fresh) is None
        assert db.categories.get(category=stored).description == stored_desc
    assert len(db.categories.list()) == before
=== END AC load-categories-duplicates ===

=== AC load-categories-unreadable-file ===
Intent: A missing file exits 1 with nothing on standard output and no change.

import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    before = len(db.categories.list())
    with tempfile.TemporaryDirectory() as d:
        missing = os.path.join(d, "absent.csv")
        code, out, err = cli_runner("load", "categories", missing)
    print(code, out, err)
    assert code == 1
    assert out == ""
    assert len(db.categories.list()) == before
=== END AC load-categories-unreadable-file ===

## User Acceptance

- None.

## Guardrails

- No row is stored when any row, header or duplicate check fails.
- Application code does not open a database driver and does not read `sources/` files.
- Diagnostics go to standard error only and never include a DSN or credential.
