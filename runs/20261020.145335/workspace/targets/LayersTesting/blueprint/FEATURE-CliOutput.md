# FEATURE: CSV Output

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Render successful command output as CSV lines and failure diagnostics as one stderr line. |
| Depends On  | FEATURE-CliEntry.md, ARCHITECTURE.md |
| Provides    | render_csv, render_diagnostic |

## Purpose

Every successful command except `init` writes CSV to standard output: one header row, then data
rows, comma-separated, no quoting, no trailing spaces, and `\n` line endings. A failing command
writes nothing to standard output and one diagnostic line to standard error. This feature owns the
text rendering used by every command so that the format is defined once.

## Interface

- `cli.output.render_csv(header: list[str], rows: list[list[str]]) -> str` returns the header line
  followed by one line per row, each terminated by `\n`. Fields are joined with `,` with no quoting
  and no padding.
- `cli.output.render_diagnostic(message: str) -> str` returns the message followed by a single `\n`.
  The caller writes the result to standard error.

## Behavior

- `render_csv` never alters a field value. Callers validate fields before rendering.
- With an empty `rows` list, only the header line is returned.
- `init` writes nothing; it does not call `render_csv`.

## Programmatic Acceptance

=== AC cli-output-csv-shape ===
Intent: render_csv writes the header and each row as one comma-separated line, in order.

from cli.output import render_csv

header = ["account", "name"]
rows = [["DRAWER1", "Front Drawer"], ["SAFE", "Store Safe"]]
text = render_csv(header, rows)
assert [line.split(",") for line in text.split("\n")[:-1]] == [header] + rows
assert text.count("\n") == len(rows) + 1
assert text.split("\n")[-1] == ""
=== END AC cli-output-csv-shape ===

=== AC cli-output-csv-header-only ===
Intent: render_csv with no rows writes only the header line.

from cli.output import render_csv

header = ["table", "rows"]
text = render_csv(header, [])
assert [line.split(",") for line in text.split("\n")[:-1]] == [header]
assert text.count("\n") == 1
=== END AC cli-output-csv-header-only ===

=== AC cli-output-csv-no-padding ===
Intent: render_csv adds no leading or trailing spaces to any line.

from cli.output import render_csv

header = ["table", "rows"]
rows = [["accounts", "4"], ["categories", "7"]]
text = render_csv(header, rows)
assert all(line == line.strip() for line in text.split("\n"))
=== END AC cli-output-csv-no-padding ===

=== AC cli-output-diagnostic-one-line ===
Intent: render_diagnostic returns the message as exactly one line.

from cli.output import render_diagnostic

message = "account DRAWER9 not found"
text = render_diagnostic(message)
assert text.rstrip("\n") == message
assert text.count("\n") == 1
=== END AC cli-output-diagnostic-one-line ===

## User Acceptance

- None.

## Guardrails

- Standard output carries CSV only; diagnostics never go to standard output.
- Field values are never quoted, escaped, or padded by this feature.
- Money is rendered by the amount formatter, not by this feature.
