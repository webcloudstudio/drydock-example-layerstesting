# FEATURE: Validate Amount

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Validates input amount text against the signed, nonzero, at-most-two-decimal rule. |
| Depends On  | ARCHITECTURE.md, FEATURE-AMOUNT-CENTS.md, FEATURE-EXIT-CODES.md, FEATURE-TEST-RUNNER.md |
| Provides    | validation.amount.validate_amount |

## Purpose

Input amounts must match `-?DIGITS[.D[D]]`, must never be zero, and must have at most two decimal places. Invalid amounts are rejected before any conversion to integer cents.

## Behavior

- `validate_amount(text)` returns `text` unchanged when it matches `-?DIGITS[.D[D]]`, has at most two decimal places, and its numeric value is not zero.
- Any other input raises `ValueError` with a one-line message. The CLI layer maps it to exit code 3.
- Examples of rejected input include `0`, `0.00`, `-0`, `1.234`, `1.`, `.50`, `+5`, `1,000.00`, and the empty string.
- The module lives at `validation/amount.py` as part of a namespace package. It creates no `__init__.py`.

## Programmatic Acceptance

=== AC amount-accepts-valid-text ===
Intent: Well-formed nonzero amounts with at most two decimal places are returned unchanged.

from validation.amount import validate_amount

accepted = ["12", "-12.5", "0.01", "5000.00", "-7"]
for text in accepted:
    assert validate_amount(text) == text
=== END AC amount-accepts-valid-text ===

=== AC amount-rejects-malformed-and-zero ===
Intent: Zero, excess decimals, and malformed text each raise ValueError.

from validation.amount import validate_amount

rejected_inputs = ["0", "0.00", "-0", "1.234", "1.", ".50", "+5", "1,000.00", "abc", ""]
rejected = 0
for text in rejected_inputs:
    try:
        validate_amount(text)
    except ValueError:
        rejected += 1
assert rejected == len(rejected_inputs)
=== END AC amount-rejects-malformed-and-zero ===

=== AC amount-rejects-three-decimals ===
Intent: An amount with three decimal places raises ValueError, while two decimal places are accepted.

from validation.amount import validate_amount

raised = False
try:
    validate_amount("1.234")
except ValueError:
    raised = True
assert raised is True

two_decimals = "1.23"
assert validate_amount(two_decimals) == two_decimals
=== END AC amount-rejects-three-decimals ===

## User Acceptance

- None.

## Guardrails

- The validator never converts input to a float. Amounts stay as text until integer-cent conversion.
- The validator never opens a database connection.
