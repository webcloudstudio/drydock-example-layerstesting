# FEATURE: Init

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | The ledger init command resets the ledger to empty and writes nothing to standard output. |
| Depends On | FEATURE-CliFoundation.md, DATABASE.md |
| Provides | ledger init |
| Consumes | transactions.list, transactions.delete, categories.list, categories.delete, accounts.list, accounts.delete |

## Purpose

`ledger init` prepares an empty ledger for loading and use and removes existing ledger records when
rerun. The schema is provisioned by the DATABASE step, so init issues no DDL (decision Q-001).

## Behavior

- Takes no arguments; any argument is a usage error (exit 2).
- Deletes all transactions first, then all categories, then all accounts, through the declared
  repository operations, so foreign keys are never violated.
- Writes nothing to standard output and exits 0. Rerunning leaves an empty ledger.

## Database Interface

- `FEATURE-TRANSACTIONS-003` — read: list transactions to remove - supplies: `account` - returns: `txn_id`
- `FEATURE-TRANSACTIONS-005` — write: delete each transaction - supplies: `txn_id` - returns: `txn_id`
- `FEATURE-CATEGORIES-003` — read: list categories to remove - supplies: `category` - returns: `category`
- `FEATURE-CATEGORIES-004` — write: delete each category - supplies: `category` - returns: `category`
- `FEATURE-ACCOUNTS-003` — read: list accounts to remove - supplies: `account` - returns: `account`
- `FEATURE-ACCOUNTS-005` — write: delete each account - supplies: `account` - returns: `account`

## Programmatic Acceptance

=== AC init-empties-ledger ===
Intent: Init removes every account, category, and transaction and exits 0 with no standard output.

from persistence.testing import db_session
from cli.testing import cli_runner

acct = "UTINI1"
cat = "UTINIC1"
with db_session() as db:
    db.accounts.create(account=acct, name="Init Probe")
    db.categories.create(category=cat, description="Init Category")
    db.transactions.create(
        txn_id=970001, date="2026-04-01", account=acct, category=cat, amount=500, memo="x"
    )
    code, out, err = cli_runner("init")
    print(err)
    assert code == 0
    assert out == ""
    assert db.transactions.list() == []
    assert db.categories.list() == []
    assert db.accounts.list() == []
=== END AC init-empties-ledger ===

=== AC init-rerun ===
Intent: Rerunning init on an already empty ledger still exits 0 and leaves it empty.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    first = cli_runner("init")
    second = cli_runner("init")
    assert first[0] == 0
    assert second[0] == 0
    assert second[1] == ""
    assert db.accounts.list() == []
    assert db.categories.list() == []
    assert db.transactions.list() == []
=== END AC init-rerun ===

=== AC init-argument-usage ===
Intent: Init with an extra argument is a usage error that changes nothing.

from persistence.testing import db_session
from cli.testing import cli_runner

acct = "UTINI2"
with db_session() as db:
    db.accounts.create(account=acct, name="Kept")
    code, out, err = cli_runner("init", "extra")
    print(err)
    assert code == 2
    assert out == ""
    assert db.accounts.get(account=acct) is not None
=== END AC init-argument-usage ===

## User Acceptance

- None.

## Guardrails

- Init issues no DDL, drops no table, and does not alter the schema.
- Init writes nothing to standard output.
