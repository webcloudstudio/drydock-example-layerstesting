# FEATURE: CSV Output

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Successful commands render their result as CSV: one header row, then data rows, with no quoting and no trailing spaces. |
| Depends On  | FEATURE-LEDGER-ENTRY.md, FEATURE-TEST-RUNNER.md |
| Provides    | cli.output.render_csv(header, rows) |

## Purpose

Every successful command other than `init` writes CSV to standard output. This story supplies the
one renderer that all commands use, so the output conventions live in one place.

## Behavior

- `render_csv(header, rows)` returns the text of one header row followed by one row per entry in
  `rows`.
- Fields are joined with `,`. No field is quoted. Each line ends with `\n`, and the text ends with
  `\n`.
- Values are written exactly as supplied. The renderer does not format numbers or trim text.
- With no rows, the result is the header row alone.

## Programmatic Acceptance

=== AC csv-rows-round-trip ===
Intent: render_csv writes the header and every data row, unquoted, comma-separated, each line ending in a newline.

from cli.output import render_csv

header = ["account", "name", "transactions", "balance"]
rows = [["DRAWER1", "Front Drawer", "39", "2299.38"], ["PETTY", "Petty Cash", "21", "306.25"]]
text = render_csv(header, rows)
assert text.endswith("\n")
raw = [line.split(",") for line in text.split("\n")[:-1]]
assert raw == [header] + rows
=== END AC csv-rows-round-trip ===

=== AC csv-header-only-when-empty ===
Intent: render_csv with no rows writes the header row alone.

from cli.output import render_csv

header = ["table", "rows"]
text = render_csv(header, [])
assert text.endswith("\n")
raw = [line.split(",") for line in text.split("\n")[:-1]]
assert raw == [header]
=== END AC csv-header-only-when-empty ===

=== AC csv-negative-amount-row ===
Intent: render_csv writes a negative amount with its leading minus and no thousands separator.

from cli.output import render_csv

header = ["category", "net"]
rows = [["RENT", "-2700.00"]]
text = render_csv(header, rows)
raw = [line.split(",") for line in text.split("\n")[:-1]]
assert raw == [header] + rows
=== END AC csv-negative-amount-row ===

## User Acceptance

- None.

## Guardrails

- Amounts reach this renderer already formatted as two-decimal text by FEATURE-AMOUNT-CENTS.md.
  This renderer never converts a number to text.
- Values containing a comma or newline are rejected by upstream validation before rendering, so no
  quoting is ever required.
- Diagnostics never pass through this renderer.
