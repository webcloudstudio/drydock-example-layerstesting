# FEATURE: Command Transaction

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Run each command as one database transaction that commits on success and rolls back on any failure. |
| Depends On  | FEATURE-CliEntry.md, DATABASE.md, ARCHITECTURE.md |
| Provides    | run_command |

## Purpose

Rule 1 of the cash ledger: every command either completes in full or changes nothing. This feature
provides the one wrapper that every mutating command and every load runs inside.

## Interface

- `cli.transactional.run_command(db, command)` calls `command(store)` inside one database
  transaction, where `store` is the `db` handle. When `command` returns normally, the transaction
  commits and the return value of `command` is returned. When `command` raises, the transaction
  rolls back and the exception is re-raised unchanged.
- Callers inside `command` use the declared operations, for example
  `store.accounts.create(account=..., name=...)`, with keyword arguments named by the Input DTO
  fields in `DATABASE.md`.

## Behavior

- The wrapper adds no locking. Concurrent processes rely on the database's own transaction
  isolation.
- Rollback covers every table written inside the command, not only the last one.

## Programmatic Acceptance

=== AC integ-txn-commit-on-success ===
Intent: run_command commits the writes of a command that returns normally.

from persistence.testing import db_session
from cli.transactional import run_command

code = "CASH1"
name = "Float"
with db_session() as db:
    def succeeding(store):
        store.accounts.create(account=code, name=name)
        return None

    run_command(db, succeeding)
    rows = db.accounts.list()
    assert len(rows) == 1
    assert rows[0].account == code
    assert rows[0].name == name
=== END AC integ-txn-commit-on-success ===

=== AC integ-txn-rollback-single-table ===
Intent: run_command rolls back a write made before the command raises, leaving the table empty.

from persistence.testing import db_session
from cli.transactional import run_command

code = "CASH1"
name = "Float"
with db_session() as db:
    def failing(store):
        store.accounts.create(account=code, name=name)
        raise ValueError("rejected after write")

    raised = False
    try:
        run_command(db, failing)
    except ValueError:
        raised = True
    assert raised
    assert len(db.accounts.list()) == 0
=== END AC integ-txn-rollback-single-table ===

=== AC integ-txn-rollback-multi-table ===
Intent: run_command rolls back writes to two tables when the command raises after both writes.

from persistence.testing import db_session
from cli.transactional import run_command

code = "CASH1"
name = "Float"
category = "OPENING"
description = "Opening balance"
with db_session() as db:
    def failing(store):
        store.accounts.create(account=code, name=name)
        store.categories.create(category=category, description=description)
        raise ValueError("rejected after two writes")

    raised = False
    try:
        run_command(db, failing)
    except ValueError:
        raised = True
    assert raised
    assert len(db.accounts.list()) == 0
    assert len(db.categories.list()) == 0
=== END AC integ-txn-rollback-multi-table ===

## User Acceptance

- None.

## Guardrails

- A command that fails leaves every table exactly as it was before the command started.
- No application-level lock is added around the transaction.
- Database drivers are never opened here; access goes through the persistence handle only.
