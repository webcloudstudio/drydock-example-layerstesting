# FEATURE: Init

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implement `ledger init`, which prepares an empty ledger and removes existing rows when rerun. |
| Depends On | FEATURE-DatabaseSelection.md, DATABASE.md |
| Provides | ledger init |
| Consumes | ledgerlib.config, persistence |

## Purpose

`ledger init` makes the configured database ready and empty. It creates the parent directory of the SQLite file when missing, opens the database through `open_database` (which provisions the declared tables idempotently), then removes every row, children first: transactions, then categories, then accounts. It writes nothing to standard output and exits 0.

## Behavior

- `cli/commands/init.py` exposes `run(args) -> list[str]` and returns no lines.
- Any argument is a usage error (exit 2).
- A PostgreSQL DSN or unreachable database exits 1 with nothing on standard output.
- Clearing uses the declared `clear` operations with the lowest possible bound (`min_txn_id` of a value below every id, empty-string bounds for codes). No driver import and no DDL outside the persistence library.
- Rerunning on a populated ledger removes every row, leaving all three tables empty.
- Creating a missing parent directory is covered by the project's own pytest suite, which owns temporary database locations.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC init-clears-rows ===
Intent: Init exits 0 with empty standard output and leaves every table empty after rows were seeded through the persistence interface.

from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZZINI1"
cat = "ZZINCAT1"
with db_session() as db:
    db.accounts.create(account=acct, name="Init Seed")
    db.categories.create(category=cat, description="Init Seed Cat")
    db.transactions.create(txn_id=960001, date="2026-05-01", account=acct, category=cat, amount=100, memo="s")
    assert len(db.transactions.list()) >= 1

    code, out, err = cli_runner("init")
    print(out)
    print(err)
    assert code == 0
    assert out == ""

    assert db.transactions.list() == []
    assert db.categories.list() == []
    assert db.accounts.list() == []
    assert db.accounts.get(account=acct) is None
=== END AC init-clears-rows ===

=== AC init-rerun ===
Intent: Running init again on an already empty ledger still succeeds with no output and the tables stay empty.

from persistence.testing import db_session
from cli.testing import cli_runner

code1, out1, err1 = cli_runner("init")
code2, out2, err2 = cli_runner("init")
print(err1)
print(err2)
assert code1 == 0
assert code2 == 0
assert out1 == ""
assert out2 == ""
with db_session() as db:
    assert db.accounts.list() == []
    assert db.categories.list() == []
    assert db.transactions.list() == []
=== END AC init-rerun ===

=== AC init-usage ===
Intent: Init rejects an unexpected argument as a usage error with exit 2, empty standard output and a diagnostic on standard error.

from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZZINU1"
with db_session() as db:
    db.accounts.create(account=acct, name="Init Usage")
    code, out, err = cli_runner("init", "extra")
    assert code == 2
    assert out == ""
    assert err != ""
    assert db.accounts.get(account=acct) is not None
=== END AC init-usage ===

## User Acceptance

- None.

## Guardrails

- Init never imports a database driver and never runs DDL itself.
- Init writes nothing to standard output.
