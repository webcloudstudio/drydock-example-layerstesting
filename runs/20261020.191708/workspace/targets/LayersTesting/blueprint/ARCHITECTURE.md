# ARCHITECTURE: Ledger Application

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Define the command-line ledger boundaries, validation flow, and persistence encapsulation. |
| Depends On  | — |
| Provides    | application module boundaries, CLI boundary, configuration boundary, validation boundary |
| Consumes    | — |

## Purpose

The application is a Python 3.11+ command-line executable named `ledger`. Commands are dispatched through a thin CLI boundary into configuration, validation, service, reporting, and persistence callers.

## Modules and Boundaries

| Module | Responsibility |
|---|---|
| `ledger` / CLI package | Parse command arguments, dispatch commands, emit CSV, and map failures to exit codes. |
| Configuration | Resolve `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`. |
| Validation and services | Parse and validate codes, text, dates, amounts, references, balances, and atomic workflows before writes. |
| Persistence callers | Use only `persistence.open_database` and generated table operations. |
| Reporting | Query persisted rows and calculate report values using integer cents. |

Application code must never import or open a database driver directly. All database access crosses the shipped persistence library boundary. Monetary values remain integer cents at every application and persistence layer; floating-point arithmetic is prohibited.

## Command Flow

Commands resolve configuration, open the database through the persistence package, validate the complete operation, perform writes within an atomic workflow, and serialize successful results as CSV. Diagnostics go to standard error. Exit codes are `0` for success, `1` for operational failure, `2` for usage errors, `3` for rejected input or invariant violations, and `4` for absent records.

## Technology Stack

- Python 3.11 or newer implements the application and tests.
- SQLite is the supplied database path, accessed through the shipped persistence library.
- PostgreSQL DSNs are supported through the same persistence boundary.
- The CLI is the executable `ledger`.
- pytest runs the project suite.
- POSIX shell runs `bin/test.sh` and the supplied harness.

## Module Ownership

| Boundary | Owner | Allowed low-level access |
|---|---|---|
| Persistence | generated `persistence` package | database driver internals only |
| Configuration | application configuration module | environment variables and path handling |
| File input | load services | CSV file reading |
| CLI | command dispatcher | argument parsing, stdout, stderr, exit codes |
| Domain validation | service layer | validation and transaction planning |
| Reports | report services | declared persistence operations |

## Programmatic Acceptance

=== AC architecture-imports ===
Intent: The built application exposes the selected CLI and persistence foundation packages.
from importlib import import_module

cli_module = import_module("cli")
persistence_module = import_module("persistence")
assert hasattr(cli_module, "main")
assert hasattr(persistence_module, "open_database")
=== END AC architecture-imports ===

=== AC architecture-cli-contract ===
Intent: The CLI foundation exposes an in-process callable accepting an argument list.
from cli import main
import inspect

signature = inspect.signature(main)
assert "argv" in signature.parameters
assert main([]) == 2
=== END AC architecture-cli-contract ===

## User Acceptance

- None.

## Guardrails

- Application code must not open a database driver directly.
- Money must not use floating-point representation or arithmetic.
- Report values must be computed from persisted state.
