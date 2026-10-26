# FEATURE: Validation

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Validation of codes, names, memos, amounts and dates, with amounts converted to integer cents. |
| Depends On | FEATURE-ErrorContract.md |
| Provides | validation.parse_amount, validation.parse_date, validation.check_code, validation.check_text |
| Consumes | ledger_errors.Rejected |

## Purpose

Every command validates its inputs through this module before it writes. Every violation raises `ledger_errors.Rejected` (exit 3).

## Interface

- `check_code(value: str) -> str`: 1 to 12 characters, each in `A-Z` or `0-9` (ASCII only). Returns the value.
- `check_text(value: str, max_len: int = 40, min_len: int = 1) -> str`: length within `min_len..max_len`, no comma, no newline or carriage return. Names and descriptions use the defaults; memos use `max_len=60, min_len=0`. Returns the value.
- `parse_amount(text: str) -> int`: the whole string matches `-?[0-9]+(\.[0-9]{1,2})?` (ASCII digits). No leading dot, plus sign, spaces, thousands separator, trailing dot or more than two decimals. The result is integer cents computed with integer arithmetic only, and a zero amount in any form (`0`, `0.00`, `-0`) is rejected.
- `parse_date(text: str) -> str`: matches `YYYY-MM-DD` with ASCII digits and is a real calendar date, with leap years honored (`2028-02-29` valid, `2026-02-29` invalid). Returns the text unchanged.

## Programmatic Acceptance

=== AC validation-amount-valid ===
Intent: parse_amount converts valid amounts to integer cents.

from validation import parse_amount

assert parse_amount("12.50") == 1250
assert parse_amount("-12.5") == -1250
assert parse_amount("5") == 500
assert parse_amount("-0.01") == -1
assert parse_amount("0.10") == 10
assert parse_amount("5000.00") == 500000
assert isinstance(parse_amount("1.00"), int)
=== END AC validation-amount-valid ===

=== AC validation-amount-rejected ===
Intent: parse_amount rejects zero in every form and every malformed amount.

from ledger_errors import Rejected
from validation import parse_amount

bad = ["0", "0.00", "-0", "-0.00", ".50", "+1", " 1", "1 ", "1,000", "1.234", "1.", "", "-", "abc", "1e3"]
for text in bad:
    try:
        parse_amount(text)
    except Rejected:
        continue
    raise AssertionError("amount accepted: " + repr(text))
=== END AC validation-amount-rejected ===

=== AC validation-date-valid ===
Intent: parse_date accepts real calendar dates including a leap day in a leap year.

from validation import parse_date

for text in ("2026-01-01", "2026-04-30", "2028-02-29", "2026-12-31"):
    assert parse_date(text) == text
=== END AC validation-date-valid ===

=== AC validation-date-rejected ===
Intent: parse_date rejects impossible dates and malformed spellings.

from ledger_errors import Rejected
from validation import parse_date

bad = ["2026-02-29", "2026-02-30", "2026-04-31", "2026-13-01", "2026-00-10", "2026-1-01", "20260101", "2026/01/01", "", "2026-01-1x"]
for text in bad:
    try:
        parse_date(text)
    except Rejected:
        continue
    raise AssertionError("date accepted: " + repr(text))
=== END AC validation-date-rejected ===

=== AC validation-code ===
Intent: check_code accepts 1 to 12 characters of A-Z and 0-9 and rejects everything else.

from ledger_errors import Rejected
from validation import check_code

good = ["A", "DRAWER1", "A" * 12, "0123456789AB"]
for value in good:
    assert check_code(value) == value
bad = ["", "A" * 13, "abc", "A-B", "A B", "A,B", "SAFE\n"]
for value in bad:
    try:
        check_code(value)
    except Rejected:
        continue
    raise AssertionError("code accepted: " + repr(value))
=== END AC validation-code ===

=== AC validation-text-name ===
Intent: check_text enforces 1 to 40 characters with no comma or newline by default.

from ledger_errors import Rejected
from validation import check_text

good = ["Front Drawer", "x", "n" * 40]
for value in good:
    assert check_text(value) == value
bad = ["", "n" * 41, "a,b", "line1\nline2", "line1\rline2"]
for value in bad:
    try:
        check_text(value)
    except Rejected:
        continue
    raise AssertionError("text accepted: " + repr(value))
=== END AC validation-text-name ===

=== AC validation-text-memo ===
Intent: check_text with memo limits allows an empty memo up to 60 characters and rejects longer or comma-bearing memos.

from ledger_errors import Rejected
from validation import check_text

empty = ""
assert check_text(empty, max_len=60, min_len=0) == empty
full = "m" * 60
assert check_text(full, max_len=60, min_len=0) == full
for value in ("m" * 61, "a,b", "a\nb"):
    try:
        check_text(value, max_len=60, min_len=0)
    except Rejected:
        continue
    raise AssertionError("memo accepted: " + repr(value))
=== END AC validation-text-memo ===

## User Acceptance

- None.

## Guardrails

- Amounts are parsed with integer arithmetic only; no floating point is used.
- Validation raises `ledger_errors.Rejected`; it never writes to the database or to standard output.
- Only ASCII digits and letters are accepted in codes, amounts and dates.
