# FEATURE: Validate Text

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Validates free-text names, descriptions, and memos against their length limits and forbidden characters. |
| Depends On  | ARCHITECTURE.md, FEATURE-EXIT-CODES.md, FEATURE-TEST-RUNNER.md |
| Provides    | validation.text.validate_text |

## Purpose

Names and descriptions must be 1 to 40 characters. Memos must be 0 to 60 characters. None may contain a comma or a newline. This module enforces those rules before any command writes to the database.

## Behavior

- `validate_text(value, min_length, max_length)` returns `value` unchanged when `min_length <= len(value) <= max_length` and `value` contains neither `,` nor a newline.
- Any other input raises `ValueError` with a one-line message. The CLI layer maps `ValueError` from validators to exit code 3.
- Callers pass the limits: names and descriptions use `1, 40`; memos use `0, 60`.
- The module lives at `validation/text.py` as part of a namespace package. It creates no `__init__.py`.

## Programmatic Acceptance

=== AC text-accepts-bounds ===
Intent: Text at each inclusive limit, including an empty memo, is returned unchanged.

from validation.text import validate_text

name_min = "x"
name_max = "A" * 40
memo_max = "m" * 60
empty_memo = ""

assert validate_text(name_min, 1, 40) == name_min
assert validate_text(name_max, 1, 40) == name_max
assert validate_text(empty_memo, 0, 60) == empty_memo
assert validate_text(memo_max, 0, 60) == memo_max
=== END AC text-accepts-bounds ===

=== AC text-rejects-length ===
Intent: Text shorter than the minimum or longer than the maximum raises ValueError.

from validation.text import validate_text

cases = [
    ("", 1, 40),
    ("B" * 41, 1, 40),
    ("C" * 61, 0, 60),
]
rejected = 0
for value, low, high in cases:
    try:
        validate_text(value, low, high)
    except ValueError:
        rejected += 1
assert rejected == len(cases)
=== END AC text-rejects-length ===

=== AC text-rejects-comma-and-newline ===
Intent: A comma or a newline anywhere in the text raises ValueError regardless of length.

from validation.text import validate_text

cases = [
    ("Front,Desk", 1, 40),
    ("two\nlines", 0, 60),
    ("memo, with comma", 0, 60),
]
rejected = 0
for value, low, high in cases:
    try:
        validate_text(value, low, high)
    except ValueError:
        rejected += 1
assert rejected == len(cases)
=== END AC text-rejects-comma-and-newline ===

## User Acceptance

- None.

## Guardrails

- The validator never opens a database connection.
- The validator never converts text to a number and never uses floating point.
