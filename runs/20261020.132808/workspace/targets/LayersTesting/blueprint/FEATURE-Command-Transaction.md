# FEATURE: Command Transaction

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Runs every ledger command inside exactly one database transaction that commits on success and rolls back on failure. |
| Depends On  | FEATURE-Database-Location.md, DATABASE.md |
| Provides    | run_command(db, command) |
| Consumes    | open_database, db.accounts.create, db.accounts.list |

## Purpose

Every command that reads or writes the store runs inside one transaction. A command either completes in full or changes nothing.

## Behavior

- `run_command(db, command)` opens one transaction on `db`, calls `command(db)` once, commits when the call returns, and returns the value the command returned.
- If `command` raises, every write made through `db` during that call is rolled back, and the exception propagates unchanged.
- A persistence error raised while the transaction is open, including a write lock held by another connection, rolls back the same way and propagates. The CLI maps it to exit 1 through FEATURE-Operational-Errors.md.
- The wrapper does not commit or roll back inside a command body. Commands never open their own transaction.

## Programmatic Acceptance

=== AC command-transaction-commits ===
Intent: A command that returns normally has its write persisted and its return value passed back to the caller.

from persistence.testing import db_session
from transaction import run_command

account_code = "TXNA1"
account_name = "Commit Test"

with db_session() as db:
    result = run_command(db, lambda d: d.accounts.create(account=account_code, name=account_name))
    assert result.account == account_code
    matches = [row for row in db.accounts.list() if row.account == account_code]
    assert len(matches) == 1
    assert matches[0].name == account_name
=== END AC command-transaction-commits ===

=== AC command-transaction-rolls-back-all-writes ===
Intent: When a command raises after two writes, neither write persists and the exception reaches the caller.

from persistence.testing import db_session
from transaction import run_command

first_code = "TXNB1"
second_code = "TXNB2"

class Abort(Exception):
    pass

def write_then_fail(d):
    d.accounts.create(account=first_code, name="Rollback First")
    d.accounts.create(account=second_code, name="Rollback Second")
    raise Abort("forced after two writes")

with db_session() as db:
    before = len(db.accounts.list())
    raised = False
    try:
        run_command(db, write_then_fail)
    except Abort:
        raised = True
    assert raised
    after = db.accounts.list()
    assert len(after) == before
    assert all(row.account not in (first_code, second_code) for row in after)
=== END AC command-transaction-rolls-back-all-writes ===

=== AC command-transaction-propagates-exception ===
Intent: The exception raised by a failing command is the same object the caller receives, not a wrapped or swallowed error.

from persistence.testing import db_session
from transaction import run_command

raised_error = RuntimeError("forced by criterion")

def fail(d):
    raise raised_error

with db_session() as db:
    try:
        run_command(db, fail)
    except RuntimeError as caught:
        assert caught is raised_error
    else:
        raise AssertionError("run_command swallowed the command's exception")
=== END AC command-transaction-propagates-exception ===

## User Acceptance

- None.

## Guardrails

- No module begins or commits a transaction outside `run_command`.
- A failed command never leaves a partial write in any table.
- No command body commits its own work.
- Application code reaches the store only through the `persistence` package, never through a database driver.
