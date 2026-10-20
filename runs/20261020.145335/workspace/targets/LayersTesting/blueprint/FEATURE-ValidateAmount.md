# FEATURE: Amount Validation

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Parse input amounts to integer cents and format stored cents as two-decimal text. |
| Depends On  | FEATURE-CliEntry.md, ARCHITECTURE.md |
| Provides    | parse_amount, format_amount |

## Purpose

Rule 5 of the cash ledger. Amounts are stored as integer cents. Input text matching
`-?DIGITS[.D[D]]` is parsed without floating point; output always has exactly two decimals.

## Interface

- `cli.amount.parse_amount(text: str) -> int` returns the signed integer number of cents. It accepts
  text matching `-?DIGITS[.D[D]]` with at most two decimal places and a non-zero value; otherwise it
  raises `ValueError`.
- `cli.amount.format_amount(cents: int) -> str` returns the amount with exactly two decimal places,
  a leading `-` when negative, and no thousands separator.

## Behavior

- Parsing uses integer arithmetic only.
- A single decimal place is padded to two places in the stored value, not in the input.

## Programmatic Acceptance

=== AC valid-amount-parse-cents ===
Intent: parse_amount converts accepted input text to the expected integer cents.

from cli.amount import parse_amount

cases = [("12.5", 1250), ("-0.05", -5), ("7", 700), ("0.1", 10), ("-3", -300), ("1.10", 110)]
parsed = [parse_amount(text) for text, _ in cases]
assert parsed == [cents for _, cents in cases]
=== END AC valid-amount-parse-cents ===

=== AC valid-amount-round-trip ===
Intent: format_amount of parse_amount returns each canonical two-decimal input unchanged.

from cli.amount import format_amount, parse_amount

samples = ["12.50", "-0.05", "0.10", "5000.00", "-12.50"]
assert [format_amount(parse_amount(text)) for text in samples] == samples
=== END AC valid-amount-round-trip ===

=== AC valid-amount-rejects ===
Intent: parse_amount raises ValueError for zero, excess decimals, malformed, signed-plus, and empty input.

from cli.amount import parse_amount

samples = ["0", "0.00", "-0", "1.234", "1.", ".5", "1,00", "+5", "abc", ""]
rejected = []
for text in samples:
    try:
        parse_amount(text)
    except ValueError:
        rejected.append(text)
assert rejected == samples
=== END AC valid-amount-rejects ===

=== AC valid-amount-integer-type ===
Intent: parse_amount returns a Python int, never a float.

from cli.amount import parse_amount

assert type(parse_amount("1.10")) is int
assert type(parse_amount("-7")) is int
=== END AC valid-amount-integer-type ===

## User Acceptance

- None.

## Guardrails

- No floating-point value is used for money at any layer.
- Zero amounts are rejected on input.
- Output never contains a thousands separator.
