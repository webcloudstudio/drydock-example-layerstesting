# FEATURE: Validate Date

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Validates that input is a real calendar date written YYYY-MM-DD. |
| Depends On  | ARCHITECTURE.md, FEATURE-EXIT-CODES.md, FEATURE-TEST-RUNNER.md |
| Provides    | validation.date.validate_date |

## Purpose

Dates are real calendar dates written `YYYY-MM-DD`. Impossible dates such as `2026-02-30` are rejected.

## Behavior

- `validate_date(text)` returns `text` unchanged when it is exactly four digits, a hyphen, two digits, a hyphen, and two digits, and those parts form a real calendar date, including leap-day rules.
- Any other input raises `ValueError` with a one-line message. The CLI layer maps it to exit code 3.
- The module lives at `validation/date.py` as part of a namespace package. It creates no `__init__.py`.

## Programmatic Acceptance

=== AC date-accepts-real-dates ===
Intent: Real calendar dates in YYYY-MM-DD form, including a leap day, are returned unchanged.

from validation.date import validate_date

accepted = ["2026-02-28", "2026-12-31", "2028-02-29"]
for text in accepted:
    assert validate_date(text) == text
=== END AC date-accepts-real-dates ===

=== AC date-rejects-impossible-dates ===
Intent: Impossible calendar dates raise ValueError, including 2026-02-30 and a non-leap 2026-02-29.

from validation.date import validate_date

rejected_inputs = ["2026-02-30", "2026-02-29", "2026-13-01", "2026-04-31"]
rejected = 0
for text in rejected_inputs:
    try:
        validate_date(text)
    except ValueError:
        rejected += 1
assert rejected == len(rejected_inputs)
=== END AC date-rejects-impossible-dates ===

=== AC date-rejects-bad-format ===
Intent: Dates that are not exactly YYYY-MM-DD raise ValueError.

from validation.date import validate_date

rejected_inputs = ["2026-1-5", "26-01-05", "2026/01/05", ""]
rejected = 0
for text in rejected_inputs:
    try:
        validate_date(text)
    except ValueError:
        rejected += 1
assert rejected == len(rejected_inputs)
=== END AC date-rejects-bad-format ===

## User Acceptance

- None.

## Guardrails

- The validator never opens a database connection.
- The validator never accepts a date that a calendar cannot represent.
