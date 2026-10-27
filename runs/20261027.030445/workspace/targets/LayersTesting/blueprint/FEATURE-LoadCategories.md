# FEATURE: Load Categories

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | The categories loader registered with the shared `ledger load` command. |
| Depends On | FEATURE-LoadAccounts.md, FEATURE-LedgerCli.md, DATABASE.md |
| Provides | ledger load categories |
| Consumes | ledger load, categories |

## Purpose

Register `categories` with the shared load dispatcher created by `FEATURE-LoadAccounts.md`, with the
same all-or-nothing contract.

## Behavior

- The header must be `category,description`; a mismatch exits 3.
- Codes follow the shared code rule (1 to 12 characters of `A-Z`, `0-9`); descriptions are 1 to 40
  characters with no comma or newline.
- Rows are validated, and duplicate keys detected within the file and against stored categories,
  before the first write. Any failure exits 3 with empty standard output and nothing stored.
- Success stores every row in one transaction and writes `table,loaded` then `categories,<rows>`.
  A header-only file writes `categories,0` and exits 0.

## Database Interface

- `FEATURE-CATEGORY-001` — write: store a category - supplies: `category`, `description` - returns: `category`, `description`
- `FEATURE-CATEGORY-002` — read: detect an existing category by code - supplies: `category` - returns: `category`, `description`

## Programmatic Acceptance

=== AC load-categories-success ===
Intent: A valid categories file exits 0, reports the loaded count, and every row is readable afterward.

import csv
import io
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

rows = [["ZQK01", "Cat One"], ["ZQK02", "Cat Two"]]
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "categories.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["category", "description"])
        w.writerows(rows)
    with db_session() as db:
        before = len(db.categories.list())
        code, out, err = cli_runner("load", "categories", path)
        print(out, err)
        assert code == 0
        parsed = list(csv.reader(io.StringIO(out)))
        assert parsed == [["table", "loaded"], ["categories", str(len(rows))]]
        assert len(db.categories.list()) == before + len(rows)
        for cat, desc in rows:
            stored = db.categories.get(category=cat)
            assert stored is not None
            assert stored.description == desc
=== END AC load-categories-success ===

=== AC load-categories-header-only ===
Intent: A header-only categories file loads zero rows, reports zero, and exits 0.

import csv
import io
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "categories.csv")
    with open(path, "w", newline="") as f:
        csv.writer(f, lineterminator="\n").writerow(["category", "description"])
    with db_session() as db:
        before = len(db.categories.list())
        code, out, err = cli_runner("load", "categories", path)
        print(out, err)
        assert code == 0
        parsed = list(csv.reader(io.StringIO(out)))
        assert parsed == [["table", "loaded"], ["categories", "0"]]
        assert len(db.categories.list()) == before
=== END AC load-categories-header-only ===

=== AC load-categories-duplicates ===
Intent: A code repeated inside the file, and a code already stored, each reject the whole file with exit 3 and store nothing new.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

stored_code = "ZQK11"
kept = "Original"
with tempfile.TemporaryDirectory() as tmp:
    dup_path = os.path.join(tmp, "dup.csv")
    with open(dup_path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["category", "description"])
        w.writerow(["ZQK12", "First"])
        w.writerow(["ZQK12", "Second"])
    stored_path = os.path.join(tmp, "stored.csv")
    with open(stored_path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["category", "description"])
        w.writerow(["ZQK13", "Fresh"])
        w.writerow([stored_code, "Replacement"])
    with db_session() as db:
        db.categories.create(category=stored_code, description=kept)
        before = len(db.categories.list())
        code, out, err = cli_runner("load", "categories", dup_path)
        assert code == 3
        assert out == ""
        code, out, err = cli_runner("load", "categories", stored_path)
        print(out, err)
        assert code == 3
        assert out == ""
        assert len(db.categories.list()) == before
        assert db.categories.get(category="ZQK12") is None
        assert db.categories.get(category="ZQK13") is None
        assert db.categories.get(category=stored_code).description == kept
=== END AC load-categories-duplicates ===

=== AC load-categories-invalid-rows ===
Intent: Invalid code or description rows after a valid row exit 3 and store neither row.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

good = ["ZQK21", "Good Row"]
bad_rows = [
    ["lower", "Lowercase code"],
    ["B" * 13, "Long code"],
    ["ZQK22", ""],
    ["ZQK23", "D" * 41],
    ["ZQK24", "has,comma"],
]
with tempfile.TemporaryDirectory() as tmp:
    with db_session() as db:
        before = len(db.categories.list())
        for i, bad in enumerate(bad_rows):
            path = os.path.join(tmp, "c%d.csv" % i)
            with open(path, "w", newline="") as f:
                w = csv.writer(f, lineterminator="\n")
                w.writerow(["category", "description"])
                w.writerow(good)
                w.writerow(bad)
            code, out, err = cli_runner("load", "categories", path)
            print(i, code, out, err)
            assert code == 3
            assert out == ""
            assert db.categories.get(category=good[0]) is None
            assert len(db.categories.list()) == before
=== END AC load-categories-invalid-rows ===

=== AC load-categories-header-mismatch ===
Intent: A categories file with the accounts header is rejected with exit 3 and nothing stored.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "wrong.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["account", "name"])
        w.writerow(["ZQK31", "Wrong Header"])
    with db_session() as db:
        before = len(db.categories.list())
        code, out, err = cli_runner("load", "categories", path)
        print(out, err)
        assert code == 3
        assert out == ""
        assert len(db.categories.list()) == before
=== END AC load-categories-header-mismatch ===

## User Acceptance

- None.

## Guardrails

- No category is stored when any row, header, or key check fails.
- Persistence is reached only through the `persistence` package.
