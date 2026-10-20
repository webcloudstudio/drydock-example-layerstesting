# Feature: Transaction Delete

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Delete one transaction by id, applying the non-negative balance rule after the delete. |
| Depends On  | DATABASE.md, FEATURE-Balance-Rule.md, FEATURE-Command-Transaction.md, FEATURE-CLI-Output.md, FEATURE-CLI-Dispatch.md |
| Provides    | ledger txn delete <id> |
| Consumes    | transactions.get, transactions.delete |

## Purpose

`ledger txn delete <id>` removes one transaction. On success it prints `deleted` and the id. An
absent id exits 4. A delete that leaves any account below zero exits 3. Every rejected delete
changes nothing.

## Trigger

The user runs `ledger txn delete <id>`.

## Behavior

1. Parse `<id>` as an integer. A non-integer id exits 3 before any lookup.
2. Within the command transaction, fetch the row by `txn_id` through `transactions.get`. An absent
   id exits 4.
3. Remove the row through `transactions.delete`.
4. Apply the balance rule to the account the removed row touched (FEATURE-Balance-Rule.md). A
   negative balance exits 3 and rolls back the delete.
5. Commit and print:

```text
deleted
<id>
```

## Routes and Interfaces

| Interface | Kind | Notes |
|---|---|---|
| `ledger txn delete <id>` | CLI command | Exit 0 on success, 3 on rejection, 4 when absent. |

## Reads and Writes

| Operation | Access | Repository operation | Notes |
|---|---|---|---|
| Fetch transaction | read | `transactions.get` | Absent id maps to exit 4. |
| Delete transaction | write | `transactions.delete` | Runs inside the command transaction. |

## Programmatic Acceptance

=== AC txn-delete-removes-row ===
Intent: Deleting an existing transaction removes it so a subsequent get reports absence.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="TDA1", name="Delete Test A")
    db.categories.create(category="TDC1", description="Delete Test C")
    row = db.transactions.create(txn_id=9001, date="2026-05-01", account="TDA1",
                                 category="TDC1", amount=500, memo="to delete")
    code, out, err = cli_runner("txn", "delete", "9001")
    assert code == 0
    code2, out2, err2 = cli_runner("txn", "get", "9001")
    assert code2 == 4
=== END AC txn-delete-removes-row ===

=== AC txn-delete-output ===
Intent: A successful delete prints exactly the header-free output `deleted` then the id.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="TDA2", name="Delete Test B")
    db.categories.create(category="TDC2", description="Delete Test D")
    db.transactions.create(txn_id=9002, date="2026-05-01", account="TDA2",
                           category="TDC2", amount=700, memo="output check")
    code, out, err = cli_runner("txn", "delete", "9002")
    assert code == 0
    assert out.splitlines()[0] == "deleted"
    assert out.splitlines()[1] == "9002"
=== END AC txn-delete-output ===

=== AC txn-delete-absent-id ===
Intent: Deleting an absent id exits 4 and changes nothing.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code, out, err = cli_runner("txn", "delete", "999999")
    assert code == 4
    assert out == ""
=== END AC txn-delete-absent-id ===

=== AC txn-delete-non-integer-id ===
Intent: A non-integer id exits 3 before any lookup.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code, out, err = cli_runner("txn", "delete", "abc")
    assert code == 3
    assert out == ""
=== END AC txn-delete-non-integer-id ===

=== AC txn-delete-balance-rejection ===
Intent: A delete that would leave an account below zero exits 3 and leaves the row in place.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="TDA3", name="Delete Test E")
    db.categories.create(category="TDC3", description="Delete Test F")
    db.transactions.create(txn_id=9003, date="2026-05-01", account="TDA3",
                           category="TDC3", amount=1000, memo="receipt")
    db.transactions.create(txn_id=9004, date="2026-05-02", account="TDA3",
                           category="TDC3", amount=-400, memo="payment")
    code, out, err = cli_runner("txn", "delete", "9003")
    assert code == 3
    assert db.transactions.get(txn_id=9003).amount == 1000
=== END AC txn-delete-balance-rejection ===

## User Acceptance

- None.

## Guardrails

- A rejected delete changes no row and prints nothing to standard output.
- Balance is computed from the database after the delete, never from a cached value.
- Absent-id and non-integer-id checks run before any write.
