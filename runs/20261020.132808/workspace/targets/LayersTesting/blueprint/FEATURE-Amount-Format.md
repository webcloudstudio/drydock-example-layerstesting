# FEATURE: Amount Format

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Parse input amounts into integer cents and format stored cents for output. |
| Depends On  | ARCHITECTURE.md |
| Provides    | parse_amount_cents, format_amount_cents |

## Purpose

Every amount crossing the command boundary is converted here. The module lives at `amounts.py` in
the application root. No floating-point value is produced or accepted at any point.

## Rules

- `parse_amount_cents(text)` accepts text matching `-?DIGITS` optionally followed by `.D` or `.DD`.
  It returns an `int` count of cents.
- Input with a leading plus sign, surrounding whitespace, a thousands separator, a bare decimal
  point, or no digits is rejected.
- Zero in any form (`0`, `0.0`, `0.00`, `-0.00`) is rejected because an amount may not be zero.
- `format_amount_cents(cents)` returns exactly two decimal places, a leading `-` when negative, and
  no separators. A zero value is written `0.00`, never `-0.00`.
- Rejections raise `ValueError`. The command layer maps them to exit 3.

## Programmatic Acceptance

=== AC amount-round-trip ===
Intent: Canonical amount strings parse to cents and format back to the same string.

from amounts import parse_amount_cents, format_amount_cents

canonical = ("12.50", "-12.50", "5000.00", "0.05", "-0.01")
for text in canonical:
    assert format_amount_cents(parse_amount_cents(text)) == text
=== END AC amount-round-trip ===

=== AC amount-short-forms-equal ===
Intent: Amounts with one decimal or no decimal parse to the same cents as their two-decimal forms.

from amounts import parse_amount_cents

short = "12.5"
full = "12.50"
whole = "3"
whole_full = "3.00"
assert parse_amount_cents(short) == parse_amount_cents(full)
assert parse_amount_cents(whole) == parse_amount_cents(whole_full)
=== END AC amount-short-forms-equal ===

=== AC amount-integer-cents ===
Intent: parse_amount_cents returns a Python int, never a float.

from amounts import parse_amount_cents

sample = "12.50"
cents = parse_amount_cents(sample)
assert type(cents) is int
=== END AC amount-integer-cents ===

=== AC amount-rejects-zero ===
Intent: Every zero form of an input amount is rejected.

from amounts import parse_amount_cents


def rejected(check, value):
    try:
        check(value)
    except ValueError:
        return True
    return False


for text in ("0", "0.0", "0.00", "-0.00"):
    assert rejected(parse_amount_cents, text) is True
=== END AC amount-rejects-zero ===

=== AC amount-rejects-malformed ===
Intent: Input that does not match the amount pattern is rejected.

from amounts import parse_amount_cents


def rejected(check, value):
    try:
        check(value)
    except ValueError:
        return True
    return False


malformed = ("", "-", "abc", "1.234", "1,000.00", " 1.00", "+1.00", ".50", "1.", "--1.00", "1.2.3")
for text in malformed:
    assert rejected(parse_amount_cents, text) is True
=== END AC amount-rejects-malformed ===

=== AC amount-format-zero-and-decimals ===
Intent: Formatted amounts have exactly two decimals, a leading minus only when negative, and no separators.

from amounts import format_amount_cents

zero = 0
text = format_amount_cents(zero)
assert text[0] != "-"
assert len(text.split(".")[1]) == 2

negative = format_amount_cents(-5)
assert negative[0] == "-"
assert len(negative.split(".")[1]) == 2

large = format_amount_cents(500000000)
assert "," not in large
=== END AC amount-format-zero-and-decimals ===

## User Acceptance

- None.

## Guardrails

- No floating-point arithmetic is used for money at any layer of this module.
- The module never opens or reads the database.
- Amount text is ASCII only.
