# FEATURE: Transaction Mutation

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Amends and deletes transactions while preserving ledger invariants. |
| Depends On  | DATABASE.md, FEATURE-Transaction-Posting.md, FEATURE-Validation.md |
| Provides    | `ledger txn amend`, `ledger txn delete` |
| Consumes    | domain validation, relational ledger schema, transaction persistence operations |

## Purpose

Change or remove transactions only after validating existence and the resulting account balances.

## Workflows

`txn amend` changes only the amount and returns the complete updated row. `txn delete` removes an existing transaction and returns the deletion result. Missing identifiers return `4`; rejected changes return `3`.

## Database Interface

- `FEATURE-LEDGER-007` — write: update a transaction amount - supplies: `txn_id`, `amount` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-LEDGER-008` — write: delete a transaction - supplies: `txn_id` - returns: `deleted`

## Programmatic Acceptance

=== AC transaction-amend-readback ===
Intent: Amending a transaction changes its amount while preserving its other fields.
from cli.testing import cli_runner

account_code, _, _ = cli_runner("account", "add", "A", "Alpha")
category_code, _, _ = cli_runner("load", "categories", "sources/seed_categories.csv")
assert account_code == 0
assert category_code == 0
post_code, _, _ = cli_runner("txn", "post", "A", "SALES", "1.00", "2026-01-01", "sale")
assert post_code == 0
amend_code, amend_stdout, amend_stderr = cli_runner("txn", "amend", "1", "2.50")
assert amend_code == 0
get_code, get_stdout, get_stderr = cli_runner("txn", "get", "1")
assert get_code == 0
assert "1,2026-01-01,A,SALES,2.50,sale" in get_stdout
=== END AC transaction-amend-readback ===

=== AC transaction-delete-readback ===
Intent: Deleting a transaction removes it from the public transaction interface.
from cli.testing import cli_runner

account_code, _, _ = cli_runner("account", "add", "A", "Alpha")
category_code, _, _ = cli_runner("load", "categories", "sources/seed_categories.csv")
assert account_code == 0
assert category_code == 0
post_code, _, _ = cli_runner("txn", "post", "A", "SALES", "1.00", "2026-01-01")
assert post_code == 0
delete_code, delete_stdout, delete_stderr = cli_runner("txn", "delete", "1")
assert delete_code == 0
get_code, get_stdout, get_stderr = cli_runner("txn", "get", "1")
assert get_code == 4
assert get_stdout == ""
=== END AC transaction-delete-readback ===

=== AC transaction-amend-negative-balance ===
Intent: An amendment that would make an account negative is rejected without changing the transaction.
from cli.testing import cli_runner

account_code, _, _ = cli_runner("account", "add", "A", "Alpha")
category_code, _, _ = cli_runner("load", "categories", "sources/seed_categories.csv")
assert account_code == 0
assert category_code == 0
post_code, _, _ = cli_runner("txn", "post", "A", "SALES", "1.00", "2026-01-01")
assert post_code == 0
amend_code, amend_stdout, amend_stderr = cli_runner("txn", "amend", "1", "-2.00")
assert amend_code == 3
assert amend_stdout == ""
get_code, get_stdout, get_stderr = cli_runner("txn", "get", "1")
assert get_code == 0
assert "1,2026-01-01,A,SALES,1.00," in get_stdout
=== END AC transaction-amend-negative-balance ===

=== AC transaction-missing-id ===
Intent: Amending or deleting an absent transaction returns the not-found exit code.
from cli.testing import cli_runner

amend_code, amend_stdout, amend_stderr = cli_runner("txn", "amend", "999", "1.00")
delete_code, delete_stdout, delete_stderr = cli_runner("txn", "delete", "999")
assert amend_code == 4
assert delete_code == 4
assert amend_stdout == ""
assert delete_stdout == ""
=== END AC transaction-missing-id ===

## User Acceptance

- None.

## Guardrails

- Amend only the amount; preserve date, account, category, and memo.
- Preflight the resulting balance before writing.
- A rejected amendment or deletion changes no data.
