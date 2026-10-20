# FEATURE: CLI Dispatcher

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provide the executable ledger dispatcher, CSV output boundary, and exit-code mapping. |
| Depends On  | FEATURE-Database-Configuration.md, DATABASE.md |
| Provides    | `./ledger`, command dispatch, CSV output, exit-code dispatch |
| Consumes    | DATABASE_URL resolution, schema initialization |

## Command Boundary

The executable `ledger` is located at the application root and invokes the CLI entry point. The dispatcher recognizes the documented command families: `init`, `count`, `load`, `account`, `txn`, `transfer`, and `report`.

Successful commands emit deterministic CSV with a header and newline-delimited rows, except `init`, which emits nothing. Diagnostics are written only to standard error. The dispatcher maps domain failures to the documented exit codes.

## Programmatic Acceptance

=== AC cli-dispatch-executable ===
Intent: The application root contains an executable ledger entry point.
from pathlib import Path
import os

ledger = Path("ledger")
assert ledger.is_file()
assert os.access(ledger, os.X_OK)
=== END AC cli-dispatch-executable ===

=== AC cli-dispatch-init-and-count ===
Intent: The dispatcher reaches schema initialization and produces structured count output.
import csv
from cli.testing import cli_runner

init_code, init_stdout, init_stderr = cli_runner("init")
assert init_code == 0
assert init_stdout == ""
count_code, count_stdout, count_stderr = cli_runner("count")
assert count_code == 0
rows = list(csv.reader(count_stdout.splitlines()))
assert rows[0] == ["table", "rows"]
assert len(rows) == 4
assert all(len(row) == 2 for row in rows)
=== END AC cli-dispatch-init-and-count ===

=== AC cli-dispatch-error-channel ===
Intent: Rejected commands return a failure code without standard-output data and provide diagnostics on standard error.
from cli.testing import cli_runner

code, stdout, stderr = cli_runner("account", "add", "BAD-CODE", "Name")
assert code == 3
assert stdout == ""
assert stderr != ""
=== END AC cli-dispatch-error-channel ===

## User Acceptance

- None.

## Guardrails

- The root executable must be named `ledger`.
- Successful output must be CSV with no diagnostic text on standard output.
- Failure diagnostics must never be used as successful data output.
- Report values must not be embedded in the dispatcher.
