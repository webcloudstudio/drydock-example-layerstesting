# ARCHITECTURE: Ledger Application

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Defines the command-line ledger boundaries, configuration precedence, transactional services, and persistence access rules. |
| Depends On  | — |
| Provides    | ledger application boundaries, configuration boundary, persistence boundary |
| Consumes    | — |

## Purpose

The application is a Python command-line cash ledger. The executable routes validated commands to transactional services, which use the generated `persistence` package for all database access.

## Technology Stack

- Python 3.11 or newer: application and tests.
- SQLite: default relational database.
- CLI: executable `ledger` at the application root.
- pytest: project test suite.
- POSIX Shell: `bin/test.sh`.
- Shipped persistence library: exclusive database access boundary.

## Module Ownership

| Boundary | Owner | Responsibility |
|---|---|---|
| CLI routing | `cli` and root `ledger` launcher | Parse commands, validate usage, map outcomes to exit codes, and emit CSV. |
| Configuration | application configuration module | Resolve `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`. |
| Validation | validation services | Validate codes, text fields, amounts, dates, references, and balances. |
| Transactions | command services | Execute each command within one database transaction and roll back rejected changes. |
| Reporting | report services | Query and aggregate stored integer cents without embedded report values. |
| Persistence | generated `persistence` package | Own connections, schema operations, and repository calls. Application code never opens a database driver. |
| Test harness | `bin/test.sh` and pytest suite | Exercise the completed application against temporary databases. |

## Command Flow

`ledger` resolves configuration, dispatches a command, opens the configured database through `persistence.open_database`, begins one transaction, validates and performs the operation, emits success CSV, and commits. Any failure rolls back and emits one diagnostic line to standard error.

## Data Rules

Amounts are integer cents at every application and persistence boundary. Account balances are sums of transaction amounts and must remain non-negative after every mutating command. Reports derive all values from database queries.

## Programmatic Acceptance

=== AC architecture-boundaries ===
Intent: The built application exposes the selected persistence and CLI foundation entry points.

from pathlib import Path
import importlib

assert Path("ledger").is_file()
cli = importlib.import_module("cli")
persistence = importlib.import_module("persistence")
assert callable(cli.main)
assert callable(persistence.open_database)
=== END AC architecture-boundaries ===

=== AC architecture-launcher ===
Intent: The root launcher is executable and delegates to the CLI entry point.

from pathlib import Path
import os

launcher = Path("ledger")
assert launcher.is_file()
assert os.access(launcher, os.X_OK)
=== END AC architecture-launcher ===

## User Acceptance

- None.

## Guardrails

- Application code must not import or open a database driver directly.
- No floating-point representation may be used for money.
- Commands must be atomic.
- Reports must be computed from stored data.
