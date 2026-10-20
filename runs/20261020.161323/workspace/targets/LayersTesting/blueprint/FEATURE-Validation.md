# FEATURE: Ledger Validation

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Defines shared validation and atomic preflight rules for ledger commands. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-Persistence-Lifecycle.md |
| Provides    | domain validation, integer-cent amount parsing, date validation, balance validation |
| Consumes    | relational ledger schema, persistence operations |

## Purpose

All commands validate their complete input and all resulting business rules before their first write.

## Validation Rules

- Codes are 1–12 uppercase alphanumeric characters.
- Names and descriptions are 1–40 characters.
- Memos are 0–60 characters.
- Names, descriptions, and memos contain no comma or newline.
- Input amounts match `-?DIGITS[.D[D]]`, have at most two decimal places, and are nonzero.
- Stored amounts are integer cents.
- Dates are real calendar dates in `YYYY-MM-DD`.
- Account and category references must exist.
- Transaction ids must be valid and unique where created.
- No resulting account balance may be negative.
- A rejected operation writes nothing.

## Atomic Preflight

Loaders, posts, amendments, deletes, and transfers first validate all rows and calculate affected balances. Only after the full operation passes may the service call persistence writes, using one transaction for multi-row operations.

## Programmatic Acceptance

=== AC validation-invalid-amount ===
Intent: Invalid decimal precision is rejected with the declared rejection status and no output.
from cli.testing import cli_runner

init_code, _, _ = cli_runner("init")
assert init_code == 0
account_code, _, _ = cli_runner("account", "add", "VALID1", "Valid Account")
assert account_code == 0

code, out, err = cli_runner("txn", "post", "VALID1", "SALES", "1.234", "2026-01-01")
expected_code = 3
assert code == expected_code
assert out == ""
assert isinstance(err, str)
=== END AC validation-invalid-amount ===

=== AC validation-invalid-date ===
Intent: Nonexistent calendar dates are rejected with the declared rejection status.
from cli.testing import cli_runner

code, out, err = cli_runner("txn", "post", "VALID1", "SALES", "1.00", "2026-02-30")
expected_code = 3
assert code == expected_code
assert out == ""
assert isinstance(err, str)
=== END AC validation-invalid-date ===

=== AC validation-negative-balance ===
Intent: A command that would make an account balance negative is rejected without standard output.
from cli.testing import cli_runner

code, out, err = cli_runner("txn", "post", "VALID1", "SALES", "-1.00", "2026-01-01")
expected_code = 3
assert code == expected_code
assert out == ""
assert isinstance(err, str)
=== END AC validation-negative-balance ===

=== AC validation-unknown-reference ===
Intent: Unknown account or category references are rejected before a transaction is written.
from cli.testing import cli_runner

code, out, err = cli_runner("txn", "post", "VALID1", "UNKNOWN1", "1.00", "2026-01-01")
expected_code = 3
assert code == expected_code
assert out == ""
assert isinstance(err, str)
=== END AC validation-unknown-reference ===

=== AC validation-atomic-rejection ===
Intent: A rejected transaction leaves the persisted transaction count unchanged.
from cli.testing import cli_runner

before_code, before_out, _ = cli_runner("count")
assert before_code == 0
before_count = before_out.splitlines()[-1].split(",")[1]

reject_code, reject_out, _ = cli_runner("txn", "post", "VALID1", "UNKNOWN1", "1.00", "2026-01-01")
assert reject_code == 3
assert reject_out == ""

after_code, after_out, _ = cli_runner("count")
assert after_code == 0
after_count = after_out.splitlines()[-1].split(",")[1]
assert after_count == before_count
=== END AC validation-atomic-rejection ===

## User Acceptance

- None.

## Guardrails

- Validation precedes every write.
- Rejected commands leave every table unchanged.
- Balance checks use integer cents.
- Floating-point arithmetic is prohibited.
- Error messages are diagnostics only and are not part of the output contract.
