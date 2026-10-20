# FEATURE: CLI Output

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provides the CSV writer every successful ledger command uses for standard output. |
| Depends On  | FEATURE-CLI-Platform.md |
| Provides    | cli.output.write_csv(header, rows) |
| Consumes    | none |

## Purpose

Every successful command except `init` reports its result as CSV on standard output, in one shared format.

## Behavior

- `write_csv(header, rows)` writes the header row, then one row per entry in `rows`, to standard output.
- Fields are joined with commas, are never quoted, and each line ends with a single `\n`.
- No line carries a trailing space, and no line contains a carriage return.
- With an empty `rows`, only the header row is written.
- Nothing is written to standard error.

## Programmatic Acceptance

=== AC cli-output-header-then-rows ===
Intent: `write_csv` writes the header row followed by one comma-separated line per data row, in order.

import contextlib
import io

from cli.output import write_csv

header = ["account", "name"]
rows = [["ALPHA", "Alpha Drawer"], ["BETA", "Beta Safe"]]

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    write_csv(header, rows)

lines = buf.getvalue().splitlines()
assert len(lines) == len(rows) + 1
assert lines[0].split(",") == header
assert [line.split(",") for line in lines[1:]] == rows
=== END AC cli-output-header-then-rows ===

=== AC cli-output-no-quoting-or-trailing-space ===
Intent: Output contains no quote characters, no carriage returns, no trailing spaces, and one line ending per written line.

import contextlib
import io

from cli.output import write_csv

header = ["category", "description"]
rows = [["SALES", "Sales receipts"], ["RENT", "Rent"]]

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    write_csv(header, rows)

text = buf.getvalue()
assert '"' not in text
assert chr(13) not in text
assert text.count(chr(10)) == len(rows) + 1
assert all(line == line.rstrip() for line in text.splitlines())
=== END AC cli-output-no-quoting-or-trailing-space ===

=== AC cli-output-header-only-and-silent-stderr ===
Intent: With no data rows, only the header is written to standard output, and nothing is written to standard error.

import contextlib
import io

from cli.output import write_csv

header = ["table", "loaded"]

out_buf = io.StringIO()
err_buf = io.StringIO()
with contextlib.redirect_stdout(out_buf), contextlib.redirect_stderr(err_buf):
    write_csv(header, [])

lines = out_buf.getvalue().splitlines()
assert len(lines) == 1
assert lines[0].split(",") == header
assert err_buf.getvalue() == ""
=== END AC cli-output-header-only-and-silent-stderr ===

## User Acceptance

- None.

## Guardrails

- No field is quoted or escaped; values containing a comma or newline are rejected upstream by validation, never encoded here.
- The writer formats only the values it is given and never formats money or dates itself.
