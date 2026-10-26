# FEATURE: Csv Output

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Integer-only cents formatting and CSV row writing to standard output. |
| Depends On | FEATURE-CliFoundation.md |
| Provides | csv_output.format_cents, csv_output.write_rows |
| Consumes | ledger.register_command |

## Purpose

Every successful command writes its result through this module so that formatting is identical everywhere.

## Interface

- `csv_output.format_cents(cents: int) -> str` returns the amount with exactly two decimals, a leading `-` when negative, no thousands separator, and `0.00` for zero (never `-0.00`). Computed with integer arithmetic (`divmod` on the absolute value). A non-`int` argument (including `float` and `bool`) raises `TypeError`.
- `csv_output.write_rows(rows) -> None` writes each row to the current `sys.stdout` (looked up at call time) as its cells joined by `,`, with no quoting, no trailing spaces and a `\n` line ending. Cells that are `int` are rendered with `str`; a `float` cell raises `TypeError`. Nothing is written when a row is invalid.

## Programmatic Acceptance

=== AC csv-format-cents-values ===
Intent: format_cents renders zero, positive, negative and large amounts with two decimals and no separator.

from csv_output import format_cents

assert format_cents(0) == "0.00"
assert format_cents(5) == "0.05"
assert format_cents(-5) == "-0.05"
assert format_cents(-1250) == "-12.50"
assert format_cents(1250) == "12.50"
assert format_cents(500000) == "5000.00"
assert format_cents(123456789) == "1234567.89"
=== END AC csv-format-cents-values ===

=== AC csv-format-cents-rejects-float ===
Intent: format_cents refuses non-integer input so money never passes through floating point.

from csv_output import format_cents

for bad in (1.5, 2.0, "100", None):
    try:
        format_cents(bad)
    except TypeError:
        continue
    raise AssertionError("format_cents accepted a non-int value")
=== END AC csv-format-cents-rejects-float ===

=== AC csv-write-rows-layout ===
Intent: write_rows emits comma-joined unquoted rows, each ending in a newline, with no carriage returns.

import contextlib
import io
from csv_output import write_rows

rows = [["account", "name", "transactions", "balance"], ["CASH9", "Event Cash Box", 0, "0.00"]]
buffer = io.StringIO()
with contextlib.redirect_stdout(buffer):
    write_rows(rows)
text = buffer.getvalue()
assert text.endswith("\n")
assert "\r" not in text
assert text.splitlines() == [",".join(str(c) for c in row) for row in rows]
=== END AC csv-write-rows-layout ===

=== AC csv-write-rows-rejects-float ===
Intent: write_rows refuses a float cell and writes nothing.

import contextlib
import io
from csv_output import write_rows

buffer = io.StringIO()
raised = False
with contextlib.redirect_stdout(buffer):
    try:
        write_rows([["a", 1.5]])
    except TypeError:
        raised = True
assert raised
assert buffer.getvalue() == ""
=== END AC csv-write-rows-rejects-float ===

=== AC csv-through-cli ===
Intent: A registered command writing rows through write_rows produces CSV that parses back to the same rows.

import csv
import io
import cli
from cli.testing import cli_runner
from csv_output import write_rows

rows = [["table", "rows"], ["accounts", "0"], ["categories", "0"]]
name = "zzrows"
cli.register_command(name, lambda args: write_rows(rows))
code, out, err = cli_runner(name)
assert code == 0
assert "\r" not in out
assert list(csv.reader(io.StringIO(out))) == rows
=== END AC csv-through-cli ===

## User Acceptance

- None.

## Guardrails

- No floating point is used for money at any layer; `format_cents` uses integer arithmetic only.
- No thousands separator, no quoting and no trailing spaces appear in any output.
- Zero is always written `0.00`, never `-0.00`.
