# FEATURE: Automated Suite

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provides the POSIX `bin/test.sh` wrapper that runs the project's pytest suite against a temporary database and exits zero only when every test passes. |
| Depends On  | ARCHITECTURE.md, FEATURE-CLI-Platform.md, DATABASE.md |
| Provides    | bin/test.sh |

## Purpose

`bin/test.sh` is the application's own automated test entry point. It is POSIX `sh`, runs from the application root, starts pytest against a real temporary SQLite database, and exits zero only when every test passes. The suite it runs covers each command, each exit code, and each rule in `sources/INSTRUCTIONS.md`.

The suite is written beside the code by the build agent. This story owns the wrapper and its contract, not the individual tests.

## Behavior

- `bin/test.sh` is a POSIX `sh` script. It creates or reuses the `.venv` created by the foundation and runs `pytest -q` from the application root.
- The database for the run is a fresh temporary SQLite file, removed on exit.
- The wrapper exits with pytest's status. A failing or erroring test makes it exit nonzero.

## Programmatic Acceptance

=== AC test-suite-posix-syntax ===
Intent: bin/test.sh parses as POSIX sh without executing any test.
Requires: executable=sh; scope=test

import os
import subprocess

result = subprocess.run(
    ["sh", "-n", "bin/test.sh"],
    capture_output=True, text=True,
    env={**os.environ},
)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC test-suite-posix-syntax ===

=== AC test-suite-passes ===
Intent: Running bin/test.sh from the application root exits zero when every automated test passes.
Requires: executable=sh; scope=test

import os
import subprocess
import sys

result = subprocess.run(
    ["sh", "bin/test.sh"],
    capture_output=True, text=True,
    env={**os.environ},
)
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == 0
=== END AC test-suite-passes ===

## User Acceptance

- None.

## Guardrails

- Do not modify, rewrite, or substitute any file under `sources/`.
- `bin/test.sh` must not read `sources/run.sh` or any seed file.
- The wrapper must not open a database driver directly; tests reach the database only through the persistence package.
