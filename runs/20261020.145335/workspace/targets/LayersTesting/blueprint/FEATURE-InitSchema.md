# FEATURE: Initialize Schema

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provide `ledger init`, which drops and recreates the three ledger tables empty. |
| Depends On  | FEATURE-DatabaseTarget.md, FEATURE-CommandTransaction.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md, DATABASE.md |
| Provides    | ledger init |
| Consumes    | open_database, db.accounts.list, db.categories.list, db.transactions.list |

## Purpose

`ledger init` resets the store. It drops `accounts`, `categories`, and `transactions` if they exist,
recreates all three from the declared schema, and leaves them empty. It writes nothing to standard
output and exits `0`. It runs inside the command transaction, so a failure leaves the prior tables
as they were.

A missing SQLite file is created empty by the first command that opens it. If a command then finds
no ledger tables, it exits `1` and writes nothing to standard output. The no-tables failure is
exercised by the commands that read the tables; this feature verifies `init` itself.

## Trigger

`ledger init` with no further arguments. Usage errors (extra arguments) exit `2` under
FEATURE-CliDispatch.md.

## Sequence

1. Resolve the database target through FEATURE-DatabaseTarget.md.
2. Open the store with `open_database`.
3. Drop each declared table if present.
4. Create each declared table empty, using the generated schema.
5. Commit. Write nothing.

## Routes and Interfaces

- `ledger init`: exit `0` on success, `1` when the database is unreachable.

## Reads and Writes

- Writes: drops and recreates `accounts`, `categories`, and `transactions`.
- Reads: none beyond the table existence check.

## Programmatic Acceptance

=== AC init-leaves-tables-empty ===
Intent: `ledger init` exits 0, writes nothing to stdout, and leaves all three tables empty.
import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")

expected_exit = 0
code, out, err = cli_runner("init")
print("stdout:", repr(out), "stderr:", repr(err))
assert code == expected_exit
assert out == ""

db = open_database(os.environ["DATABASE_URL"])
assert len(db.accounts.list()) == 0
assert len(db.categories.list()) == 0
assert len(db.transactions.list()) == 0
=== END AC init-leaves-tables-empty ===

=== AC init-drops-existing-rows ===
Intent: `ledger init` removes rows that existed before it ran.
import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
cli_runner("init")

db = open_database(os.environ["DATABASE_URL"])
db.accounts.create(account="CASH1", name="Till")
before = len(db.accounts.list())

expected_exit = 0
code, out, err = cli_runner("init")
print("stdout:", repr(out), "stderr:", repr(err))
assert code == expected_exit

db = open_database(os.environ["DATABASE_URL"])
assert before == 1
assert len(db.accounts.list()) == 0
=== END AC init-drops-existing-rows ===

=== AC init-creates-missing-file ===
Intent: The first command against a missing SQLite file creates it.
import os
import tempfile

from cli.testing import cli_runner

work = tempfile.mkdtemp()
path = os.path.join(work, "fresh.db")
os.environ["DATABASE_URL"] = path
assert not os.path.exists(path)

expected_exit = 0
code, out, err = cli_runner("init")
print("stdout:", repr(out), "stderr:", repr(err))
assert code == expected_exit
assert os.path.exists(path)
=== END AC init-creates-missing-file ===

=== AC init-rejects-extra-argument ===
Intent: Extra arguments to `init` are a usage error with exit 2.
import os
import tempfile

from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")

expected_exit = 2
code, out, err = cli_runner("init", "extra")
print("stdout:", repr(out), "stderr:", repr(err))
assert code == expected_exit
assert out == ""
=== END AC init-rejects-extra-argument ===

## User Acceptance

- None.

## Guardrails

- `init` never writes CSV or any other text to standard output.
- `init` never reads or stages a seed file.
- Table creation comes from the declared schema; no table or column is hand-written here.
