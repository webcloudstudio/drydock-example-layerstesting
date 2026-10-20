# FEATURE: Account Delete

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Delete an account that has no transactions and print the deleted code. |
| Depends On  | DATABASE.md, FEATURE-CLI-Dispatch.md, FEATURE-CLI-Output.md, FEATURE-Code-Validation.md, FEATURE-Command-Transaction.md |
| Provides    | ledger account delete <code> |
| Consumes    | accounts.get, accounts.delete, transactions.list |

## Purpose

`ledger account delete <code>` removes an account. The delete is refused while any transaction
references the account.

## Behavior

- The command runs inside one command transaction (FEATURE-Command-Transaction.md).
- The `<code>` argument is validated as an account code (FEATURE-Code-Validation.md) before any lookup.
- The account is looked up with `accounts.get`. An absent code exits 4 with no change.
- If any transaction references the account, the command exits 3 with no change.
- Otherwise the account is removed with `accounts.delete` and the output is:

  ```text
  deleted
  <code>
  ```

## Routes and Interfaces

| Command | Exit 0 | Exit 3 | Exit 4 |
|---|---|---|---|
| `ledger account delete <code>` | `deleted`, code | account in use | absent code |

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC account-delete-unused-succeeds ===
Intent: Deleting an account with no transactions prints deleted and the code, and the row is gone.
Suite: scoped

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.accounts.create(account="CASH9", name="Event Float")
    code, out, _ = cli_runner("account", "delete", "CASH9")
    row = db.accounts.get(account="CASH9")

assert code == 0
assert out == "deleted\nCASH9\n"
assert row is None
=== END AC account-delete-unused-succeeds ===

=== AC account-delete-in-use-exits-3 ===
Intent: Deleting an account referenced by a transaction exits 3 and leaves the account in place.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.accounts.create(account="CASH9", name="Event Float")
    db.categories.create(category="SALES", description="Sales receipts")
    db.transactions.create(txn_id=1, date="2026-01-01", account="CASH9", category="SALES", amount=100, memo="")
    code, out, _ = cli_runner("account", "delete", "CASH9")
    row = db.accounts.get(account="CASH9")

assert code == 3
assert out == ""
assert row.name == "Event Float"
=== END AC account-delete-in-use-exits-3 ===

=== AC account-delete-absent-exits-4 ===
Intent: Deleting an absent account exits 4 and writes nothing to stdout.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    code, out, _ = cli_runner("account", "delete", "NOSUCH")

assert code == 4
assert out == ""
=== END AC account-delete-absent-exits-4 ===

## User Acceptance

- None.

## Guardrails

- The in-use check is computed by query over transactions, never by a stored count.
- Application code reaches the database only through `persistence` operations.
