# FEATURE: Transaction Get

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Print one transaction row by id, rejecting non-integer ids before lookup. |
| Depends On  | DATABASE.md, FEATURE-CLI-Dispatch.md, FEATURE-CLI-Output.md, FEATURE-Amount-Format.md, FEATURE-Command-Transaction.md |
| Provides    | ledger txn get <id> |
| Consumes    | transactions.get |

## Purpose

`ledger txn get <id>` prints the stored transaction with the given id.

## Behavior

- The command runs inside one command transaction (FEATURE-Command-Transaction.md).
- The `<id>` argument must be a non-integer-free decimal integer. A non-integer id exits 3 before any
  lookup (AC-012).
- The row is read with `transactions.get`. An absent id exits 4.
- On success the row is printed through the CSV output contract as:

  ```text
  txn_id,date,account,category,amount,memo
  <id>,<date>,<account>,<category>,<amount>,<memo>
  ```

  The amount uses the two-decimal output format.

## Routes and Interfaces

| Command | Exit 0 | Exit 3 | Exit 4 |
|---|---|---|---|
| `ledger txn get <id>` | transaction row | non-integer id | absent id |

## Database Interface

- `FEATURE-TXN-002` — read: retrieve a transaction by id - supplies: `txn_id` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC txn-get-prints-row ===
Intent: Getting an existing transaction prints its row with the two-decimal amount.
Suite: scoped

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.accounts.create(account="DRAWER1", name="Front Drawer")
    db.categories.create(category="SALES", description="Sales receipts")
    db.transactions.create(txn_id=121, date="2026-04-01", account="DRAWER1", category="SALES", amount=4550, memo="walk in sale")
    code, out, _ = cli_runner("txn", "get", "121")

assert code == 0
assert out == "txn_id,date,account,category,amount,memo\n121,2026-04-01,DRAWER1,SALES,45.50,walk in sale\n"
=== END AC txn-get-prints-row ===

=== AC txn-get-absent-exits-4 ===
Intent: Getting an absent transaction id exits 4 and writes nothing to stdout.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    code, out, _ = cli_runner("txn", "get", "999")

assert code == 4
assert out == ""
=== END AC txn-get-absent-exits-4 ===

=== AC txn-get-non-integer-exits-3 ===
Intent: A non-integer id argument exits 3 before any lookup (AC-012).

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    code, out, _ = cli_runner("txn", "get", "12a")

assert code == 3
assert out == ""
=== END AC txn-get-non-integer-exits-3 ===

## User Acceptance

- None.

## Guardrails

- The printed row comes from a query; no transaction value is hardcoded.
- Application code reaches the database only through `persistence` operations.
