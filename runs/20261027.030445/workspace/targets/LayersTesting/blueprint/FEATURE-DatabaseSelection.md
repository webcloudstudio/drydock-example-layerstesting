# FEATURE: Database Selection

| Field       | Value |
|-------------|-------|
| Version     | 20261027 V1 |
| Description | Resolve the database location from configuration and open the store through the shipped persistence library. |
| Depends On  | ARCHITECTURE.md, DATABASE.md |
| Provides    | config.database_path, config.open_store |

## Purpose

Every command reads its database location from one place. `ledgerapp/config.py` resolves it and opens the store.

## Behavior

- `database_path() -> str` reads the environment at each call. It returns `DATABASE_URL` when set and non-empty, with one leading `sqlite://` prefix removed if present. Otherwise it returns `DATABASE_PATH` when set and non-empty. Otherwise it returns `data/app.db`.
- `open_store()` opens the resolved path through `persistence.open_database` and returns the `Database`. For the default path only, it first creates the parent directory if absent. For any other path no directory is created.
- When the database cannot be opened, `open_store()` raises `ledgerapp.errors.StoreUnavailable` (exit code 1). The CLI maps it to exit 1 with nothing on standard output and no record changed.
- This module imports no database driver and applies no DDL.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC config-url-prefix-stripped ===
Intent: DATABASE_URL with the sqlite:// prefix resolves to the bare path and wins over DATABASE_PATH.

import os

from ledgerapp import config

url_path = "/tmp/zq-ledger-url/ledger.db"
other_path = "/tmp/zq-ledger-other/ledger.db"
saved = {k: os.environ.get(k) for k in ("DATABASE_URL", "DATABASE_PATH")}
try:
    os.environ["DATABASE_URL"] = "sqlite://" + url_path
    os.environ["DATABASE_PATH"] = other_path
    assert str(config.database_path()) == url_path
finally:
    for key, value in saved.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
=== END AC config-url-prefix-stripped ===

=== AC config-url-without-prefix ===
Intent: DATABASE_URL given as a plain path is returned unchanged.

import os

from ledgerapp import config

plain_path = "/tmp/zq-ledger-plain/ledger.db"
saved = {k: os.environ.get(k) for k in ("DATABASE_URL", "DATABASE_PATH")}
try:
    os.environ["DATABASE_URL"] = plain_path
    os.environ.pop("DATABASE_PATH", None)
    assert str(config.database_path()) == plain_path
finally:
    for key, value in saved.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
=== END AC config-url-without-prefix ===

=== AC config-database-path-fallback ===
Intent: With DATABASE_URL unset, DATABASE_PATH is used.

import os

from ledgerapp import config

path_value = "/tmp/zq-ledger-fallback/ledger.db"
saved = {k: os.environ.get(k) for k in ("DATABASE_URL", "DATABASE_PATH")}
try:
    os.environ.pop("DATABASE_URL", None)
    os.environ["DATABASE_PATH"] = path_value
    assert str(config.database_path()) == path_value
finally:
    for key, value in saved.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
=== END AC config-database-path-fallback ===

=== AC config-default-path ===
Intent: With neither variable set, the path is the documented default data/app.db.

import os

from ledgerapp import config

default_path = "data/app.db"
saved = {k: os.environ.get(k) for k in ("DATABASE_URL", "DATABASE_PATH")}
try:
    os.environ.pop("DATABASE_URL", None)
    os.environ.pop("DATABASE_PATH", None)
    assert str(config.database_path()) == default_path
finally:
    for key, value in saved.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
=== END AC config-default-path ===

=== AC config-open-store-configured ===
Intent: open_store opens the configured provisioned store and the declared accounts operations answer on it.

from ledgerapp import config

db = config.open_store()
rows = db.accounts.list()
assert isinstance(rows, list)
=== END AC config-open-store-configured ===

=== AC config-open-store-unavailable ===
Intent: A path in a directory that does not exist cannot be opened, so open_store raises StoreUnavailable and creates no directory.

import os
import shutil
import tempfile

from ledgerapp import config
from ledgerapp.errors import StoreUnavailable

base = tempfile.mkdtemp()
missing_dir = os.path.join(base, "missing-dir")
bad_path = os.path.join(missing_dir, "ledger.db")
saved = {k: os.environ.get(k) for k in ("DATABASE_URL", "DATABASE_PATH")}
raised = False
try:
    os.environ["DATABASE_URL"] = bad_path
    os.environ.pop("DATABASE_PATH", None)
    try:
        config.open_store()
    except StoreUnavailable:
        raised = True
    assert raised
    assert not os.path.exists(missing_dir)
finally:
    for key, value in saved.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    shutil.rmtree(base, ignore_errors=True)
=== END AC config-open-store-unavailable ===

## User Acceptance

- None.

## Guardrails

- Do not import a database driver in this module.
- Do not apply DDL or create tables when opening the store.
- Create a directory only for the default path `data/app.db`.
