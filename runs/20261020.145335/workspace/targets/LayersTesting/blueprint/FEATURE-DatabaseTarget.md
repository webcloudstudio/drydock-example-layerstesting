# FEATURE: Database Target

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Resolves the database target from the environment and opens it through the shipped persistence library. |
| Depends On  | ARCHITECTURE.md, DATABASE.md |
| Provides    | resolve_database_target() |
| Consumes    | open_database |

## Purpose

Every command needs one database target. `config.resolve_database_target()` returns the setting
that applies by precedence: `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`. The value is
returned unchanged, including any `postgres://`, `postgresql://`, or `sqlite://` prefix, and is
passed to `persistence.open_database` as the DSN.

## Behavior

- If `DATABASE_URL` is set and non-empty, its value is the target.
- Otherwise, if `DATABASE_PATH` is set and non-empty, its value is the target.
- Otherwise the target is `data/app.db`.
- The function reads the environment only. It opens no connection.

## Programmatic Acceptance

=== AC target-precedence ===
Intent: DATABASE_URL takes precedence over DATABASE_PATH, which takes precedence over data/app.db, and each value is returned unchanged.

import os
from config import resolve_database_target

for name in ("DATABASE_URL", "DATABASE_PATH"):
    os.environ.pop(name, None)
default_target = "data/app.db"
assert resolve_database_target() == default_target

path_value = "scratch.db"
os.environ["DATABASE_PATH"] = path_value
assert resolve_database_target() == path_value

url_value = "sqlite://" + path_value
os.environ["DATABASE_URL"] = url_value
assert resolve_database_target() == url_value

postgres_value = "postgresql://ledger@localhost/ledger"
os.environ["DATABASE_URL"] = postgres_value
assert resolve_database_target() == postgres_value
=== END AC target-precedence ===

=== AC target-opens-store ===
Intent: The resolved target opens through the shipped persistence library and yields an empty accounts table.

import os
import tempfile
from pathlib import Path
from config import resolve_database_target
from persistence.testing import db_session

os.environ.pop("DATABASE_URL", None)
scratch_dir = tempfile.mkdtemp()
path_value = str(Path(scratch_dir) / "ledger.db")
os.environ["DATABASE_PATH"] = path_value
target = resolve_database_target()
assert target == path_value
with db_session(target) as db:
    rows = db.accounts.list()
    print(rows)
    assert rows == []
=== END AC target-opens-store ===

## User Acceptance

- None.

## Guardrails

- The target is never opened by this module; only persistence opens connections.
- No default target other than `data/app.db` is applied when either setting is present.
