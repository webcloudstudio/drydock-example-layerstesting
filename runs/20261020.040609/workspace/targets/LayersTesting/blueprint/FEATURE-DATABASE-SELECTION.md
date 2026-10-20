# FEATURE: Database Selection

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Resolves the database location from the environment and reports connection failures as persistence errors. |
| Depends On  | DATABASE.md, FEATURE-TEST-RUNNER.md |
| Provides    | resolve_dsn(environ) -> str |
| Consumes    | open_database(dsn) |

## Purpose

Every command opens the database at the location the environment names. Resolution lives in
`config.py`, and the persistence library then selects the engine from the DSN.

## Behavior

- `resolve_dsn(environ)` returns the value of `DATABASE_URL` when it is set and non-empty.
- Otherwise it returns the value of `DATABASE_PATH` when that is set and non-empty.
- Otherwise it returns `data/app.db`.
- The returned value is the configured string unchanged. No normalization is applied.
- A `postgres://` or `postgresql://` DSN selects PostgreSQL. Any other value selects SQLite, with an
  optional `sqlite://` prefix. The persistence library makes that choice.
- Connection failures and expired connect attempts surface as `PersistenceError`, so the command
  layer can exit `1`.

## Programmatic Acceptance

=== AC db-selection-url-precedence ===
Intent: DATABASE_URL wins over DATABASE_PATH when both are set, and the value is returned unchanged.

import os
import tempfile

from config import resolve_dsn

directory = tempfile.mkdtemp()
url = os.path.join(directory, "url.db")
path = os.path.join(directory, "path.db")
assert resolve_dsn({"DATABASE_URL": url, "DATABASE_PATH": path}) == url
=== END AC db-selection-url-precedence ===

=== AC db-selection-path-fallback ===
Intent: DATABASE_PATH is used when DATABASE_URL is unset or empty.

import os
import tempfile

from config import resolve_dsn

directory = tempfile.mkdtemp()
path = os.path.join(directory, "path.db")
assert resolve_dsn({"DATABASE_PATH": path}) == path
assert resolve_dsn({"DATABASE_URL": "", "DATABASE_PATH": path}) == path
=== END AC db-selection-path-fallback ===

=== AC db-selection-postgres-dsn ===
Intent: A PostgreSQL DSN in DATABASE_URL is returned unchanged for the persistence library to select the engine.

from config import resolve_dsn

dsn = "postgresql://127.0.0.1:1/ledger"
assert resolve_dsn({"DATABASE_URL": dsn}) == dsn
=== END AC db-selection-postgres-dsn ===

=== AC db-selection-default ===
Intent: With neither variable set, resolution returns a non-empty database location.

from config import resolve_dsn

result = resolve_dsn({})
assert isinstance(result, str)
assert result != ""
=== END AC db-selection-default ===

=== AC db-selection-unreachable ===
Intent: An unreachable PostgreSQL server raises PersistenceError instead of returning a database.

Requires: python-package=psycopg; scope=runtime

from persistence import PersistenceError, open_database

dsn = "postgresql://127.0.0.1:1/ledger"
try:
    db = open_database(dsn)
    db.accounts.list()
except PersistenceError as error:
    failure = error
else:
    failure = None
print(failure)
assert isinstance(failure, PersistenceError)
=== END AC db-selection-unreachable ===

## User Acceptance

- None.

## Guardrails

- `config.py` is the only module that reads `DATABASE_URL` and `DATABASE_PATH`.
- Diagnostics never print a DSN password to standard output.
