# ARCHITECTURE: Cash Ledger

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Modules, boundaries, and technology stack for the `ledger` cash-ledger command-line program. |
| Provides    | pyproject.toml, uv.lock, .venv, bin/ launchers |

## Purpose

The application is one executable named `ledger` at the application root. It records accounts,
categories, and cash transactions in a relational database, enforces atomic commands and
non-negative balances, and reports balances, category totals, and monthly totals. Every value is
computed by a query, and every amount is stored as integer cents.

## Technology Stack

- Python 3.11 or newer (`python.md`): implementation language.
- SQLite (`sqlite.md`): the database, reached only through the shipped persistence library. This
  build has no PostgreSQL backend.
- CLI (`cli.md`): the `ledger` executable at the application root.
- pytest (`python.md`): the test runner behind `bin/test.sh`.
- POSIX sh (`common.md`): `bin/test.sh` and the supplied grader.

## Foundation

- The project root holds `pyproject.toml` declaring Python 3.11 or newer, pytest, and ruff.
- `uv.lock` is committed beside `pyproject.toml`.
- `.venv` is created with `uv venv`. Launchers in `bin/` activate it.
- `pytest -q` is the project test runner.

## Modules

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

## Module Ownership

| Boundary | Owner | Allowed access |
|---|---|---|
| Persistence | `persistence` package generated from `DATABASE.md` | Domain modules call `open_database(dsn)` and `db.<table>.<verb>(...)` only. No module imports a database driver. |
| Configuration | `database_location` | Only module that reads `DATABASE_URL` and `DATABASE_PATH` |
| File store | None | Input CSV files are read only by `loader` |
| External service | None | No network access, except to a PostgreSQL server named by `DATABASE_URL`. This build rejects that DSN with exit 1. |

## Technical Decisions

- Amounts are stored and computed as integer cents. No floating-point type is used for money.
- Every command runs in one transaction through `command_transaction`. Any failure rolls back all changes.
- The balance rule runs after a command's changes and before commit, for every touched account.
- Application code never reads `sources/run.sh` or any seed file. Seed files reach the database only through `ledger load`.
- Reports are computed from the database. No report answer is embedded in code.

## Programmatic Acceptance

=== AC arch-python-version ===
Intent: The running interpreter is Python 3.11 or newer, as the Technology Stack requires.

import sys

assert sys.version_info[:2] >= (3, 11)
=== END AC arch-python-version ===

=== AC arch-pyproject ===
Intent: pyproject.toml exists at the project root and parses as TOML with a project table.

import tomllib

with open("pyproject.toml", "rb") as handle:
    data = tomllib.load(handle)
assert isinstance(data["project"], dict)
=== END AC arch-pyproject ===

=== AC arch-uv-lock ===
Intent: uv.lock is committed at the project root beside pyproject.toml.

from pathlib import Path

assert Path("uv.lock").is_file()
=== END AC arch-uv-lock ===

## User Acceptance

- None.

## Guardrails

- Do not modify, rewrite, or substitute any file under `sources/`.
- Do not open a database driver outside the `persistence` package.
- Do not use floating point for money at any layer.
