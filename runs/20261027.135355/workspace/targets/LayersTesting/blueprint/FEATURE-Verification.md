# FEATURE: Verification

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Terminal gate that runs the supplied end-to-end grader and the project's own test suite. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-CommandContract.md, FEATURE-NoNegativeBalance.md |
| Provides | — |
| Consumes | ledger |

## Purpose

Terminal story. After every other story has closed, run `sh sources/run.sh` and `sh bin/test.sh`,
each of which must exit zero. Nothing under `sources/` is modified. Failures are fixed in the
owning module, never by editing the grader or its seed files.

The grader creates its own temporary SQLite database and runs `ledger init`, which empties the
database. The criterion therefore removes `DATABASE_URL` and `DATABASE_PATH` from the otherwise
inherited environment so the managed store is never touched by a child process.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC verification-full-suite ===
Intent: The supplied grader and the project's own test suite both exit zero when run from the application root against their own temporary databases.
Suite: full
Requires: executable=sh; scope=test

import os
import subprocess
import sys

env = {k: v for k, v in os.environ.items() if k not in ("DATABASE_URL", "DATABASE_PATH")}

grader = subprocess.run(["sh", "sources/run.sh"], capture_output=True, text=True, env=env)
print(grader.stdout)
print(grader.stderr, file=sys.stderr)
assert grader.returncode == 0

suite = subprocess.run(["sh", "bin/test.sh"], capture_output=True, text=True, env=env)
print(suite.stdout)
print(suite.stderr, file=sys.stderr)
assert suite.returncode == 0
=== END AC verification-full-suite ===

## User Acceptance

- None.

## Guardrails

- Do not modify, rewrite, regenerate, or substitute anything under `sources/`.
- Application code never reads `sources/run.sh` or any seed file.
- Child processes never receive the managed store's `DATABASE_URL` or `DATABASE_PATH`.
