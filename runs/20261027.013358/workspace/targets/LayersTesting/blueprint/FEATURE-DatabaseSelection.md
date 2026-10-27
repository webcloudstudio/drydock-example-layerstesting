# FEATURE: Database Selection

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Resolve the ledger database location from configuration and open it through the persistence library. |
| Depends On | FEATURE-CliEntry.md, DATABASE.md |
| Provides | ledgerlib.config |
| Consumes | cli.main, persistence |

## Purpose

Decide which database a command uses and refuse unsupported engines before anything is written.

## Interface

`ledgerlib/config.py`:

- `resolve_database(environ: Mapping[str, str] | None = None) -> str` returns the SQLite location
  using `DATABASE_URL`, else `DATABASE_PATH`, else `data/app.db`. A leading `sqlite://` is removed.
  `environ` defaults to `os.environ`; an unset or empty value counts as absent.
- A value beginning `postgres://` or `postgresql://` raises `OperationalError` (exit 1) before any
  file or directory is created or written.
- `open_ledger(environ: Mapping[str, str] | None = None)` returns an open persistence `Database` for
  the resolved location via `open_database`. An unreachable location, or an existing file that is
  not a valid database, raises `OperationalError`. Nothing is written to standard output.

## Database Interface

- None — persistence is declared by DATABASE.md and reached through `open_database`.

## Programmatic Acceptance

=== AC config-url-wins ===
Intent: DATABASE_URL takes precedence over DATABASE_PATH.

from ledgerlib.config import resolve_database

url_value = "zz_url_choice.db"
path_value = "zz_path_choice.db"
environ = {"DATABASE_URL": url_value, "DATABASE_PATH": path_value}
assert resolve_database(environ) == url_value
=== END AC config-url-wins ===

=== AC config-path-fallback ===
Intent: DATABASE_PATH is used when DATABASE_URL is unset.

from ledgerlib.config import resolve_database

path_value = "zz_path_only.db"
assert resolve_database({"DATABASE_PATH": path_value}) == path_value
=== END AC config-path-fallback ===

=== AC config-default ===
Intent: With neither variable set the default location data/app.db is used.

from ledgerlib.config import resolve_database

assert resolve_database({}) == "data/app.db"
=== END AC config-default ===

=== AC config-sqlite-prefix ===
Intent: An optional sqlite:// prefix is stripped from the location.

from ledgerlib.config import resolve_database

location = "zz_prefixed.db"
assert resolve_database({"DATABASE_URL": "sqlite://" + location}) == location
=== END AC config-sqlite-prefix ===

=== AC config-postgres-refused ===
Intent: A PostgreSQL DSN is refused with exit code 1 and no database file is created.

import os
import tempfile

from cli.errors import OperationalError
from ledgerlib.config import resolve_database

with tempfile.TemporaryDirectory() as tmp:
    would_create = os.path.join(tmp, "nested", "ledger.db")
    for dsn in ("postgres://localhost/ledger", "postgresql://localhost/ledger"):
        environ = {"DATABASE_URL": dsn, "DATABASE_PATH": would_create}
        raised = None
        try:
            resolve_database(environ)
        except OperationalError as exc:
            raised = exc
        assert raised is not None
        assert raised.exit_code == 1
    assert not os.path.exists(would_create)
    assert not os.path.exists(os.path.dirname(would_create))
=== END AC config-postgres-refused ===

=== AC config-open-ledger ===
Intent: open_ledger returns a database exposing the declared tables that can be read.

from ledgerlib.config import open_ledger

db = open_ledger()
rows = db.accounts.list()
assert isinstance(rows, list)
=== END AC config-open-ledger ===

=== AC config-invalid-database-file ===
Intent: An existing file that is not a valid database makes open_ledger fail with exit code 1 and print nothing.

import contextlib
import io
import os
import tempfile

from cli.errors import OperationalError
from ledgerlib.config import open_ledger

with tempfile.TemporaryDirectory() as tmp:
    bogus = os.path.join(tmp, "not_a_database.db")
    with open(bogus, "wb") as handle:
        handle.write(b"x" * 4096)
    out = io.StringIO()
    raised = None
    with contextlib.redirect_stdout(out):
        try:
            db = open_ledger({"DATABASE_URL": bogus})
            db.accounts.list()
        except OperationalError as exc:
            raised = exc
    assert raised is not None
    assert raised.exit_code == 1
    assert out.getvalue() == ""
=== END AC config-invalid-database-file ===

## User Acceptance

- None.

## Guardrails

- No database driver is imported outside the `persistence` package.
- A PostgreSQL DSN never causes a file or directory to be created.
- Nothing is written to standard output on failure.
