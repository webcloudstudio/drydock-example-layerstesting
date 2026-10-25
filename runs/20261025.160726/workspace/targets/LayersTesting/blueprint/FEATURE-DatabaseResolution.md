# FEATURE: Database Resolution

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Resolve the database from DATABASE_URL, then DATABASE_PATH, then data/app.db, selecting PostgreSQL or SQLite by prefix. |
| Depends On | FEATURE-Init.md, FEATURE-Count.md, FEATURE-CliEntry.md, DATABASE.md |
| Provides | database resolution, cli.database.resolve_database_dsn, cli.database.database_engine |
| Consumes | cli.main, ledger count, ledger txn post |

## Purpose

Every command opens the store through the shipped persistence library using one DSN chosen by a
single pure resolver. No driver is opened anywhere else and amounts stay integer cents.

## Interface

Module `cli/database.py`:

- `resolve_database_dsn(environ: Mapping[str, str]) -> str` returns `environ["DATABASE_URL"]` when
  set and non-empty, else `environ["DATABASE_PATH"]` when set and non-empty, else `data/app.db`.
  The value is returned unchanged and handed to `persistence.open_database`.
- `database_engine(dsn: str) -> str` returns `postgres` for a value beginning `postgres://` or
  `postgresql://`, and `sqlite` for anything else, including a `sqlite://` prefixed value.
- The command layer calls `resolve_database_dsn(os.environ)` once per invocation. A missing
  directory, unreachable server, or missing tables is exit `1`.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: list accounts to confirm the resolved store is reachable - supplies: `account` - returns: `account`, `name`

## Programmatic Acceptance

=== AC dsn-url-wins ===
Intent: DATABASE_URL takes precedence over DATABASE_PATH.

from cli.database import resolve_database_dsn

url = "postgres://user@host/ledger"
path = "other/place.db"
assert resolve_database_dsn({"DATABASE_URL": url, "DATABASE_PATH": path}) == url
assert resolve_database_dsn({"DATABASE_URL": url}) == url
=== END AC dsn-url-wins ===

=== AC dsn-path-fallback ===
Intent: With DATABASE_URL unset, DATABASE_PATH is used.

from cli.database import resolve_database_dsn

path = "other/place.db"
assert resolve_database_dsn({"DATABASE_PATH": path}) == path
=== END AC dsn-path-fallback ===

=== AC dsn-default ===
Intent: With neither variable set, the resolver returns data/app.db.

from cli.database import resolve_database_dsn

assert resolve_database_dsn({}) == "data/app.db"
=== END AC dsn-default ===

=== AC dsn-engine-selection ===
Intent: postgres:// and postgresql:// select PostgreSQL; other values, with or without sqlite://, select SQLite.

from cli.database import database_engine

for dsn in ("postgres://u@h/db", "postgresql://u@h/db"):
    assert database_engine(dsn) == "postgres", dsn
for dsn in ("data/app.db", "sqlite:///tmp/x.db", "/abs/path/ledger.db"):
    assert database_engine(dsn) == "sqlite", dsn
=== END AC dsn-engine-selection ===

=== AC dsn-configured-store-is-used ===
Intent: The count command runs against the configured store and lists the three tables in order.

import csv
import io
from cli.testing import cli_runner

code, out, err = cli_runner("count")
print(out)
print(err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["table", "rows"]
assert [r[0] for r in rows[1:]] == ["accounts", "categories", "transactions"]
assert all(r[1].isdigit() for r in rows[1:])
=== END AC dsn-configured-store-is-used ===

=== AC dsn-amounts-stored-as-integer-cents ===
Intent: A posted amount is stored as an integer number of cents.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "DSNC1"
cat = "DSNCC1"
cents = 1234
amount_text = f"{cents // 100}.{cents % 100:02d}"
with db_session() as db:
    db.accounts.create(account=acct, name="Cents Account")
    db.categories.create(category=cat, description="Cents Category")
    code, out, err = cli_runner("txn", "post", acct, cat, amount_text, "2026-06-02", "cents")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    stored = db.transactions.get(txn_id=int(rows[1][0]))
    assert stored is not None
    assert isinstance(stored.amount, int)
    assert stored.amount == cents
=== END AC dsn-amounts-stored-as-integer-cents ===

## User Acceptance

- None.

## Guardrails

- No database driver is imported outside the shipped persistence library.
- The resolver reads only the environment mapping it is given and never a file.
- No floating-point type holds money at any layer.
