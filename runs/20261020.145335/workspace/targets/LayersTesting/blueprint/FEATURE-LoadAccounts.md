# FEATURE: Load Accounts

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provide `ledger load accounts <csv>`, which loads every account row from a file or none. |
| Depends On  | FEATURE-CommandTransaction.md, FEATURE-ValidateText.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md, FEATURE-InitSchema.md, DATABASE.md |
| Provides    | ledger load accounts |
| Consumes    | db.accounts.create, db.accounts.get, db.accounts.list |

## Purpose

`ledger load accounts <csv>` reads an accounts file and inserts every row into the `accounts` table.
The whole load runs in one command transaction: if any row is rejected, no row is stored.

## Trigger

`ledger load accounts <path>`.

## Sequence

1. Open the file. If it cannot be read, exit `1`.
2. Check the header is exactly `account,name`. If it is not, exit `3`.
3. Validate each row's code and name with the validators of FEATURE-ValidateText.md. An invalid row,
   or a code repeated within the file or already present in the table, exits `3`.
4. Insert every row with `db.accounts.create`, inside the command transaction.
5. Write `table,loaded` then `accounts,<rows>` and exit `0`.

## Routes and Interfaces

- `ledger load accounts <csv>`: exit `0` on success; `1` unreadable file; `2` wrong argument count;
  `3` rejected header or row, with nothing stored.

## Reads and Writes

- Writes: inserts the file's rows into `accounts`, all or none.
- Reads: `accounts` for duplicate detection.

## Programmatic Acceptance

=== AC load-accounts-seed-file ===
Intent: Loading the staged seed accounts file exits 0 and stores exactly its data rows.
import os
import tempfile
import pathlib

from cli.testing import cli_runner
from persistence import open_database

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
cli_runner("init")

seed = pathlib.Path("sources/seed_accounts.csv")
expected_rows = len(seed.read_text().splitlines()) - 1

expected_exit = 0
code, out, err = cli_runner("load", "accounts", str(seed))
print("stdout:", repr(out), "stderr:", repr(err))
assert code == expected_exit
lines = out.splitlines()
assert lines[0] == "table,loaded"
assert lines[1].split(",") == ["accounts", str(expected_rows)]

db = open_database(os.environ["DATABASE_URL"])
assert len(db.accounts.list()) == expected_rows
=== END AC load-accounts-seed-file ===

=== AC load-accounts-bad-header-stores-nothing ===
Intent: A file whose header is not `account,name` exits 3 and stores no rows.
import os
import tempfile
import pathlib

from cli.testing import cli_runner
from persistence import open_database

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
cli_runner("init")

path = pathlib.Path(work, "reordered.csv")
path.write_text("name,account\nTill,CASH1\n")

expected_exit = 3
code, out, err = cli_runner("load", "accounts", str(path))
print("stdout:", repr(out), "stderr:", repr(err))
assert code == expected_exit
assert out == ""

db = open_database(os.environ["DATABASE_URL"])
assert len(db.accounts.list()) == 0
=== END AC load-accounts-bad-header-stores-nothing ===

=== AC load-accounts-duplicate-code-all-or-none ===
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
path.write_text("account,name\nCASH1,Till\nCASH1,Safe\n")

expected_exit = 3
code, out, err = cli_runner("load", "accounts", str(path))
print("stdout:", repr(out), "stderr:", repr(err))
assert code == expected_exit
assert out == ""

db = open_database(os.environ["DATABASE_URL"])
assert len(db.accounts.list()) == 0
=== END AC load-accounts-duplicate-code-all-or-none ===

=== AC load-accounts-invalid-code-all-or-none ===
Intent: A lowercase code exits 3 and stores none of the file's rows.
import os
import tempfile
import pathlib

from cli.testing import cli_runner
from persistence import open_database

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
cli_runner("init")

path = pathlib.Path(work, "badcode.csv")
path.write_text("account,name\nCASH1,Till\ncash2,Safe\n")

expected_exit = 3
code, out, err = cli_runner("load", "accounts", str(path))
print("stdout:", repr(out), "stderr:", repr(err))
assert code == expected_exit
assert out == ""

db = open_database(os.environ["DATABASE_URL"])
assert len(db.accounts.list()) == 0
=== END AC load-accounts-invalid-code-all-or-none ===

=== AC load-accounts-unreadable-file ===
Intent: A path that does not exist exits 1 and writes nothing to stdout.
import os
import tempfile

from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
cli_runner("init")

expected_exit = 1
code, out, err = cli_runner("load", "accounts", os.path.join(work, "missing.csv"))
print("stdout:", repr(out), "stderr:", repr(err))
assert code == expected_exit
assert out == ""
=== END AC load-accounts-unreadable-file ===

## User Acceptance

- None.

## Guardrails

- Loading is all or none; a rejected file leaves `accounts` exactly as it was.
- Row values are inserted as read; no balance or derived field is written.
- The seed file is read from the staged `sources/` path and never embedded in application code.
