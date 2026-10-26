# FEATURE: Ledger Init

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Implement `ledger init` to prepare an empty ledger and remove all rows when rerun. |
| Depends On | FEATURE-CliFoundation.md, FEATURE-ErrorContract.md, DATABASE.md |
| Provides | ledger init |
| Consumes | ledger.register_command, ledger_config.database_dsn, persistence.open_database, ledger_errors.OperationalFailure |

## Purpose

`ledger init` leaves the ledger empty and ready for loading. The tables are created by the
DATABASE step; `init` only removes rows and never issues DDL.

## Rules

- Register `init` through `ledger.register_command`; it takes no arguments.
- In one database transaction delete every transaction, then every category, then every account (`db.transactions.delete_all()`, `db.categories.delete_all()`, `db.accounts.delete_all()`), so foreign keys hold at each step.
- Write nothing to standard output. Exit 0.
- Rerunning on an empty or populated ledger always succeeds and leaves zero rows in all three tables.
- The database is resolved by `DATABASE_URL` (an empty value counts as unset), then `DATABASE_PATH` (used only when `DATABASE_URL` is unset), then `data/app.db`.
- An unreachable database or missing tables raises `OperationalFailure` (exit 1). The diagnostic never contains the DSN, a path credential or a password.

## Database Interface

- `FEATURE-TXN-006` — write: delete every transaction - supplies: none - returns: none
- `FEATURE-CATEGORY-006` — write: delete every category - supplies: none - returns: none
- `FEATURE-ACCOUNT-006` — write: delete every account - supplies: none - returns: none

## Programmatic Acceptance

=== AC init-removes-all-rows ===
Intent: init exits 0, writes nothing to stdout, and removes every row from all three tables.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQINIT1"
cat = "ZQINITC1"
with db_session() as db:
    db.accounts.create(account=acct, name="Init Account")
    db.categories.create(category=cat, description="Init Category")
    db.transactions.create(
        txn_id=920001, date="2026-04-01", account=acct, category=cat, amount=100, memo=""
    )
    code, out, err = cli_runner("init")
    print(err)
    assert code == 0
    assert out == ""
    assert db.transactions.list() == []
    assert db.categories.list() == []
    assert db.accounts.list() == []
=== END AC init-removes-all-rows ===

=== AC init-rerun ===
Intent: Rerunning init on an already empty ledger succeeds and stays empty.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    for _ in range(2):
        code, out, err = cli_runner("init")
        print(err)
        assert code == 0
        assert out == ""
    assert db.accounts.list() == []
    assert db.categories.list() == []
    assert db.transactions.list() == []
=== END AC init-rerun ===

=== AC init-wrong-argument-count ===
Intent: init with an extra argument is a usage error that removes nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQINIT2"
with db_session() as db:
    db.accounts.create(account=acct, name="Init Keep")
    code, out, err = cli_runner("init", "extra")
    assert code == 2
    assert db.accounts.get(account=acct) is not None
=== END AC init-wrong-argument-count ===

## User Acceptance

- None.

## Guardrails

- `init` never issues DDL and never drops tables.
- A failure never writes the database URL, path credential or DSN password to standard output or standard error.
