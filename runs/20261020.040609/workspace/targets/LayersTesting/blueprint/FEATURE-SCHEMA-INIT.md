# FEATURE: Schema Init

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Implements `ledger init`, which drops and recreates the accounts, categories, and transactions tables empty. |
| Depends On  | DATABASE.md, FEATURE-EXIT-CODES.md, FEATURE-TEST-RUNNER.md |
| Provides    | ledger init |
| Consumes    | open_database(dsn) |

## Purpose

`ledger init` gives the ledger an empty three-table schema. It is the first command the shop runs, and it is the only command that removes all rows.

## Behavior

- `ledger init` drops the `accounts`, `categories`, and `transactions` tables if present, then recreates them empty from the generated `schema.sql`.
- The command writes nothing to standard output and exits 0 on success.
- The command runs inside one database transaction, as required by FEATURE-ATOMIC-COMMANDS.
- Drop and recreate uses the generated schema lifecycle only. It adds no repository operation to `DATABASE.md`.
- An unreachable database exits 1 through the exit-code mapping in FEATURE-EXIT-CODES.

## Programmatic Acceptance

=== AC init-creates-empty-schema ===
Intent: Running init on a fresh store exits 0, writes nothing to standard output, and leaves every table empty.

import os
import sys
import tempfile

from cli.testing import cli_runner
from persistence import open_database

with tempfile.TemporaryDirectory() as work:
    dsn = os.path.join(work, "ledger.db")
    os.environ["DATABASE_URL"] = dsn
    code, out, err = cli_runner("init")
    print(out)
    print(err, file=sys.stderr)
    assert code == 0
    assert out == ""
    db = open_database(dsn)
    assert len(db.accounts.list()) == 0
    assert len(db.categories.list()) == 0
    assert len(db.transactions.list()) == 0
=== END AC init-creates-empty-schema ===

=== AC init-drops-existing-rows ===
Intent: Running init again removes rows that were present before it ran.

import os
import sys
import tempfile

from cli.testing import cli_runner
from persistence import open_database

with tempfile.TemporaryDirectory() as work:
    dsn = os.path.join(work, "ledger.db")
    os.environ["DATABASE_URL"] = dsn
    code, out, err = cli_runner("init")
    assert code == 0
    db = open_database(dsn)
    db.accounts.create(account="CASH1", name="Till")
    db.categories.create(category="SALES", description="Sales receipts")
    assert len(db.accounts.list()) == 1
    assert len(db.categories.list()) == 1
    code, out, err = cli_runner("init")
    print(out)
    print(err, file=sys.stderr)
    assert code == 0
    db = open_database(dsn)
    assert len(db.accounts.list()) == 0
    assert len(db.categories.list()) == 0
=== END AC init-drops-existing-rows ===

## User Acceptance

- None.

## Guardrails

- `ledger init` never writes to standard output.
- `ledger init` never preserves a row from before it ran.
