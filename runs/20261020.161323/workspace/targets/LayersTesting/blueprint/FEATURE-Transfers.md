# FEATURE: Transfers

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Transfers funds atomically between two ledger accounts. |
| Depends On  | DATABASE.md, FEATURE-Accounts.md, FEATURE-Transaction-Posting.md, FEATURE-Validation.md |
| Provides    | `ledger transfer` |
| Consumes    | domain validation, relational ledger schema, transaction persistence operations |

## Purpose

Move a positive amount between distinct accounts using two consecutive `TRANSFER` transactions.

## Workflow

The outgoing row uses the next transaction identifier, a negative amount, and memo `transfer to <account>`. The incoming row uses the following identifier, a positive amount, and memo `transfer from <account>`. Both rows are committed together only after validating all inputs and resulting balances.

## Database Interface


- None — persistence is owned by DATABASE.md, FEATURE-Accounts.md, FEATURE-Balance-Reports.md, FEATURE-Category-Reports.md, FEATURE-Monthly-Reports.md, FEATURE-Transaction-Mutation.md, FEATURE-Transaction-Posting.md.

## Programmatic Acceptance

=== AC transfer-creates-pair ===
Intent: A valid transfer creates consecutive outgoing and incoming transaction rows.
from cli.testing import cli_runner

for account in ("A", "B"):
    code, _, _ = cli_runner("account", "add", account, account)
    assert code == 0
category_code, _, _ = cli_runner("load", "categories", "sources/seed_categories.csv")
assert category_code == 0
seed_code, _, _ = cli_runner("txn", "post", "A", "SALES", "10.00", "2026-01-01")
assert seed_code == 0
code, stdout, stderr = cli_runner("transfer", "A", "B", "5.00", "2026-01-02")
assert code == 0
assert "2,2026-01-02,A,TRANSFER,-5.00,transfer to B" in stdout
assert "3,2026-01-02,B,TRANSFER,5.00,transfer from A" in stdout
=== END AC transfer-creates-pair ===

=== AC transfer-insufficient-balance ===
Intent: A transfer that would overdraw the source account is rejected atomically.
from cli.testing import cli_runner

for account in ("A", "B"):
    code, _, _ = cli_runner("account", "add", account, account)
    assert code == 0
category_code, _, _ = cli_runner("load", "categories", "sources/seed_categories.csv")
assert category_code == 0
seed_code, _, _ = cli_runner("txn", "post", "A", "SALES", "1.00", "2026-01-01")
assert seed_code == 0
code, stdout, stderr = cli_runner("transfer", "A", "B", "2.00", "2026-01-02")
assert code == 3
assert stdout == ""
count_code, count_stdout, count_stderr = cli_runner("count")
assert count_code == 0
assert "transactions,1" in count_stdout
=== END AC transfer-insufficient-balance ===

=== AC transfer-same-account ===
Intent: A transfer between the same account is rejected.
from cli.testing import cli_runner

account_code, _, _ = cli_runner("account", "add", "A", "Alpha")
category_code, _, _ = cli_runner("load", "categories", "sources/seed_categories.csv")
assert account_code == 0
assert category_code == 0
seed_code, _, _ = cli_runner("txn", "post", "A", "SALES", "1.00", "2026-01-01")
assert seed_code == 0
code, stdout, stderr = cli_runner("transfer", "A", "A", "1.00", "2026-01-02")
assert code == 3
assert stdout == ""
=== END AC transfer-same-account ===

=== AC transfer-invalid-amount ===
Intent: A transfer with a non-positive amount is rejected.
from cli.testing import cli_runner

for account in ("A", "B"):
    code, _, _ = cli_runner("account", "add", account, account)
    assert code == 0
category_code, _, _ = cli_runner("load", "categories", "sources/seed_categories.csv")
assert category_code == 0
code, stdout, stderr = cli_runner("transfer", "A", "B", "0.00", "2026-01-02")
assert code == 3
assert stdout == ""
=== END AC transfer-invalid-amount ===

## User Acceptance

- None.

## Guardrails

- Transfer amounts must be positive.
- Source and destination accounts must differ and exist.
- Both rows are written atomically or neither is written.
- No account balance may become negative.
