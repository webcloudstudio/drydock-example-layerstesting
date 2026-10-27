# FEATURE: Validation

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Pure validation of codes, names, memos, amounts, and dates, and conversion between integer cents and two-decimal text. |
| Depends On | ARCHITECTURE.md |
| Provides | ledger_core.validation, ledger_core.money |

## Purpose

Every command validates its inputs with these functions before it writes. They touch no storage and print nothing. Every violation raises `ledger_core.errors.Rejected` (exit code 3).

## Interface

`ledger_core.validation`, each returning the validated string unchanged:

| Function | Rule |
|---|---|
| `validate_code(value)` | 1 to 12 characters, each in `A-Z` or `0-9`. |
| `validate_name(value)` | 1 to 40 characters, no comma, no newline. Used for account names and category descriptions. |
| `validate_memo(value)` | 0 to 60 characters, no comma, no newline. |
| `validate_date(value)` | A real calendar date written `YYYY-MM-DD` with four-digit year, two-digit month and day. `2026-02-30` is rejected. |

`ledger_core.money`:

| Function | Rule |
|---|---|
| `parse_amount(text) -> int` | Input matches `-?DIGITS[.D[D]]`: at least one digit, an optional single decimal part of one or two digits, no sign other than `-`, no spaces. Returns integer cents. Zero (`0`, `0.00`, `-0`) is rejected. Three or more decimals are rejected. No floating point is used. |
| `format_cents(cents) -> str` | Exactly two decimal places, a leading `-` when negative, no thousands separator: `-12.50`, `0.00`, `5000.00`. |

## Database Interface

- None — this feature is pure and reaches no repository.

## Programmatic Acceptance

=== AC validation-code ===
Intent: Codes of 1 to 12 characters from A-Z and 0-9 are returned unchanged; empty, lowercase, too long, and other characters are rejected with exit code 3.

from ledger_core.validation import validate_code
from ledger_core.errors import Rejected

def rejected(value):
    try:
        validate_code(value)
    except Rejected as err:
        assert err.exit_code == 3
        return True
    return False

for good in ["DRAWER1", "A", "0", "ABCDEFGHIJKL", "Z9Z9Z9Z9Z9Z9"]:
    assert validate_code(good) == good
for bad in ["", "drawer1", "Drawer", "ABCDEFGHIJKLM", "AB-C", "A B", "A_B"]:
    assert rejected(bad), bad
=== END AC validation-code ===

=== AC validation-name ===
Intent: Names of 1 to 40 characters without comma or newline are accepted; empty, 41 characters, comma, and newline are rejected.

from ledger_core.validation import validate_name
from ledger_core.errors import Rejected

def rejected(value):
    try:
        validate_name(value)
    except Rejected as err:
        assert err.exit_code == 3
        return True
    return False

for good in ["Front Drawer", "x", "x" * 40]:
    assert validate_name(good) == good
for bad in ["", "x" * 41, "a,b", "a\nb"]:
    assert rejected(bad), repr(bad)
=== END AC validation-name ===

=== AC validation-memo ===
Intent: Memos of 0 to 60 characters without comma or newline are accepted, including the empty memo; 61 characters, comma, and newline are rejected.

from ledger_core.validation import validate_memo
from ledger_core.errors import Rejected

def rejected(value):
    try:
        validate_memo(value)
    except Rejected as err:
        assert err.exit_code == 3
        return True
    return False

for good in ["", "walk in sale", "m" * 60]:
    assert validate_memo(good) == good
for bad in ["m" * 61, "a,b", "a\nb"]:
    assert rejected(bad), repr(bad)
=== END AC validation-memo ===

=== AC validation-date ===
Intent: Real calendar dates in YYYY-MM-DD form are accepted, including a leap day; impossible dates and other layouts are rejected.

from ledger_core.validation import validate_date
from ledger_core.errors import Rejected

def rejected(value):
    try:
        validate_date(value)
    except Rejected as err:
        assert err.exit_code == 3
        return True
    return False

for good in ["2026-04-01", "2024-02-29", "2026-12-31"]:
    assert validate_date(good) == good
for bad in ["2026-02-30", "2026-02-29", "2026-13-01", "2026-00-10", "2026-4-1", "20260401", "", "2026-04-01x"]:
    assert rejected(bad), bad
=== END AC validation-date ===

=== AC money-parse-valid ===
Intent: Valid amount text parses to the integer cents it denotes, as an int and not a float.

from ledger_core.money import parse_amount

cases = [("45.50", 4550), ("-12.34", -1234), ("7", 700), ("1.5", 150),
         ("0.01", 1), ("5000.00", 500000), ("-0.99", -99), ("-3", -300)]
for text, cents in cases:
    value = parse_amount(text)
    assert type(value) is int, text
    assert value == cents, text
=== END AC money-parse-valid ===

=== AC money-parse-invalid ===
Intent: Zero, three or more decimals, and text outside -?DIGITS[.D[D]] are rejected with exit code 3.

from ledger_core.money import parse_amount
from ledger_core.errors import Rejected

def rejected(value):
    try:
        parse_amount(value)
    except Rejected as err:
        assert err.exit_code == 3
        return True
    return False

for bad in ["0", "0.00", "-0", "-0.0", "1.234", "1.000", "abc", "1.", ".5", "+5", "1,5", "", "-", "1 .5", "--5"]:
    assert rejected(bad), repr(bad)
=== END AC money-parse-invalid ===

=== AC money-format ===
Intent: Integer cents format with exactly two decimals, a leading minus when negative, and no thousands separator.

from ledger_core.money import format_cents

cases = [(-1250, "-12.50"), (0, "0.00"), (500000, "5000.00"),
         (5, "0.05"), (-5, "-0.05"), (123456789, "1234567.89")]
for cents, text in cases:
    assert format_cents(cents) == text, cents
=== END AC money-format ===

=== AC money-round-trip ===
Intent: Parsing the formatted text of any nonzero cents value returns the same cents.

from ledger_core.money import parse_amount, format_cents

for cents in [1, -1, 99, 100, -100, 12345, -987654, 500000]:
    assert parse_amount(format_cents(cents)) == cents
=== END AC money-round-trip ===

## User Acceptance

- None.

## Guardrails

- No floating point is used for money, in parsing or formatting.
- Validation functions write nothing and read nothing from storage.
- A violation raises `Rejected`; no other exception type signals invalid input.
