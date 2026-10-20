# FEATURE: Usage Errors

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | An unknown command, unknown load table, unknown report, or wrong argument count exits 2 before any database is opened. |
| Depends On  | FEATURE-EXIT-CODES.md |

## Purpose

Usage errors are the caller's mistake, not a data problem. They are reported with exit code 2 and
are detected from the arguments alone.

## Behavior

- An unknown command name exits 2.
- `load` with a table name other than `accounts`, `categories`, or `transactions` exits 2.
- `report` with a name other than `balances`, `categories`, or `monthly` exits 2.
- A command given a number of arguments outside the Commands table exits 2.
- Running `ledger` with no arguments exits 2 and writes one usage line to standard error. This is
  the conventional response chosen in DECISIONS.json (Q-003).
- Each usage error writes nothing to standard output and one line to standard error.

## Programmatic Acceptance

=== AC usage-unknown-command ===
Intent: An unknown command exits 2, writes nothing to standard output, and writes one line to standard error.

from cli.testing import cli_runner

code, out, err = cli_runner("frobnicate")
assert code == 2
assert out == ""
assert err.count("\n") == 1
=== END AC usage-unknown-command ===

=== AC usage-no-arguments ===
Intent: Running with no arguments exits 2 with one usage line on standard error.

from cli.testing import cli_runner

code, out, err = cli_runner()
assert code == 2
assert out == ""
assert err.count("\n") == 1
=== END AC usage-no-arguments ===

=== AC usage-unknown-load-table ===
Intent: load with an unknown table name exits 2 without reading the file.

from cli.testing import cli_runner

code, out, err = cli_runner("load", "nosuch", "unknown-table.csv")
assert code == 2
assert out == ""
=== END AC usage-unknown-load-table ===

=== AC usage-unknown-report ===
Intent: report with an unknown report name exits 2.

from cli.testing import cli_runner

code, out, err = cli_runner("report", "nosuch")
assert code == 2
assert out == ""
=== END AC usage-unknown-report ===

=== AC usage-extra-argument ===
Intent: A command given more arguments than its Commands table entry exits 2.

from cli.testing import cli_runner

code, out, err = cli_runner("count", "extra")
assert code == 2
assert out == ""
=== END AC usage-extra-argument ===

=== AC usage-missing-argument ===
Intent: A sub-verb given fewer arguments than its Commands table entry exits 2.

from cli.testing import cli_runner

code, out, err = cli_runner("account", "get")
assert code == 2
assert out == ""
=== END AC usage-missing-argument ===

## User Acceptance

- None.

## Guardrails

- Usage is checked before any database is opened. A usage error never touches the database.
- `--help` is not treated as an unknown command by this story. Help output belongs to the help story.
- Usage messages are diagnostics. They are never written to standard output.
