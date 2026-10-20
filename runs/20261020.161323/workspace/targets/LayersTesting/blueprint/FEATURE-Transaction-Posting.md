# FEATURE: Transaction Posting

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Posts and retrieves individual ledger transactions. |
| Depends On  | DATABASE.md, FEATURE-Accounts.md, FEATURE-Bulk-Transaction-Loading.md, FEATURE-Validation.md |
| Provides    | `ledger txn post`, `ledger txn get` |
| Consumes    | domain validation, relational ledger schema, transaction persistence operations |

## Purpose

Post a new transaction with the next available identifier and retrieve transactions by identifier.

## Workflows

`txn post` validates the account, category, amount, date, memo, and resulting balance before inserting. The identifier is one greater than the current maximum, or `1` when empty. `txn get` returns the persisted transaction or exit code `4` when absent.

## Database Interface

- `FEATURE-LEDGER-005` — write: create a transaction - supplies: `txn_id`, `date`, `account`, `category`, `amount`, `memo` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-LEDGER-006` — read: retrieve transaction - supplies: `txn_id` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC transaction-post-read ===
Intent: A posted transaction is persisted and can be retrieved by its assigned identifier.
from cli.testing import cli_runner

account_code, _, _ = cli_runner("account", "add", "A", "Alpha")
category_code, _, _ = cli_runner("load", "categories", "sources/seed_categories.csv")
assert account_code == 0
assert category_code == 0
post_code, post_stdout, post_stderr = cli_runner(
    "txn", "post", "A", "SALES", "1.25", "2026-01-01", "sale"
)
assert post_code == 0
get_code, get_stdout, get_stderr = cli_runner("txn", "get", "1")
assert get_code == 0
assert "1,2026-01-01,A,SALES,1.25,sale" in get_stdout
=== END AC transaction-post-read ===

=== AC transaction-next-id ===
Intent: A second posted transaction receives the next identifier.
from cli.testing import cli_runner

account_code, _, _ = cli_runner("account", "add", "A", "Alpha")
category_code, _, _ = cli_runner("load", "categories", "sources/seed_categories.csv")
assert account_code == 0
assert category_code == 0
first_code, _, _ = cli_runner("txn", "post", "A", "SALES", "1.00", "2026-01-01")
second_code, second_stdout, second_stderr = cli_runner(
    "txn", "post", "A", "SALES", "2.00", "2026-01-02"
)
assert first_code == 0
assert second_code == 0
assert "2,2026-01-02,A,SALES,2.00," in second_stdout
=== END AC transaction-next-id ===

=== AC transaction-invalid-reference ===
Intent: Posting with an unknown category is rejected without output.
from cli.testing import cli_runner

account_code, _, _ = cli_runner("account", "add", "A", "Alpha")
assert account_code == 0
code, stdout, stderr = cli_runner(
    "txn", "post", "A", "NOSUCH", "1.00", "2026-01-01"
)
assert code == 3
assert stdout == ""
=== END AC transaction-invalid-reference ===

=== AC transaction-invalid-amount ===
Intent: Posting an amount with more than two decimal places is rejected.
from cli.testing import cli_runner

account_code, _, _ = cli_runner("account", "add", "A", "Alpha")
category_code, _, _ = cli_runner("load", "categories", "sources/seed_categories.csv")
assert account_code == 0
assert category_code == 0
code, stdout, stderr = cli_runner(
    "txn", "post", "A", "SALES", "1.234", "2026-01-01"
)
assert code == 3
assert stdout == ""
=== END AC transaction-invalid-amount ===

## User Acceptance

- None.

## Guardrails

- Never use floating-point money arithmetic.
- Validate all inputs before inserting.
- Return only persisted transaction rows.
- Preserve exact two-decimal output formatting.
