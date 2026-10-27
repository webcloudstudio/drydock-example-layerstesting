# FEATURE: Account Delete

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger account delete <code>`, removing an account that has no transactions. |
| Depends On | FEATURE-AccountAdd.md, FEATURE-CliEntry.md, DATABASE.md |
| Provides | ledger account delete |
| Consumes | ledger_core.accounts, cli.registry |

## Purpose

`ledger account delete <code>` removes an account and prints `deleted` then the code, one per line. An account that still has transactions is refused.

## Behavior

- Exactly one argument is required; otherwise exit 2.
- An absent code exits 4.
- An account with at least one transaction exits 3 and stays stored.
- Otherwise the account is deleted and the command exits 0.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: check the account exists - supplies: `account` - returns: `account`
- `FEATURE-TXN-005` — read: check the account has transactions - supplies: `account` - returns: `txn_id`
- `FEATURE-ACCOUNT-004` — write: delete the account - supplies: `account` - returns: `account`

## Programmatic Acceptance

=== AC account-delete-success ===
Intent: Deleting an account without transactions prints the confirmation and a later read finds nothing.
Requires: executable=python3; scope=test

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

code = "ZZAD1"
with db_session() as db:
    db.accounts.create(account=code, name="Delete Probe")
    rc, out, err = cli_runner("account", "delete", code)
    print(out)
    print(err)
    assert rc == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows == [["deleted"], [code]]
    assert db.accounts.get(account=code) is None
=== END AC account-delete-success ===

=== AC account-delete-in-use ===
Intent: An account with a transaction is refused with exit 3 and both the account and the transaction remain.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

code, cat, tid = "ZZAD2", "ZZADC2", 900001201
with db_session() as db:
    db.accounts.create(account=code, name="In Use")
    db.categories.create(category=cat, description="Delete Category")
    db.transactions.create(txn_id=tid, date="2026-04-01", account=code, category=cat, amount=500, memo="")
    rc, out, err = cli_runner("account", "delete", code)
    print(err)
    assert rc == 3
    assert out == ""
    assert db.accounts.get(account=code) is not None
    assert db.transactions.get(txn_id=tid) is not None
=== END AC account-delete-in-use ===

=== AC account-delete-absent ===
Intent: Deleting an absent account exits 4 with no standard output.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

code = "ZZADNONE"
with db_session() as db:
    assert db.accounts.get(account=code) is None
    rc, out, err = cli_runner("account", "delete", code)
    print(err)
    assert rc == 4
    assert out == ""
=== END AC account-delete-absent ===

=== AC account-delete-usage ===
Intent: A missing argument is a usage error with exit 2 and no standard output.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    rc, out, err = cli_runner("account", "delete")
    assert rc == 2
    assert out == ""
=== END AC account-delete-usage ===

## User Acceptance

- None.

## Guardrails

- Existence and in-use checks both complete before the delete is issued.
- A refused or failed delete leaves every stored record unchanged.
- Failures write nothing to standard output.
