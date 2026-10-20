# FEATURE: CLI Foundation

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provides the executable ledger command, dispatch, configuration resolution, CSV output, and exit-code behavior. |
| Depends On  | ARCHITECTURE.md, DATABASE.md |
| Provides    | ./ledger executable, command dispatch, usage validation, exit-code mapping |
| Consumes    | ledger application boundaries, ledger persistence operations |

## Purpose

The root executable `ledger` is the only user-facing entry point. It dispatches supported commands and maps outcomes to the contract's exit codes.

## Configuration

Resolve the database location from `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`. The resolved value is passed to the shipped persistence library.

## Command Contract

Successful commands emit CSV to standard output. Failures emit no standard output and one diagnostic line to standard error.

| Exit code | Meaning |
|---|---|
| 0 | Success |
| 1 | Operational failure |
| 2 | Usage error |
| 3 | Rejected input or rejected state change |
| 4 | Requested record not found |

Unknown commands, reports, tables, and incorrect argument counts return exit code 2.

## Programmatic Acceptance

=== AC cli-success-dispatch ===
Intent: The executable dispatches a supported command and returns its successful exit status.

import os
import subprocess
import tempfile

with tempfile.TemporaryDirectory() as directory:
    env = {**os.environ, "DATABASE_URL": os.path.join(directory, "ledger.db")}
    result = subprocess.run(["./ledger", "init"], capture_output=True, text=True, env=env)
    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0
    assert result.stdout == ""
=== END AC cli-success-dispatch ===

=== AC cli-usage-error ===
Intent: An unknown command is reported as a usage error without standard output.

import os
import subprocess
import tempfile

with tempfile.TemporaryDirectory() as directory:
    env = {**os.environ, "DATABASE_URL": os.path.join(directory, "ledger.db")}
    result = subprocess.run(["./ledger", "frobnicate"], capture_output=True, text=True, env=env)
    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 2
    assert result.stdout == ""
    assert len(result.stderr.splitlines()) == 1
=== END AC cli-usage-error ===

=== AC cli-database-precedence ===
Intent: DATABASE_URL takes precedence over DATABASE_PATH when selecting the store.

import os
import subprocess
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as directory:
    url_db = Path(directory) / "url.db"
    path_db = Path(directory) / "path.db"
    env = {**os.environ, "DATABASE_URL": str(url_db), "DATABASE_PATH": str(path_db)}
    result = subprocess.run(["./ledger", "init"], capture_output=True, text=True, env=env)
    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0
    assert url_db.exists()
    assert not path_db.exists()
=== END AC cli-database-precedence ===

## User Acceptance

- None.

## Guardrails

- The launcher must be executable at the application root.
- The CLI must not read or embed supplied seed files or report answers.
- Failed commands must not write standard output.
- Diagnostics must go to standard error.
- Database drivers must not be opened outside `persistence`.
