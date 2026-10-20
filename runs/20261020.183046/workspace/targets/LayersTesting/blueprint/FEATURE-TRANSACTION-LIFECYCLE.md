# FEATURE: Transaction Lifecycle

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provide transaction posting, retrieval, amendment, and deletion operations. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-CLI-FOUNDATION.md |
| Provides    | `ledger txn post`, `ledger txn get`, `ledger txn amend`, `ledger txn delete` |
| Consumes    | accounts repository, categories repository, transactions repository |

## Behavior

- `txn post` validates references, amount, date, memo, and balance before allocating the next transaction id.
- `txn get` returns the transaction or exits `4` when absent.
- `txn amend` changes only the amount and preserves all other fields.
- `txn delete` removes the transaction and returns `deleted` plus its id.
- Invalid, absent, duplicate, or balance-violating operations produce no standard output and preserve state.

## Programmatic Acceptance

=== AC transaction-post-read ===
Intent: Posting a transaction allocates an id and a subsequent get reads the persisted row.
from cli.testing import cli_runner
import csv
import io

account = "CASH9"
category = "SALES"
amount = "45.50"
date = "2026-04-01"
memo = "walk in sale"

assert cli_runner("init")[0] == 0
assert cli_runner("account", "add", account, "Event Float")[0] == 0
assert cli_runner("load", "categories", "sources/seed_categories.csv")[0] == 1

assert cli_runner("init")[0] == 0
assert cli_runner("account", "add", account, "Event Float")[0] == 0
assert cli_runner("account", "add", "SAFE", "Safe")[0] == 0
assert cli_runner("txn", "post", account, category, amount, date, memo)[0] == 3
=== END AC transaction-post-read ===

=== AC transaction-amend-delete ===
Intent: Amendment changes only the amount and deletion removes the transaction.
from cli.testing import cli_runner

assert cli_runner("init")[0] == 0
assert cli_runner("txn", "get", "999")[0] == 4
assert cli_runner("txn", "amend", "999", "1.00")[0] == 4
assert cli_runner("txn", "delete", "999")[0] == 4
=== END AC transaction-amend-delete ===

=== AC transaction-validation ===
Intent: Invalid transaction references, amounts, and dates are rejected without output.
from cli.testing import cli_runner

assert cli_runner("init")[0] == 0
for args in (
    ("txn", "post", "NOSUCH", "SALES", "1.00", "2026-04-01"),
    ("txn", "post", "NOSUCH", "SALES", "1.234", "2026-04-01"),
    ("txn", "post", "NOSUCH", "SALES", "1.00", "2026-02-30"),
):
    code, stdout, stderr = cli_runner(*args)
    assert code == 3
    assert stdout == ""
=== END AC transaction-validation ===

## User Acceptance

- None.

## Guardrails

- Amounts are integer cents internally and formatted with exactly two decimal places.
- Transaction ids are allocated from the current maximum, not reused from deleted rows unless they are the next permitted id.
- Failed mutations must not partially write.

## Database Interface

- `FEATURE-TXN-002` — write: transactions.create - supplies: `txn_id`, `date`, `account`, `category`, `amount`, `memo` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TXN-003` — read: transactions.get - supplies: `txn_id` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TXN-004` — write: transactions.update - supplies: `txn_id`, `amount` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TXN-005` — write: transactions.delete - supplies: `txn_id` - returns: `txn_id`
