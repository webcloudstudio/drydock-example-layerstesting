# FEATURE: Init

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | The `ledger init` command that returns the three ledger tables to an empty state. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-CliEntry.md, FEATURE-LedgerCore.md |
| Provides | ledger init |
| Consumes | cli.registry.register, cli.context.open_store |

## Purpose

`ledger init` drops all three tables if present and recreates them empty, writing nothing to standard output. It takes no arguments; any argument is a usage error (exit 2) and changes nothing. This is the contract surfaced in the commands table of the source instructions.

## Behavior

1. Open the store with `cli.context.open_store()`.
2. Make sure the three tables exist. If opening a store that has no tables does not already create them, apply the generated idempotent `schema.sql` through the persistence library's own facility. Application code never executes driver calls itself. The grader runs `ledger init` against a brand-new database file, so this step must work on an empty store.
3. Empty the tables in foreign-key order with the declared clear operations: transactions first, then accounts, then categories.
4. Return `None` so standard output stays empty; exit 0.
5. An unreachable database exits 1.

The registration is `register(("init",), handler, (0, 0))` in `cli/commands/init.py`.

## Database Interface


- `FEATURE-ACCOUNT-006` — write: accounts.clear - supplies: `first_code` - returns: —
- `FEATURE-CATEGORY-004` — write: categories.clear - supplies: `first_code` - returns: —
- `FEATURE-TXN-006` — write: transactions.clear - supplies: `min_id` - returns: —

## Programmatic Acceptance

=== AC init-empties-tables ===
Intent: ledger init exits 0, prints nothing, and leaves all three tables empty even when transactions reference accounts and categories.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    acct = "ACPTIN1"
    cat = "ACPTINC1"
    db.accounts.create(account=acct, name="Init Account")
    db.categories.create(category=cat, description="Init Category")
    new_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(
        txn_id=new_id, date="2026-06-01", account=acct, category=cat, amount=500, memo=""
    )
    code, out, err = cli_runner("init")
    print(out, err)
    assert code == 0
    assert out == ""
    assert db.transactions.list() == []
    assert db.accounts.list() == []
    assert db.categories.list() == []
=== END AC init-empties-tables ===

=== AC init-repeatable ===
Intent: Running ledger init twice in a row succeeds both times.

from cli.testing import cli_runner

first = cli_runner("init")
second = cli_runner("init")
assert first[0] == 0
assert second[0] == 0
assert second[1] == ""
=== END AC init-repeatable ===

=== AC init-usage-error ===
Intent: ledger init with an extra argument is exit 2 and removes nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    acct = "ACPTIN2"
    db.accounts.create(account=acct, name="Keep Me")
    code, out, err = cli_runner("init", "extra")
    assert code == 2
    assert out == ""
    assert db.accounts.get(account=acct) is not None
=== END AC init-usage-error ===

## User Acceptance

- None.

## Guardrails

- `init` writes nothing to standard output.
- `init` never opens a database driver directly.
- A rejected `init` (usage error) changes nothing.
