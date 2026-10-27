# ARCHITECTURE: LayersTesting

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Modules, boundaries, and technical decisions for the LayersTesting command-line cash ledger. |
| Provides | project tree, bin/test.sh |

## Purpose

The product is an executable named `ledger` at the application root. It keeps accounts, categories, and cash transactions in SQLite through the generated `persistence` package. Every command either completes in full or changes nothing. This file states the module layout and boundaries every other Blueprint builds into.

## Technology Stack

Derived from `TECHNOLOGY_STACK.md`, which remains the decision of record.

| Technology | Where it applies |
|---|---|
| Python 3.11+ | All application code, the `ledger` launcher target, and the tests. |
| SQLite | The only store, reached through the generated `persistence` package. |
| CLI | The `ledger` executable and the `cli` package. |
| pytest | Test runner behind `bin/test.sh`. |
| POSIX sh | `bin/test.sh` and the `ledger` launcher. |

## Project Tree

| Path | Owner story | Purpose |
|---|---|---|
| `pyproject.toml`, `uv.lock` | foundation-python | Dependency manifest and committed lock. |
| `bin/test.sh` | foundation-python | POSIX launcher: activates `.venv`, runs `pytest -q` from the application root, exits zero only when every test passes. |
| `conftest.py` | foundation-python | Exposes the `db_session` and `cli_runner` fixtures. |
| `ledger_core/` | foundation-python and later services | Domain logic: `config`, `errors`, then `validation`, `money`, `balances`, `csvio`, `accounts`, `transactions`, `reports` added by their own stories. |
| `persistence/` | Drydock (generated) | Repository layer generated from `DATABASE.md`. |
| `cli/` | foundation-cli | `main`, registry, command modules, `testing.cli_runner`. |
| `ledger` | foundation-cli | Executable launcher at the application root. |
| `tests/` | each story | The project's own test suite. |

## Module Ownership

| Boundary | Owning module | May access |
|---|---|---|
| Persistence | `persistence` (generated) | The SQLite driver, the only module that does. |
| Configuration | `ledger_core.config` | `DATABASE_URL`, `DATABASE_PATH`, process environment. |
| Domain errors | `ledger_core.errors` | Nothing external. |
| Money and validation | `ledger_core.money`, `ledger_core.validation` | Nothing external; pure functions. |
| Command dispatch and output | `cli` | stdout, stderr, `ledger_core`, `persistence.open_database`. |
| File stores | none | The only files read are CSV files named on a command line, through `ledger_core.csvio`. |
| External services | none | No network access. |

No module outside `persistence` imports `sqlite3` or any other database driver. Callers use `db.<table>.<operation>(...)`.

## Configuration

`ledger_core.config.database_path() -> str` resolves `DATABASE_URL` first, with an optional leading `sqlite://` removed, then `DATABASE_PATH`, then `data/app.db`. An unset or empty value is skipped. A database location that cannot be opened is an operational failure: exit `1`, nothing written.

## Errors and Exit Codes

`ledger_core.errors` defines `LedgerError` with an integer `exit_code` attribute and three subclasses.

| Class | exit_code | Meaning |
|---|---|---|
| `Rejected` | 3 | Invalid input, duplicate key, unknown reference, account in use, negative balance. |
| `NotFound` | 4 | Absent account or transaction on get, rename, delete, or amend. |
| `Operational` | 1 | Unreadable file or unopenable database. |

Usage errors (exit `2`) are produced by `cli` dispatch and are not domain errors.

## Money

Amounts are integer cents at every layer: parsing, storage, arithmetic, and reports. Floating point is never used for money. Text is produced only at output by `ledger_core.money.format_cents`.

## Atomicity

Every writing command validates all inputs and rules, including the no-negative-balance rule, before its first write. A rejected command writes nothing.

## Test Command

`sh bin/test.sh` runs `pytest -q` and is the verification command for every behavioral story.

## Programmatic Acceptance

=== AC arch-project-files ===
Intent: The project root carries the dependency manifest, lock, pytest conftest, and a test launcher that runs pytest.

from pathlib import Path

for name in ["pyproject.toml", "uv.lock", "conftest.py", "bin/test.sh"]:
    assert Path(name).is_file(), name
launcher = Path("bin/test.sh").read_text()
assert "pytest" in launcher
=== END AC arch-project-files ===

=== AC arch-packages-import ===
Intent: The ledger_core package and its foundation modules import.

import ledger_core
import ledger_core.config
import ledger_core.errors

assert callable(ledger_core.config.database_path)
=== END AC arch-packages-import ===

=== AC arch-config-precedence ===
Intent: DATABASE_URL wins over DATABASE_PATH, an empty URL falls through, and with both unset the default path is used.

from drydock_acceptance import database_environment
from ledger_core.config import database_path

with database_environment(url="sqlite://primary.db", path="fallback.db") as root:
    assert str(database_path()) == str(root / "primary.db")
with database_environment(url="plain.db", path="fallback.db") as root:
    assert str(database_path()) == str(root / "plain.db")
with database_environment(url="", path="fallback.db") as root:
    assert str(database_path()) == str(root / "fallback.db")
with database_environment(path="fallback.db") as root:
    assert str(database_path()) == str(root / "fallback.db")
with database_environment() as root:
    assert str(database_path()) == "data/app.db"
=== END AC arch-config-precedence ===

=== AC arch-error-exit-codes ===
Intent: The three domain error classes derive from LedgerError and carry the exit codes 3, 4, and 1.

from ledger_core.errors import LedgerError, Rejected, NotFound, Operational

expected = {Rejected: 3, NotFound: 4, Operational: 1}
for cls, code in expected.items():
    assert issubclass(cls, LedgerError)
    err = cls("probe")
    assert err.exit_code == code
=== END AC arch-error-exit-codes ===

=== AC arch-driver-boundary ===
Intent: No application module outside the generated persistence package imports a database driver.

import ast
from pathlib import Path

banned = {"sqlite3", "psycopg", "psycopg2"}
checked = 0
assert Path("ledger_core").is_dir()
for root in ["ledger_core", "cli"]:
    base = Path(root)
    if not base.is_dir():
        continue
    for path in base.rglob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").split(".")[0]]
            else:
                continue
            assert not (banned & set(names)), (str(path), names)
        checked += 1
print(checked, "files scanned")
assert checked >= 1
=== END AC arch-driver-boundary ===

=== AC arch-no-float ===
Intent: Domain code contains no float call and no float literal, so money never uses floating point.

import ast
from pathlib import Path

checked = 0
for path in Path("ledger_core").rglob("*.py"):
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "float", str(path)
        if isinstance(node, ast.Constant):
            assert not isinstance(node.value, float), str(path)
    checked += 1
print(checked, "files scanned")
assert checked >= 1
=== END AC arch-no-float ===

## User Acceptance

- None.

## Guardrails

- Do not modify any file under `sources/`.
- Application code never reads `sources/run.sh` or any seed file; seed files reach the database only through `ledger load`.
- Do not hardcode a report row, a count, or a total; every value comes from a query.
- Do not open a database driver outside the generated persistence package.
- Do not use floating point for money at any layer.
- The ledger runs without network access.
- Diagnostics go to standard error and are never compared.
