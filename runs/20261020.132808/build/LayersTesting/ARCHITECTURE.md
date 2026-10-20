# ARCHITECTURE: Cash Ledger

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Modules, boundaries, and technology stack for the `ledger` cash-ledger command-line program. |
| Provides    | pyproject.toml, uv.lock, .venv, bin/ launchers |

## Technology Stack

Derived from the Blueprint `ARCHITECTURE.md` and the Python foundation.

- Python 3.11 or newer (`pyproject.toml` `requires-python = ">=3.11"`): implementation language.
- SQLite: the database, reached only through the shipped `persistence` package. This build has no
  PostgreSQL backend.
- CLI: the `ledger` executable at the application root.
- pytest: the test runner behind `bin/test.sh` (`pytest -q`).
- ruff: the linter behind `bin/lint.sh`.
- POSIX sh: the launchers in `bin/`.

## Foundation

- The project root holds `pyproject.toml` (Python 3.11 or newer, dev group: pytest, ruff).
- `uv.lock` is committed beside `pyproject.toml`.
- `.venv` is created with `uv venv` and managed with `uv`. Launchers in `bin/` put `.venv/bin` on
  `PATH`; they contain no business logic.
- `pytest -q` is the project test command.

## Module Ownership

| Boundary | Owner | Allowed access |
|---|---|---|
| Persistence | `persistence` package generated from `DATABASE.md` | Domain modules call `open_database(dsn)` and `db.<table>.<verb>(...)` only. No module imports a database driver. |
| Configuration | `database_location` | Only module that reads `DATABASE_URL` and `DATABASE_PATH` |
| File store | None | Input CSV files are read only by `loader` |
| External service | None | No network access, except to a PostgreSQL server named by `DATABASE_URL`. This build rejects that DSN with exit 1. |

## Module Responsibilities

| Module | Responsibility |
|---|---|
| `cli` | Entry `main(argv)`, command routing, usage listing, CSV output writer, operational error mapping to exit codes |
| `database_location` | Resolves the database location from `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db` |
| `persistence` (generated) | Store access through `open_database(dsn)` and `db.<table>.<verb>(...)` |
| `command_transaction` | Runs each command inside one database transaction; rolls back on any failure |
| `validation` | Codes, names, memos, amounts as integer cents, calendar dates |
| `balance` | Non-negative balance check after a command's changes and before commit |
| `loader` | Bulk CSV loads, all or nothing |
| `accounts` | Account add, get, rename, delete |
| `transactions` | Post, get, amend, delete, and the next-id rule |
| `transfers` | Two-row transfer stored as `TRANSFER` rows, or neither |
| `reports` | Balances, categories, and monthly reports computed by query |
