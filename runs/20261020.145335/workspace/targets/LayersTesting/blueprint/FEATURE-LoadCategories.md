# FEATURE: Load Categories

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provide `ledger load categories <csv>`, which loads every category row from a file or none. |
| Depends On  | FEATURE-CommandTransaction.md, FEATURE-ValidateText.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md, FEATURE-InitSchema.md, DATABASE.md |
| Provides    | ledger load categories |
| Consumes    | db.categories.create, db.categories.get, db.categories.list |

## Purpose

`ledger load categories <csv>` reads a categories file and inserts every row into the `categories`
table. The whole load runs in one command transaction: if any row is rejected, no row is stored.

## Trigger

`ledger load categories <path>`.

## Sequence

1. Open the file. If it cannot be read, exit `1`.
2. Check the header is exactly `category,description`. If it is not, exit `3`.
3. Validate each row's code and description with the validators of FEATURE-ValidateText.md. An
   invalid row, or a code repeated within the file or already present in the table, exits `3`.
4. Insert every row with `db.categories.create`, inside the command transaction.
5. Write `table,loaded` then `categories,<rows>` and exit `0`.

## Routes and Interfaces

- `ledger load categories <csv>`: exit `0` on success; `1` unreadable file; `2` wrong argument count;
  `3` rejected header or row, with nothing stored.

## Reads and Writes

- Writes: inserts the file's rows into `categories`, all or none.
- Reads: `categories` for duplicate detection.

## Programmatic Acceptance

=== AC load-categories-seed-file ===
Intent: Loading the staged seed categories file exits 0 and stores exactly its data rows.
import os
import tempfile
import pathlib

from cli.testing import cli_runner
from persistence import open_database

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
cli_runner("init")

seed = pathlib.Path("sources/seed_categories.csv")
expected_rows = len(seed.read_text().splitlines()) - 1

expected_exit = 0
code, out, err = cli_runner("load", "categories", str(seed))
print("stdout:", repr(out), "stderr:", repr(err))
assert code == expected_exit
lines = out.splitlines()
assert lines[0] == "table,loaded"
assert lines[1].split(",") == ["categories", str(expected_rows)]

db = open_database(os.environ["DATABASE_URL"])
assert len(db.categories.list()) == expected_rows
=== END AC load-categories-seed-file ===

=== AC load-categories-bad-header-stores-nothing ===
Intent: A file whose header is not `category,description` exits 3 and stores no rows.
import os
import tempfile
import pathlib

from cli.testing import cli_runner
from persistence import open_database

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
cli_runner("init")

path = pathlib.Path(work, "reordered.csv")
path.write_text("description,category\nSales receipts,SALES\n")

expected_exit = 3
code, out, err = cli_runner("load", "categories", str(path))
print("stdout:", repr(out), "stderr:", repr(err))
assert code == expected_exit
assert out == ""

db = open_database(os.environ["DATABASE_URL"])
assert len(db.categories.list()) == 0
=== END AC load-categories-bad-header-stores-nothing ===

=== AC load-categories-duplicate-code-all-or-none ===
Intent: A duplicate code inside one file exits 3 and stores none of its rows, including the valid first row.
import os
import tempfile
import pathlib

from cli.testing import cli_runner
from persistence import open_database

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
cli_runner("init")

path = pathlib.Path(work, "dup.csv")
path.write_text("category,description\nSALES,Sales receipts\nSALES,Other\n")

expected_exit = 3
code, out, err = cli_runner("load", "categories", str(path))
print("stdout:", repr(out), "stderr:", repr(err))
assert code == expected_exit
assert out == ""

db = open_database(os.environ["DATABASE_URL"])
assert len(db.categories.list()) == 0
=== END AC load-categories-duplicate-code-all-or-none ===

=== AC load-categories-invalid-description-all-or-none ===
Intent: A description longer than 40 characters exits 3 and stores none of the file's rows.
import os
import tempfile
import pathlib

from cli.testing import cli_runner
from persistence import open_database

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
cli_runner("init")

too_long = "X" * 41
path = pathlib.Path(work, "long.csv")
path.write_text("category,description\nSALES,Sales receipts\nRENT," + too_long + "\n")

expected_exit = 3
code, out, err = cli_runner("load", "categories", str(path))
print("stdout:", repr(out), "stderr:", repr(err))
assert code == expected_exit
assert out == ""

db = open_database(os.environ["DATABASE_URL"])
assert len(db.categories.list()) == 0
=== END AC load-categories-invalid-description-all-or-none ===

=== AC load-categories-unreadable-file ===
Intent: A path that does not exist exits 1 and writes nothing to stdout.
import os
import tempfile

from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
cli_runner("init")

expected_exit = 1
code, out, err = cli_runner("load", "categories", os.path.join(work, "missing.csv"))
print("stdout:", repr(out), "stderr:", repr(err))
assert code == expected_exit
assert out == ""
=== END AC load-categories-unreadable-file ===

## User Acceptance

- None.

## Guardrails

- Loading is all or none; a rejected file leaves `categories` exactly as it was.
- Row values are inserted as read; no total or derived field is written.
- The seed file is read from the staged `sources/` path and never embedded in application code.
