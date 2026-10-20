# FEATURE: Date Validation

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Accept only real YYYY-MM-DD calendar dates for every command that takes a date. |
| Depends On  | ARCHITECTURE.md |
| Provides    | parse_date |

## Purpose

Dates enter the ledger through `txn post`, `transfer`, and `load transactions`. This module is the
single parser for all of them. It lives at `dates.py` in the application root.

## Rules

- `parse_date(text)` accepts exactly the form `YYYY-MM-DD` with four digits, a two-digit month, and
  a two-digit day.
- The date must exist on the calendar. Leap years are honored, so `2028-02-29` is valid and
  `2026-02-29` is not.
- Impossible dates such as `2026-02-30`, month `13`, and day `00` are rejected.
- Any other shape, including `2026-1-01`, `20260101`, and `2026/01/01`, is rejected.
- Success returns a `datetime.date`. Rejection raises `ValueError`, which the command layer maps to
  exit 3.

## Programmatic Acceptance

=== AC date-round-trip ===
Intent: Valid calendar dates parse to a datetime.date whose ISO form equals the input.

import datetime
from dates import parse_date

for text in ("2026-01-01", "2026-02-28", "2028-02-29", "2026-12-31"):
    result = parse_date(text)
    assert isinstance(result, datetime.date)
    assert result.isoformat() == text
=== END AC date-round-trip ===

=== AC date-rejects-impossible ===
Intent: Dates that do not exist on the calendar are rejected.

from dates import parse_date


def rejected(check, value):
    try:
        check(value)
    except ValueError:
        return True
    return False


for text in ("2026-02-30", "2026-02-29", "2026-04-31", "2026-13-01", "2026-00-10", "2026-01-00"):
    assert rejected(parse_date, text) is True
=== END AC date-rejects-impossible ===

=== AC date-rejects-malformed ===
Intent: Text that is not in the YYYY-MM-DD shape is rejected.

from dates import parse_date


def rejected(check, value):
    try:
        check(value)
    except ValueError:
        return True
    return False


for text in ("", "2026-1-01", "2026-01-1", "20260101", "26-01-01", "2026/01/01", "not-a-date"):
    assert rejected(parse_date, text) is True
=== END AC date-rejects-malformed ===

## User Acceptance

- None.

## Guardrails

- The parser never reads the system clock; it validates only the text it is given.
- The module never opens or reads the database.
