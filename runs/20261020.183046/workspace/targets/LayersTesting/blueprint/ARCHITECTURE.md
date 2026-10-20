# ARCHITECTURE: Ledger Application Architecture

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Define the layered Python architecture and boundaries for the cash ledger CLI. |
| Depends On  | — |
| Provides    | application module boundaries, configuration boundary, persistence boundary |
| Consumes    | — |

## Purpose

The application is a local command-line cash ledger. Its layers are:

- `ledger` — executable launcher at the application root.
- `cli` — argument parsing, command dispatch, usage validation, and exit-code mapping.
- `ledger_app.config` — database configuration resolution.
- `ledger_app.services` — validation, business rules, atomic workflows, and report calculations.
- `persistence` — the shipped database boundary; application code never opens a database driver directly.

Commands validate their complete input and business rules before the first write. Mutating workflows use one database transaction and either commit all changes or roll them back.

## Module Ownership

| Boundary | Owning module | Allowed dependency |
|---|---|---|
| CLI parsing and dispatch | `cli` | configuration and services |
| Configuration | `ledger_app.config` | standard library only |
| Ledger workflows | `ledger_app.services` | `persistence` |
| Database access | shipped `persistence` package | database engine |
| Process entry point | `ledger` | `cli.main` |

The CLI does not contain SQL or database-driver imports. Services call repository methods exposed by `persistence.open_database`.

## Configuration

Resolve the database location in this order:

1. `DATABASE_URL`
2. `DATABASE_PATH`
3. `data/app.db`

The selected value is passed to `persistence.open_database`.

## Error Contract

Map outcomes to the documented exit codes:

- `0` success
- `1` operational failure
- `2` usage error
- `3` rejected command
- `4` absent record

Diagnostics are written to standard error. Successful command data is written to standard output.

## Technology Stack

- Python 3.11 or newer for the application and tests.
- SQLite through the shipped Python persistence library.
- POSIX shell for executable test launchers.
- pytest for the project test suite.

## Programmatic Acceptance

=== AC architecture-config-precedence ===
Intent: The configuration boundary exposes the documented database-source precedence.

import os
from ledger_app.config import database_dsn

saved = {key: os.environ.get(key) for key in ("DATABASE_URL", "DATABASE_PATH")}
try:
    os.environ["DATABASE_URL"] = "sqlite://url.db"
    os.environ["DATABASE_PATH"] = "path.db"
    assert database_dsn() == "sqlite://url.db"

    del os.environ["DATABASE_URL"]
    assert database_dsn() == "path.db"

    del os.environ["DATABASE_PATH"]
    assert database_dsn() == "data/app.db"
finally:
    for key, value in saved.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
=== END AC architecture-config-precedence ===

=== AC architecture-error-boundary ===
Intent: The application exposes distinct typed outcomes for usage, rejection, and not-found failures.

from ledger_app.errors import NotFoundError, RejectedError, UsageError

assert issubclass(UsageError, Exception)
assert issubclass(RejectedError, Exception)
assert issubclass(NotFoundError, Exception)
assert len({UsageError, RejectedError, NotFoundError}) == 3
=== END AC architecture-error-boundary ===

## User Acceptance

- None.

## Guardrails

- Application code must not import `sqlite3`, PostgreSQL drivers, or any other database driver.
- Application code must not read or embed files under `sources/`.
- Amounts remain integer cents throughout the application.
