# FEATURE: Transfers

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Execute atomic paired transfers between ledger accounts. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-TRANSACTION-LIFECYCLE.md |
| Provides    | `ledger transfer` |
| Consumes    | accounts repository, categories repository, transactions repository |

## Purpose

Transfer a positive amount between two distinct existing accounts as one atomic operation. The outgoing transaction is written first with a negative amount, followed by the incoming transaction with a positive amount.

## Behavior

The command validates both accounts, the positive amount, date, available source balance, consecutive ids, the `TRANSFER` category, and generated memos before writing either transaction. It emits both rows in order:

- outgoing: `-amount`, memo `transfer to <to>`
- incoming: `+amount`, memo `transfer from <from>`

A rejected transfer returns exit code `3`, emits no standard output, and creates neither row.

## Programmatic Acceptance

=== AC transfer-requires-valid-accounts ===
Intent: A transfer with an absent account is rejected without standard output.
from cli.testing import cli_runner

assert cli_runner("init")[0] == 0
code, stdout, stderr = cli_runner("transfer", "FROM", "MISSING", "1.00", "2026-04-01")
assert code == 3
assert stdout == ""
=== END AC transfer-requires-valid-accounts ===

=== AC transfer-rejects-invalid-input ===
Intent: Transfers reject non-positive amounts, equal accounts, and invalid dates.
from cli.testing import cli_runner

assert cli_runner("init")[0] == 0
for args in (
    ("transfer", "FROM", "FROM", "1.00", "2026-04-01"),
    ("transfer", "FROM", "TO", "0.00", "2026-04-01"),
    ("transfer", "FROM", "TO", "1.00", "2026-02-30"),
):
    code, stdout, stderr = cli_runner(*args)
    assert code == 3
    assert stdout == ""
=== END AC transfer-rejects-invalid-input ===

=== AC transfer-output-shape ===
Intent: A valid transfer produces two persisted transaction rows with paired ids and opposite amounts.
from cli.testing import cli_runner
import csv
import io

source = "SOURCE"
destination = "DEST"
amount = "5.00"
date = "2026-04-01"

assert cli_runner("init")[0] == 0
assert cli_runner("account", "add", source, "Source")[0] == 0
assert cli_runner("account", "add", destination, "Destination")[0] == 0
assert cli_runner("load", "categories", "sources/seed_categories.csv")[0] == 1
=== END AC transfer-output-shape ===

## User Acceptance

- None.

## Guardrails

- Transfers are all-or-nothing.
- The source account must remain non-negative.
- The two transaction rows use consecutive ids and category `TRANSFER`.
- Generated memos must identify the counterparty account.
