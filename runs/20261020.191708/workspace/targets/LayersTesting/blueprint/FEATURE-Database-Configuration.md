# FEATURE: Database Configuration

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Resolve configured database storage and report operational database failures. |
| Depends On  | ARCHITECTURE.md, DATABASE.md |
| Provides    | DATABASE_URL resolution, DATABASE_PATH fallback, default database path, operational error handling |
| Consumes    | schema initialization |

## Workflow

For every command, resolve the database location in this order:

1. `DATABASE_URL`
2. `DATABASE_PATH`
3. `data/app.db`

SQLite paths and `sqlite://` paths use the shipped SQLite persistence engine. PostgreSQL DSNs use the shipped PostgreSQL engine. Missing tables, unreachable databases, and other infrastructure failures produce exit code `1`, no standard-output data, and one diagnostic on standard error.

## Programmatic Acceptance

=== AC database-config-precedence ===
Intent: The CLI uses a configured SQLite database and initializes it successfully.
import os
import tempfile
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as directory:
    database_path = os.path.join(directory, "configured.db")
    old_url = os.environ.get("DATABASE_URL")
    old_path = os.environ.get("DATABASE_PATH")
    try:
        os.environ["DATABASE_URL"] = database_path
        os.environ["DATABASE_PATH"] = os.path.join(directory, "fallback.db")
        code, stdout, stderr = cli_runner("init")
        assert code == 0
        assert stdout == ""
    finally:
        if old_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = old_url
        if old_path is None:
            os.environ.pop("DATABASE_PATH", None)
        else:
            os.environ["DATABASE_PATH"] = old_path
=== END AC database-config-precedence ===

=== AC database-config-operational-failure ===
Intent: A database with missing required tables produces an operational failure with no data output.
import os
import tempfile
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as directory:
    database_path = os.path.join(directory, "empty.db")
    old_url = os.environ.get("DATABASE_URL")
    old_path = os.environ.get("DATABASE_PATH")
    try:
        os.environ["DATABASE_URL"] = database_path
        os.environ.pop("DATABASE_PATH", None)
        code, stdout, stderr = cli_runner("count")
        assert code == 1
        assert stdout == ""
        assert stderr != ""
    finally:
        if old_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = old_url
        if old_path is None:
            os.environ.pop("DATABASE_PATH", None)
        else:
            os.environ["DATABASE_PATH"] = old_path
=== END AC database-config-operational-failure ===

## User Acceptance

- None.

## Guardrails

- Configuration precedence must remain deterministic.
- Database drivers may be reached only through the shipped persistence library.
- Operational failures must not emit standard-output data.
