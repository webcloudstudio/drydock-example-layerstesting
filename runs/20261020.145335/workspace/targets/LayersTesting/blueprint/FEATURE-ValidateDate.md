# FEATURE: Date Validation

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Accept only real calendar dates written YYYY-MM-DD. |
| Depends On  | FEATURE-CliEntry.md, ARCHITECTURE.md |
| Provides    | check_date |

## Purpose

Rule 6 of the cash ledger. A date is accepted only when it is a real calendar date in the form
`YYYY-MM-DD`. Impossible dates such as `2026-02-30` are rejected.

## Interface

- `cli.dates.check_date(text: str) -> str` returns `text` when it is a real calendar date in the form
  `YYYY-MM-DD`; otherwise raises `ValueError`.

## Behavior

- The check uses the calendar, including leap years.
- Only the exact `YYYY-MM-DD` shape is accepted; single-digit months or days are rejected.

## Programmatic Acceptance

=== AC valid-date-accepts ===
Intent: check_date returns each real calendar date in YYYY-MM-DD form unchanged, including a leap day.

from cli.dates import check_date

samples = ["2026-01-01", "2024-02-29", "2026-12-31"]
assert [check_date(text) for text in samples] == samples
=== END AC valid-date-accepts ===

=== AC valid-date-rejects ===
Intent: check_date raises ValueError for impossible dates and for every malformed shape.

from cli.dates import check_date

samples = [
    "2026-02-30",
    "2025-02-29",
    "2026-13-01",
    "2026-00-10",
    "2026-04-31",
    "2026-1-01",
    "26-01-01",
    "2026/01/01",
    "",
]
rejected = []
for text in samples:
    try:
        check_date(text)
    except ValueError:
        rejected.append(text)
assert rejected == samples
=== END AC valid-date-rejects ===

## User Acceptance

- None.

## Guardrails

- A date that the calendar does not contain is never accepted.
- Dates are never converted to another format by this feature.
