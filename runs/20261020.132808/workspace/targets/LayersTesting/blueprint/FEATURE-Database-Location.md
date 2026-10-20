# FEATURE: Database Location

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Resolve the database location from DATABASE_URL, then DATABASE_PATH, then data/app.db, and reject PostgreSQL DSNs in this build. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-CLI-Platform.md |
| Provides    | resolve_database_location() |
| Consumes    | open_database(dsn) |

## Purpose

Every command finds its database through this resolution. The resolved value is passed to
`open_database(dsn)`. This feature does not open a connection.

## Interface

- `database_location.resolve_database_location() -> str` returns the location string.
- `database_location.DatabaseLocationError` is raised for an unsupported DSN.

## Resolution Rules

1. If `DATABASE_URL` is set, it is used.
2. Else, if `DATABASE_PATH` is set, it is used.
3. Else, the value is `data/app.db`, which is relative to the working directory.
4. A `sqlite://` prefix is removed. The remainder is the location.
5. A value beginning `postgres://` or `postgresql://` raises `DatabaseLocationError`. The CLI
   boundary maps that error to exit 1.

## Programmatic Acceptance

=== AC dbloc-default ===
Intent: With neither DATABASE_URL nor DATABASE_PATH set, the location is data/app.db.

import os

from database_location import resolve_database_location

keys = ("DATABASE_URL", "DATABASE_PATH")
saved = {key: os.environ.pop(key, None) for key in keys}
try:
    location = resolve_database_location()
finally:
    for key, value in saved.items():
        if value is not None:
            os.environ[key] = value
print(location)
assert location == "data/app.db"
=== END AC dbloc-default ===

=== AC dbloc-path-fallback ===
Intent: With only DATABASE_PATH set, the location is that path.

import os
import tempfile
from pathlib import Path

from database_location import resolve_database_location

keys = ("DATABASE_URL", "DATABASE_PATH")
saved = {key: os.environ.pop(key, None) for key in keys}
try:
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "ledger.db")
        os.environ["DATABASE_PATH"] = path
        location = resolve_database_location()
finally:
    for key, value in saved.items():
        if value is not None:
            os.environ[key] = value
print(location)
assert location == path
=== END AC dbloc-path-fallback ===

=== AC dbloc-url-precedence ===
Intent: When both DATABASE_URL and DATABASE_PATH are set, DATABASE_URL wins.

import os
import tempfile
from pathlib import Path

from database_location import resolve_database_location

keys = ("DATABASE_URL", "DATABASE_PATH")
saved = {key: os.environ.pop(key, None) for key in keys}
try:
    with tempfile.TemporaryDirectory() as tmp:
        url = str(Path(tmp) / "primary.db")
        other = str(Path(tmp) / "secondary.db")
        os.environ["DATABASE_URL"] = url
        os.environ["DATABASE_PATH"] = other
        location = resolve_database_location()
finally:
    for key, value in saved.items():
        if value is not None:
            os.environ[key] = value
print(location)
assert location == url
=== END AC dbloc-url-precedence ===

=== AC dbloc-sqlite-prefix ===
Intent: A sqlite:// prefix on DATABASE_URL is removed, leaving the file path.

import os
import tempfile
from pathlib import Path

from database_location import resolve_database_location

keys = ("DATABASE_URL", "DATABASE_PATH")
saved = {key: os.environ.pop(key, None) for key in keys}
try:
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "prefixed.db")
        os.environ["DATABASE_URL"] = "sqlite://" + path
        location = resolve_database_location()
finally:
    for key, value in saved.items():
        if value is not None:
            os.environ[key] = value
print(location)
assert location == path
=== END AC dbloc-sqlite-prefix ===

=== AC dbloc-postgres-rejected ===
Intent: postgres:// and postgresql:// DSNs raise DatabaseLocationError in this build.

import os

from database_location import DatabaseLocationError, resolve_database_location

keys = ("DATABASE_URL", "DATABASE_PATH")
saved = {key: os.environ.pop(key, None) for key in keys}
rejected = 0
try:
    for dsn in ("postgres://ledger@localhost/ledger", "postgresql://ledger@localhost/ledger"):
        os.environ["DATABASE_URL"] = dsn
        try:
            resolve_database_location()
        except DatabaseLocationError:
            rejected += 1
finally:
    for key, value in saved.items():
        if value is not None:
            os.environ[key] = value
print(rejected)
assert rejected == 2
=== END AC dbloc-postgres-rejected ===

## User Acceptance

- None.

## Guardrails

- This feature reads the environment only. It never opens a database connection.
- Application code outside this feature never reads `DATABASE_URL` or `DATABASE_PATH` directly.
