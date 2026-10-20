# ARCHITECTURE: Cash Ledger

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Module layout, boundaries, and technology decisions for the command-line cash ledger. |

## Purpose

The `ledger` executable is a command-line cash ledger for a small shop. Commands read CSV on
standard output, diagnostics on standard error, and exit codes 0 to 4. Every command runs as one
database transaction. All persistence goes through the shipped persistence library, and the
database is selected by `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`.

## Technology Stack

- Python 3.11 or newer: implementation language. Governed by `python.md`.
- SQLite: database engine, reached through `persistence.open_database` and the shipped SQLite engine. Governed by `sqlite.md`.
- PostgreSQL: selected only by a `postgres://` or `postgresql://` DSN through the same shipped library. Not verified by any acceptance check.
- CLI: the `ledger` executable at the application root. Governed by `cli.md`.
- pytest: test runner behind `bin/test.sh`. Governed by `python.md`.
- POSIX sh: `bin/test.sh`, the `ledger` launcher, and the supplied grader. Governed by `common.md`.

## Module Layout

- `ledger`: POSIX launcher at the application root. It changes to the application root and runs `cli.main` under `.venv`.
- `pyproject.toml` and `uv.lock`: dependency manifest and committed lock file.
- `.venv/`: environment created by `uv venv`.
- `bin/`: POSIX launchers, including `bin/test.sh`.
- `config.py`: database target resolution from the environment.
- `cli/`: `main(argv)` entry point, `cli_runner` test client, command dispatch, and CSV output.
- `commands/`: one module per command group (accounts, categories, transactions, transfers, loads, reports). Each command body runs inside the command transaction wrapper.
- `persistence/` and `schema.sql`: generated from `DATABASE.md` at the DATABASE step.
- `tests/`: pytest suite for the application.

## Boundaries

- Call direction is `cli` to `commands` to `persistence`. The `cli` package never opens a database.
- `commands` reach storage only through `db.<table>.<verb>(...)`, obtained from `persistence.open_database`.
- Application code never imports `sqlite3` or any PostgreSQL driver. Only the shipped engines under `persistence/` do.
- `config.py` reads the environment and returns the selected target as a string. It never opens a connection.
- No command reads `sources/run.sh` or any seed file except through `ledger load`.

## Module Ownership

| Boundary | Owner | Low-level APIs it may access |
|----------|-------|------------------------------|
| Persistence | `persistence/` (generated and shipped) | Driver APIs inside `persistence/sqlite.py` and `persistence/postgres.py` only |
| Configuration | `config.py` | `os.environ` for `DATABASE_URL`, `DATABASE_PATH` |
| File store | None | None. Seed files are read only by `ledger load`, through `commands/` |
| External service | None | None |

## Transaction and Balance Boundary

- The `commands` layer opens one transaction per command and commits it only after every change succeeds.
- Before commit, the balance rule is checked for every affected account. A negative balance rolls the command back and exits 3.
- Concurrency relies on the database's own transaction isolation. No application-level locking is added.

## Programmatic Acceptance

=== AC architecture-python-manifest ===
Intent: pyproject.toml declares a project requiring Python 3.11 or newer.

import tomllib
from pathlib import Path

data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
requires = data["project"]["requires-python"]
assert isinstance(requires, str)
assert "3.11" in requires
=== END AC architecture-python-manifest ===

=== AC architecture-dependency-manifest ===
Intent: pyproject.toml declares psycopg for the PostgreSQL engine and pytest for the test runner.

import tomllib
from pathlib import Path

data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
dependencies = list(data["project"]["dependencies"])
dev_group = list(data.get("dependency-groups", {}).get("dev", []))
assert any(item.startswith("psycopg") for item in dependencies)
assert any(item.startswith("pytest") for item in dependencies + dev_group)
=== END AC architecture-dependency-manifest ===

=== AC architecture-lock-and-venv ===
Intent: uv.lock is committed at the application root and .venv exists as the environment directory.

from pathlib import Path

assert Path("uv.lock").is_file()
assert Path(".venv").is_dir()
=== END AC architecture-lock-and-venv ===

## User Acceptance

- None.

## Guardrails

- Application code never opens a database driver outside the shipped persistence library.
- Money is stored and computed as integer cents at every layer.
- No command writes outside the application root and its temporary test database.
- No report row, count, or total is embedded in code.
