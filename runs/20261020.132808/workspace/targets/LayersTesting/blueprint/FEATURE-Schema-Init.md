# FEATURE: Schema Init

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Implements `ledger init`, which drops and recreates the three ledger tables empty. |
| Depends On  | FEATURE-Command-Transaction.md, FEATURE-CLI-Dispatch.md, DATABASE.md |
| Provides    | ledger init |
| Consumes    | open_database, run_command |

## Purpose

`ledger init` resets the store to three empty tables, so a later load or report starts from a known state.

## Behavior

- `ledger init` drops `accounts`, `categories`, and `transactions` if they exist, then recreates them empty from the generated schema through the `persistence` package.
- The drop and recreate run inside one command transaction (FEATURE-Command-Transaction.md).
- `init` writes nothing to standard output and exits 0.
- Argument-count errors are rejected by FEATURE-CLI-Dispatch.md before this handler runs.

## Programmatic Acceptance

=== AC schema-init-exit-and-silent ===
Intent: `ledger init` exits 0 and writes nothing to standard output on a fresh database.

import os
import tempfile

from cli.testing import cli_runner

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn

code, out, err = cli_runner("init")
assert code == 0
assert out == ""
=== END AC schema-init-exit-and-silent ===

=== AC schema-init-drops-existing-rows ===
Intent: Running `ledger init` against a store holding a row leaves all three tables empty.

import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn

seeded = open_database(dsn)
seeded.accounts.create(account="INITA", name="Before Init")
assert len(seeded.accounts.list()) == 1

code, out, err = cli_runner("init")
assert code == 0
assert out == ""

after = open_database(dsn)
assert len(after.accounts.list()) == 0
assert len(after.categories.list()) == 0
assert len(after.transactions.list()) == 0
=== END AC schema-init-drops-existing-rows ===

=== AC schema-init-recreates-usable-schema ===
Intent: After `ledger init` runs a second time, the recreated tables accept a new row.

import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn

first_code, first_out, first_err = cli_runner("init")
assert first_code == 0
second_code, second_out, second_err = cli_runner("init")
assert second_code == 0
assert second_out == ""

db = open_database(dsn)
db.accounts.create(account="INITB", name="After Init")
assert len(db.accounts.list()) == 1
=== END AC schema-init-recreates-usable-schema ===

## User Acceptance

- None.

## Guardrails

- `init` does not read any file under `sources/`.
- `init` never writes to standard output.
- Schema objects are created only through the generated `schema.sql`, never by inline SQL in this handler.
