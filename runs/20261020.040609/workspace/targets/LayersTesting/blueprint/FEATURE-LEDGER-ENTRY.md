# FEATURE: Ledger Entry

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | The `ledger` executable at the application root parses its arguments and routes each command to its handler. |
| Depends On  | FEATURE-DATABASE-SELECTION.md, DATABASE.md, FEATURE-TEST-RUNNER.md |
| Provides    | ./ledger <command> |
| Consumes    | open_database(dsn) |

## Purpose

`ledger` is the single command surface of the cash ledger. It is an executable file at the
application root. Invoked as `./ledger <command> [arguments]`, it hands the arguments to the
`cli` package entry point `main(argv)` and exits with the integer that `main` returns.

## Behavior

- `ledger` is a regular file at the application root with the executable bit set.
- `ledger` calls `cli.main` with the arguments after the program name and exits with the returned
  integer as its exit status.
- Each command name in the Commands table of `sources/INSTRUCTIONS.md` is routed to a handler in
  the handler table. Each handler is implemented by the story that owns that command.
- The database is opened through `open_database` with the DSN selected by FEATURE-DATABASE-SELECTION.md.
  Usage errors are detected before any database is opened.

## Programmatic Acceptance

=== AC ledger-executable-present ===
Intent: The application root contains an executable regular file named ledger.

from pathlib import Path
import os

ledger = Path("ledger")
assert ledger.is_file()
assert os.access(ledger, os.X_OK)
=== END AC ledger-executable-present ===

=== AC ledger-entry-dispatch-in-process ===
Intent: The cli entry point main returns an integer status for an unknown command name.

from cli.testing import cli_runner

code, out, err = cli_runner("frobnicate")
assert code == 2
assert out == ""
=== END AC ledger-entry-dispatch-in-process ===

=== AC ledger-entry-exit-status ===
Intent: Invoking ./ledger with an unknown command exits with the status main returns.
Requires: executable=python3; scope=test

import os
import subprocess
import tempfile

with tempfile.TemporaryDirectory() as scratch:
    env = {**os.environ, "DATABASE_URL": os.path.join(scratch, "ledger.db")}
    result = subprocess.run(
        ["./ledger", "frobnicate"],
        capture_output=True, text=True, env=env,
    )
print(result.stdout)
print(result.stderr)
assert result.returncode == 2
assert result.stdout == ""
=== END AC ledger-entry-exit-status ===

## User Acceptance

- None.

## Guardrails

- `ledger` contains no report, count, balance, or total computation. Every value comes from a query.
- Application code never reads `sources/run.sh` or any seed file.
- This story routes command names only. It does not implement the behavior of any command.
- No database driver is imported here. Database access goes through `open_database` and the generated
  persistence layer.
