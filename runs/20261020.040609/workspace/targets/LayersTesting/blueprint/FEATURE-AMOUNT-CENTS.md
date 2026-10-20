# FEATURE: Amount Cents

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Converts between validated amount text and integer cents using integer arithmetic only. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-TEST-RUNNER.md |
| Provides    | parse_amount(text) -> int; format_cents(cents) -> str |

## Purpose

Amounts are stored as integer cents and shown with two decimal places. This module is the only place
that converts between the two forms.

## Behavior

- `parse_amount(text)` accepts text matching `-?DIGITS[.D[D]]`, with at most two decimal places, and
  returns the signed integer cent value. `12.5` is `1250` cents.
- `parse_amount` raises `ValueError` for any other text, including text with more than two decimal
  places and text containing a comma.
- `format_cents(cents)` returns text with exactly two decimal places, a leading `-` when negative,
  and no thousands separator.
- All arithmetic is integer arithmetic. No float or `Decimal` conversion is used at any point.

## Programmatic Acceptance

=== AC amount-round-trip ===
Intent: Formatting then parsing returns the original integer cents, and parse returns an int.

from amounts import format_cents, parse_amount

for cents in (0, 1, -1, 1250, -1250, 500000, -2299):
    text = format_cents(cents)
    assert isinstance(text, str)
    assert parse_amount(text) == cents
    assert type(parse_amount(text)) is int
=== END AC amount-round-trip ===

=== AC amount-format-shape ===
Intent: format_cents writes exactly two decimal places, a leading minus only when negative, and no thousands separator.

from amounts import format_cents

for cents in (0, 5, -5, 1250, 500000, -1250000):
    text = format_cents(cents)
    whole, dot, fraction = text.lstrip("-").partition(".")
    assert dot == "."
    assert len(fraction) == 2
    assert fraction.isdigit()
    assert whole.isdigit()
    assert "," not in text
    assert text.startswith("-") == (cents < 0)
=== END AC amount-format-shape ===

=== AC amount-parse-decimal ===
Intent: parse_amount reads a signed one-decimal amount as integer cents.

from amounts import parse_amount

text = "-12.5"
assert parse_amount(text) == -1250
=== END AC amount-parse-decimal ===

=== AC amount-rejects-three-decimals ===
Intent: parse_amount rejects text with more than two decimal places by raising ValueError.

from amounts import parse_amount

text = "1.234"
try:
    parse_amount(text)
except ValueError:
    rejected = True
else:
    rejected = False
assert rejected is True
=== END AC amount-rejects-three-decimals ===

=== AC amount-rejects-separator ===
Intent: parse_amount rejects text containing a thousands separator by raising ValueError.

from amounts import parse_amount

text = "1,000.00"
try:
    parse_amount(text)
except ValueError:
    rejected = True
else:
    rejected = False
assert rejected is True
=== END AC amount-rejects-separator ===

## User Acceptance

- None.

## Guardrails

- Never convert money through `float` at any layer.
- Output amounts never carry a thousands separator.
