# FEATURE: Transaction Amend

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Change only the amount of one transaction, applying the balance rule and printing the updated row. |
| Depends On  | DATABASE.md, FEATURE-CLI-Dispatch.md, FEATURE-CLI-Output.md, FEATURE-Amount-Format.md, FEATURE-Balance-Rule.md, FEATURE-Command-Transaction.md |
| Provides    | ledger txn amend <id> <amount> |
| Consumes    | transactions.get, transactions.update, transactions.list |

## Purpose

`ledger txn amend <id> <amount>` replaces the amount of an existing transaction. No other field
changes.

## Behavior

- The command runs inside one command transaction (FEATURE-Command-Transaction.md).
- The `<id>` argument must be an integer. A non-integer id exits 3 before any lookup.
- The `<amount>` argument is parsed as integer cents (FEATURE-Amount-Format.md). Zero in any form
  exits 3.
- The transaction is read with `transactions.get`. An absent id exits 4 with no change.
- The amount is written with `transactions.update`. No other column changes.
- The balance rule (FEATURE-Balance-Rule.md) is checked after the update and before commit. A
  resulting negative balance exits 3 with no change.
- On success the updated row is printed as:

  ```text
  txn_id,date,account,category,amount,memo
  <id>,<date>,<account>,<category>,<amount>,<memo>
  ```

## Routes and Interfaces

| Command | Exit 0 | Exit 3 | Exit 4 |
|---|---|---|---|
| `ledger txn amend <id> <amount>` | updated row | malformed id or amount, negative balance | absent id |

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC txn-amend-changes-only-amount ===
Intent: Amending a transaction changes only its amount and prints the updated row.
Suite: scoped

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.accounts.create(account="DRAWER1", name="Front Drawer")
    db.categories.create(category="SALES", description="Sales receipts")
    db.transactions.create(txn_id=121, date="2026-04-01", account="DRAWER1", category="SALES", amount=4550, memo="walk in sale")
    code, out, _ = cli_runner("txn", "amend", "121", "54.50")
    row = db.transactions.get(txn_id=121)

assert code == 0
assert out == "txn_id,date,account,category,amount,memo\n121,2026-04-01,DRAWER1,SALES,54.50,walk in sale\n"
assert row.amount == 5450
assert row.memo == "walk in sale"
assert row.date == "2026-04-01"
=== END AC txn-amend-changes-only-amount ===

=== AC txn-amend-absent-exits-4 ===
Intent: Amending an absent transaction id exits 4 and writes nothing to stdout.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    code, out, _ = cli_runner("txn", "amend", "999", "1.00")

assert code == 4
assert out == ""
=== END AC txn-amend-absent-exits-4 ===

=== AC txn-amend-zero-amount-exits-3 ===
Intent: A zero amount in any form is rejected with exit 3 and the stored amount is unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.accounts.create(account="DRAWER1", name="Front Drawer")
    db.categories.create(category="SALES", description="Sales receipts")
    db.transactions.create(txn_id=121, date="2026-04-01", account="DRAWER1", category="SALES", amount=4550, memo="walk in sale")
    code, out, _ = cli_runner("txn", "amend", "121", "0.00")
    row = db.transactions.get(txn_id=121)

assert code == 3
assert out == ""
assert row.amount == 4550
=== END AC txn-amend-zero-amount-exits-3 ===

=== AC txn-amend-negative-balance-exits-3 ===
Intent: An amendment that would leave an account below zero exits 3 and changes nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.accounts.create(account="PETTY", name="Petty Cash")
    db.categories.create(category="SUPPLY", description="Supplies")
    db.transactions.create(txn_id=1, date="2026-01-01", account="PETTY", category="SUPPLY", amount=-1200, memo="tape")
    code, out, _ = cli_runner("txn", "amend", "1", "-1000.00")
    row = db.transactions.get(txn_id=1)

assert code == 3
assert out == ""
assert row.amount == -1200
=== END AC txn-amend-negative-balance-exits-3 ===

## User Acceptance

- None.

## Guardrails

- Only the amount column changes on amend; account, category, date, and memo are never rewritten.
- Amounts are integer cents end to end; no floating point is used for money.
- Application code reaches the database only through `persistence` operations.
