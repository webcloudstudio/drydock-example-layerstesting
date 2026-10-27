# FEATURE: Account Delete

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger account delete`, which removes an account that has no transactions. |
| Depends On | FEATURE-AccountGet.md, FEATURE-LedgerCli.md, DATABASE.md |
| Provides | ledger account delete |
| Consumes | ledger, accounts, transactions |

## Purpose

Let the shop remove an account created in error, while protecting any account that already carries transaction history.

## Trigger

`ledger account delete <code>` invoked from the command line.

## Sequence

1. Require exactly one argument after `delete`; otherwise raise the shared usage error (exit 2).
2. Look up the account. An absent code exits 4.
3. List the account's transactions. If any exist, exit 3 and remove nothing.
4. Delete the account through the persistence library.
5. Write `deleted` and then the code, one per line.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: look up the account by code - supplies: `account` - returns: `account`
- `FEATURE-ACCOUNT-004` — write: delete the account - supplies: `account` - returns: `account`
- `FEATURE-TXN-005` — read: list the account's transactions to detect use - supplies: `account` - returns: `txn_id`

## Behavior Rules

- An account with at least one transaction is never removed.
- A failing command writes nothing to standard output and one diagnostic line to standard error.

## Programmatic Acceptance

=== AC acct-delete-success ===
Intent: Deleting an unused account exits 0, writes the word deleted then the code, and a separate read finds the account gone.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

code = "ZDL1"
with db_session() as db:
    db.accounts.create(account=code, name="Disposable")
    exit_code, out, err = cli_runner("account", "delete", code)
    print(exit_code, out, err)
    assert exit_code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows == [["deleted"], [code]]
    assert db.accounts.get(account=code) is None
=== END AC acct-delete-success ===

=== AC acct-delete-in-use ===
Intent: An account that has a transaction is refused with exit 3, and both the account and its transaction remain.

from persistence.testing import db_session
from cli.testing import cli_runner

code = "ZDL2"
cat = "ZDL2"
txn_id = 920001
with db_session() as db:
    db.accounts.create(account=code, name="In Use")
    db.categories.create(category=cat, description="Delete Category")
    db.transactions.create(
        txn_id=txn_id, date="2026-05-01", account=code, category=cat, amount=500, memo=""
    )
    exit_code, out, err = cli_runner("account", "delete", code)
    print(exit_code, out, err)
    assert exit_code == 3
    assert out == ""
    assert db.accounts.get(account=code) is not None
    assert db.transactions.get(txn_id=txn_id) is not None
=== END AC acct-delete-in-use ===

=== AC acct-delete-absent ===
Intent: Deleting an account that does not exist exits 4 with nothing on standard output.

from persistence.testing import db_session
from cli.testing import cli_runner

code = "ZDLNONE"
with db_session() as db:
    assert db.accounts.get(account=code) is None
    exit_code, out, err = cli_runner("account", "delete", code)
    print(exit_code, out, err)
    assert exit_code == 4
    assert out == ""
=== END AC acct-delete-absent ===

=== AC acct-delete-leaves-others ===
Intent: Deleting one account removes only that account; a second account created alongside it is still present.

from persistence.testing import db_session
from cli.testing import cli_runner

gone = "ZDL3"
kept = "ZDL4"
kept_name = "Keeper"
with db_session() as db:
    db.accounts.create(account=gone, name="Goner")
    db.accounts.create(account=kept, name=kept_name)
    exit_code, out, err = cli_runner("account", "delete", gone)
    print(exit_code, out, err)
    assert exit_code == 0
    assert db.accounts.get(account=gone) is None
    survivor = db.accounts.get(account=kept)
    assert survivor is not None
    assert survivor.name == kept_name
=== END AC acct-delete-leaves-others ===

## User Acceptance

- None.

## Guardrails

- An account with transactions is never deleted.
- Persistence is reached only through the generated persistence package.
- A rejected delete writes nothing to the database.
