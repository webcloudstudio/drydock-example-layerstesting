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

| Technology | Rigging | Role |
|------------|---------|------|
| Python 3.11 or newer | `python.md` | Implementation language. |
| SQLite | `sqlite.md` | Database engine, reached through `persistence.open_database` and the shipped SQLite engine. |
| PostgreSQL | `python.md` (persistence contract) | Selected only by a `postgres://` or `postgresql://` DSN through the same shipped library. Not verified by any acceptance check. |
| CLI | `cli.md` | The `ledger` executable at the application root. |
| pytest | `python.md` | Test runner behind `bin/test.sh`. |
| POSIX sh | `common.md` | `bin/test.sh`, `bin/sync.sh`, the `ledger` launcher, and the supplied grader. |

Dependency management uses `uv`: `pyproject.toml` declares the project and its dependencies,
`uv.lock` is the committed lock file, and `.venv/` is the environment directory created by
`uv venv` (gitignored).

## Module Layout

- `ledger`: POSIX launcher at the application root. It changes to the application root and runs `cli.main` under `.venv`.
- `pyproject.toml` and `uv.lock`: dependency manifest and committed lock file. Runtime dependency `psycopg[binary]`; dev group `pytest`.
- `.venv/`: environment created by `uv venv`. Not committed.
- `bin/`: POSIX launchers. `bin/sync.sh` creates `.venv` and installs from `uv.lock`; `bin/test.sh` activates `.venv` and runs `pytest -q`.
- `config.py`: database target resolution from the environment.
- `cli/`: `main(argv)` entry point, `cli_runner` test client, command dispatch, and CSV output.
- `commands/`: one module per command group (accounts, categories, transactions, transfers, loads, reports). Each command body runs inside the command transaction wrapper.
- `persistence/` and `schema.sql`: generated from `DATABASE.md` at the DATABASE step.
- `tests/`: pytest suite for the application. `tests/test_foundation.py` covers the project manifest, lock file, environment, and launchers.

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

## Guardrails

- Application code never opens a database driver outside the shipped persistence library.
- Money is stored and computed as integer cents at every layer.
- No command writes outside the application root and its temporary test database.
- No report row, count, or total is embedded in code.
