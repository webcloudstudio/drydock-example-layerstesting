# FEATURE: CLI Dispatch

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Routes `ledger` command words to their handlers and rejects usage errors with exit 2 before any database access. |
| Depends On  | FEATURE-CLI-Platform.md |
| Provides    | ledger <command> routing, usage error exit 2 |
| Consumes    | cli.main, cli_runner |

## Purpose

Every `ledger` invocation is either handed to the handler its story owns or rejected as a usage error. Nothing else happens first.

## Behavior

- The command word, sub-verb, and argument count are checked against the Commands table before any handler or database access runs.
- An unknown command, unknown sub-verb, unknown table, unknown report, or wrong argument count exits 2 with exactly one line on standard error and nothing on standard output.
- A correctly shaped command is passed to its handler, and the handler's exit code is returned unchanged.

## Programmatic Acceptance

=== AC cli-dispatch-usage-errors-exit-two ===
Intent: Each unknown command, sub-verb, table, report, or wrong argument count exits 2 with empty stdout and one stderr line.

from cli.testing import cli_runner

usage_errors = [
    ("frobnicate",),
    ("report", "nosuch"),
    ("load", "nosuch", "missing.csv"),
    ("account", "nosuch"),
    ("count", "extra"),
    ("account", "add", "ONLY"),
]

for args in usage_errors:
    code, out, err = cli_runner(*args)
    print(args, err)
    assert code == 2
    assert out == ""
    assert len(err.splitlines()) == 1
=== END AC cli-dispatch-usage-errors-exit-two ===

=== AC cli-dispatch-usage-touches-no-database ===
Intent: A usage error exits 2 without creating or opening the database file named by DATABASE_URL.

import os
import tempfile

from cli.testing import cli_runner

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn

code, out, err = cli_runner("frobnicate")
assert code == 2
assert not os.path.exists(dsn)
=== END AC cli-dispatch-usage-touches-no-database ===

=== AC cli-dispatch-main-returns-usage-code ===
Intent: The published `main` entry point returns the integer 2 for an unknown command.

from cli import main

result = main(["frobnicate"])
assert isinstance(result, int)
assert result == 2
=== END AC cli-dispatch-main-returns-usage-code ===

## User Acceptance

- None.

## Guardrails

- Argument validation completes before any database connection is opened.
- Usage diagnostics go to standard error only and are never written to standard output.
- Dispatch never reads a file named on the command line before validating the command.
