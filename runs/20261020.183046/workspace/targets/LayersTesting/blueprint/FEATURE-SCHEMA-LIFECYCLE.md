# FEATURE: Schema Lifecycle

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Initialize the ledger schema and report row counts for all required tables. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-CLI-FOUNDATION.md |
| Provides    | `ledger init`, `ledger count` |
| Consumes    | accounts repository, categories repository, transactions repository |

## Behavior

`ledger init` drops and recreates `accounts`, `categories`, and `transactions` as an atomic schema reset. It writes nothing to standard output.

`ledger count` emits the header `table,rows`, followed by the row counts in this fixed order:

1. `accounts`
2. `categories`
3. `transactions`

A database operational failure returns exit code `1`.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC schema-init-empty ===
Intent: Initialization leaves all three declared tables empty and count reports their state.

import csv
import os
import tempfile
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as directory:
    old = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = os.path.join(directory, "ledger.db")
    os.environ.pop("DATABASE_URL", None)
    try:
        init_code, init_out, init_err = cli_runner("init")
        assert init_code == 0
        assert init_out == ""

        count_code, count_out, count_err = cli_runner("count")
        assert count_code == 0
        rows = list(csv.reader(count_out.splitlines()))
        assert len(rows) == 4
        assert rows[0] == ["table", "rows"]
        assert [row[1] for row in rows[1:]] == ["0", "0", "0"]
    finally:
        if old is None:
            os.environ.pop("DATABASE_PATH", None)
        else:
            os.environ["DATABASE_PATH"] = old
=== END AC schema-init-empty ===

=== AC schema-reinitializes ===
Intent: A second initialization removes previously stored rows.

import csv
import os
import tempfile
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as directory:
    old = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = os.path.join(directory, "ledger.db")
    os.environ.pop("DATABASE_URL", None)
    try:
        assert cli_runner("init")[0] == 0
        assert cli_runner("account", "add", "TEMP", "Temporary")[0] == 0
        assert cli_runner("init")[0] == 0

        code, output, error = cli_runner("count")
        assert code == 0
        rows = list(csv.reader(output.splitlines()))
        assert len(rows) == 4
        assert [row[1] for row in rows[1:]] == ["0", "0", "0"]
    finally:
        if old is None:
            os.environ.pop("DATABASE_PATH", None)
        else:
            os.environ["DATABASE_PATH"] = old
=== END AC schema-reinitializes ===

=== AC schema-count-order ===
Intent: Count exposes exactly one row for each required table in the documented order.

import csv
import os
import tempfile
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as directory:
    old = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = os.path.join(directory, "ledger.db")
    os.environ.pop("DATABASE_URL", None)
    try:
        assert cli_runner("init")[0] == 0
        code, output, error = cli_runner("count")
        assert code == 0
        rows = list(csv.reader(output.splitlines()))
        assert [row[0] for row in rows[1:]] == ["accounts", "categories", "transactions"]
    finally:
        if old is None:
            os.environ.pop("DATABASE_PATH", None)
        else:
            os.environ["DATABASE_PATH"] = old
=== END AC schema-count-order ===

## User Acceptance

- None.

## Guardrails

- `init` must not emit standard output.
- Reinitialization must remove rows from all three tables.
- Count values must come from database queries, not hardcoded report data.
