# ARCHITECTURE: LayersTesting

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Modules, boundaries, and technical decisions for the LayersTesting cash ledger CLI. |
| Depends On | None |
| Provides | bin/test.sh, pyproject.toml, tests/conftest.py |

## Purpose

`ledger` is a single-executable command-line cash ledger. It keeps accounts, categories, and cash
transactions in a relational database reached only through the shipped persistence library, rejects
a failing command before it writes, enforces non-negative balances, and reports balances, category
totals, and monthly totals. All values come from queries; no report row, count, or total is embedded.

## Technology Stack

Derived from `TECHNOLOGY_STACK.md`, which remains the decision of record.

| Technology | Where it applies |
|---|---|
| Python 3.11 or newer | Implementation language for every module. |
| SQLite | The database, reached only through the shipped persistence package. |
| CLI | The `ledger` executable at the application root and the `cli` package behind it. |
| pytest | The test runner behind `bin/test.sh`. |
| POSIX sh | `bin/test.sh` and the supplied grader `sources/run.sh`. |

## Project Layout

| Path | Role |
|---|---|
| `ledger` | Executable at the application root; calls `cli.main` and exits with its return value. |
| `cli/` | Command-line package: dispatch, errors, validators, money, output, commands. |
| `cli/commands/` | One module per command; each registers a handler with the command registry. |
| `persistence/` | Generated and shipped by Drydock from `DATABASE.md`; never hand-written. |
| `tests/` | The project's own pytest suite, with `conftest.py` exposing `db_session` and `cli_runner`. |
| `bin/test.sh` | POSIX sh launcher: activates `.venv`, runs `pytest -q` from the root, exits zero only when all tests pass. |
| `pyproject.toml`, `uv.lock` | Dependency manifest and committed lock; environment created by `uv venv`. |
| `sources/` | Read-only scoring assets staged by Drydock; application code never reads them. |

## Module Ownership

| Boundary | Owning module | Allowed low-level access |
|---|---|---|
| Persistence | `persistence/` (generated) | The only package that imports a database driver. |
| Configuration | `persistence.open_database` via `cli.database` | Resolves `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`. |
| File stores | None | Command modules read only the CSV path named on the command line. |
| External services | None | No network access. |

Callers use `db.<table>.<operation>(...)` as declared in `DATABASE.md`. SQL, sessions, table names,
and column names never cross that boundary, and no command issues DDL.

## Technical Decisions

- Money is integer cents at every layer; floating point is never used. Parsing and formatting use
  integer arithmetic only.
- Every command validates its full input and every business rule before its first write.
- Sums, counts, balances, and the next transaction id are computed by services from listed rows.
- Standard output carries only CSV (`\n` endings, no quoting); diagnostics go to standard error.
- Exit codes: 0 success, 1 operational, 2 usage, 3 rejected, 4 not found.
- Commands register themselves in a registry; the dispatcher checks arity before opening the database.

## Programmatic Acceptance

=== AC architecture-python-version ===
Intent: The build runs on Python 3.11 or newer, as the technology stack requires.

import sys

assert sys.version_info >= (3, 11)
=== END AC architecture-python-version ===

=== AC architecture-pyproject ===
Intent: pyproject.toml parses as TOML and declares a project table.

import tomllib
from pathlib import Path

path = Path("pyproject.toml")
assert path.is_file()
data = tomllib.loads(path.read_text(encoding="utf-8"))
assert "project" in data
=== END AC architecture-pyproject ===

=== AC architecture-test-launcher ===
Intent: bin/test.sh exists and is syntactically valid POSIX sh.

import subprocess
from pathlib import Path

launcher = Path("bin/test.sh")
assert launcher.is_file()
result = subprocess.run(["sh", "-n", str(launcher)], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC architecture-test-launcher ===

=== AC architecture-conftest ===
Intent: tests/conftest.py exists as the pytest fixture module.

from pathlib import Path

assert Path("tests/conftest.py").is_file()
=== END AC architecture-conftest ===

## User Acceptance

- None.

## Guardrails

- Only the shipped persistence package touches a database driver.
- Money is never floating point at any layer.
- Application code never reads `sources/run.sh` or any seed file, and never embeds a report answer.
- Nothing under `sources/` is modified.
