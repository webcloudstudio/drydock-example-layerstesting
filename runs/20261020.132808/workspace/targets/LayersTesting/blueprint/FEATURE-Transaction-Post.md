# FEATURE: Transaction Post

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Post a transaction with the next id after validating every field and applying the balance rule. |
| Depends On  | DATABASE.md, FEATURE-CLI-Dispatch.md, FEATURE-CLI-Output.md, FEATURE-Code-Validation.md, FEATURE-Amount-Format.md, FEATURE-Date-Validation.md, FEATURE-Balance-Rule.md, FEATURE-Command-Transaction.md |
| Provides    | ledger txn post <account> <category> <amount> <date> [<memo>], next_txn_id() |
| Consumes    | accounts.get, categories.get, transactions.list, transactions.create |

## Purpose

`ledger txn post` records one transaction against an account and category. It assigns the next
transaction id, validates every field, applies the non-negative balance rule, and prints the new row.

## Behavior

- The command runs inside one command transaction (FEATURE-Command-Transaction.md).
- Argument syntax is validated before any lookup. A malformed amount, date, code, or memo exits 3
  even when the account is absent (AC-010).
- The amount is parsed as integer cents (FEATURE-Amount-Format.md). Zero in any form exits 3.
- The date is validated as a real `YYYY-MM-DD` calendar date (FEATURE-Date-Validation.md).
- The memo is optional, 0 to 60 characters, with no comma or newline. An omitted memo is stored as
  the empty string.
- The account and category are looked up with `accounts.get` and `categories.get`. A missing account
  or category exits 3, not 4 (AC-011).
- `next_txn_id()` returns the largest `txn_id` from `transactions.list` plus one, or `1` when the
  table is empty. Ids are computed by query.
- The balance rule (FEATURE-Balance-Rule.md) is checked after the insert and before commit. A
  resulting negative balance exits 3 with no change.
- On success the row is written with `transactions.create` and printed as:

  ```text
  txn_id,date,account,category,amount,memo
  <id>,<date>,<account>,<category>,<amount>,<memo>
  ```

  The amount uses the two-decimal output format.

## Routes and Interfaces

| Command | Exit 0 | Exit 3 | Exit 4 |
|---|---|---|---|
| `ledger txn post <account> <category> <amount> <date> [<memo>]` | new row | malformed argument, missing account or category, negative balance | not used |

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC txn-post-assigns-next-id ===
Intent: Posting into a populated table assigns the largest txn_id plus one and prints the new row.
Suite: scoped

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.accounts.create(account="DRAWER1", name="Front Drawer")
    db.categories.create(category="SALES", description="Sales receipts")
    db.transactions.create(txn_id=7, date="2026-01-01", account="DRAWER1", category="SALES", amount=500, memo="")
    code, out, _ = cli_runner("txn", "post", "DRAWER1", "SALES", "45.50", "2026-04-01", "walk in sale")
    row = db.transactions.get(txn_id=8)

assert code == 0
assert out == "txn_id,date,account,category,amount,memo\n8,2026-04-01,DRAWER1,SALES,45.50,walk in sale\n"
assert row.amount == 4550
=== END AC txn-post-assigns-next-id ===

=== AC txn-post-empty-table-starts-at-1 ===
Intent: Posting into an empty transactions table assigns txn_id 1.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.accounts.create(account="DRAWER1", name="Front Drawer")
    db.categories.create(category="SALES", description="Sales receipts")
    code, out, _ = cli_runner("txn", "post", "DRAWER1", "SALES", "10.00", "2026-04-01")
    row = db.transactions.get(txn_id=1)

assert code == 0
assert row.account == "DRAWER1"
assert row.amount == 1000
=== END AC txn-post-empty-table-starts-at-1 ===

=== AC txn-post-zero-amount-exits-3 ===
Intent: A zero amount in any form is rejected with exit 3 and stores nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.accounts.create(account="DRAWER1", name="Front Drawer")
    db.categories.create(category="SALES", description="Sales receipts")
    code, out, _ = cli_runner("txn", "post", "DRAWER1", "SALES", "-0.00", "2026-04-01")
    count = db.transactions.list()

assert code == 3
assert out == ""
assert len(count) == 0
=== END AC txn-post-zero-amount-exits-3 ===

=== AC txn-post-malformed-amount-before-lookup ===
Intent: A malformed amount exits 3 even when the account is absent (AC-010).

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    code, out, _ = cli_runner("txn", "post", "NOSUCH", "SALES", "1.234", "2026-04-01")

assert code == 3
assert out == ""
=== END AC txn-post-malformed-amount-before-lookup ===

=== AC txn-post-missing-account-exits-3 ===
Intent: Posting to an account that does not exist exits 3, not 4 (AC-011).

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.categories.create(category="SALES", description="Sales receipts")
    code, out, _ = cli_runner("txn", "post", "NOSUCH", "SALES", "1.00", "2026-04-01")

assert code == 3
assert out == ""
=== END AC txn-post-missing-account-exits-3 ===

=== AC txn-post-invalid-date-exits-3 ===
Intent: An impossible calendar date is rejected with exit 3.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.accounts.create(account="DRAWER1", name="Front Drawer")
    db.categories.create(category="SALES", description="Sales receipts")
    code, out, _ = cli_runner("txn", "post", "DRAWER1", "SALES", "1.00", "2026-02-30")

assert code == 3
assert out == ""
=== END AC txn-post-invalid-date-exits-3 ===

=== AC txn-post-negative-balance-exits-3 ===
Intent: A post that would leave an account below zero exits 3 and stores nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.accounts.create(account="PETTY", name="Petty Cash")
    db.categories.create(category="SUPPLY", description="Supplies")
    code, out, _ = cli_runner("txn", "post", "PETTY", "SUPPLY", "-1000.00", "2026-04-04")
    count = db.transactions.list()

assert code == 3
assert out == ""
assert len(count) == 0
=== END AC txn-post-negative-balance-exits-3 ===

## User Acceptance

- None.

## Guardrails

- The next id, balances, and printed values are computed by query; no value is hardcoded.
- Amounts are integer cents end to end; no floating point is used for money.
- Application code reaches the database only through `persistence` operations.
