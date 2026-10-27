# FEATURE: Release Verification

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Terminal gate that runs the supplied end-to-end grader unfiltered and the application test runner, requiring exit zero from both. |
| Depends On | FEATURE-UsageErrors.md, FEATURE-OperationalFailures.md, FEATURE-TestRunner.md |
| Provides | release-verification |
| Consumes | ledger, test-runner-contract |

## Purpose

This is the terminal story. Every command story has closed before it runs. It proves the assembled
ledger passes all 43 supplied checks in `sources/run.sh` and that the application's own suite passes
through `bin/test.sh`. Application code never reads `sources/run.sh` or any seed file.

## Assembly and Intent

- Run `sh sources/run.sh` from the application root, unfiltered; exit status is the verdict.
- The grader chooses its own temporary database when `DATABASE_URL` is unset, so the child process
  is run without `DATABASE_URL` and `DATABASE_PATH`; this protects the configured store from `init`.
- Run `sh bin/test.sh` and require exit zero.
- Do not modify, regenerate, or substitute any file under `sources/`.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC verify-grader-full ===
Intent: The supplied grader sh sources/run.sh passes every check, so the runner exits zero.
Suite: full
Requires: executable=sh; scope=test

import os
import subprocess
import sys

env = {k: v for k, v in os.environ.items() if k not in ("DATABASE_URL", "DATABASE_PATH")}
result = subprocess.run(
    ["sh", "sources/run.sh"],
    capture_output=True,
    text=True,
    env=env,
)
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == 0
=== END AC verify-grader-full ===

=== AC verify-application-tests ===
Intent: The application's own test runner bin/test.sh exits zero only when every application test passes.
Requires: executable=sh; scope=test

import os
import subprocess
import sys

env = {k: v for k, v in os.environ.items() if k not in ("DATABASE_URL", "DATABASE_PATH")}
result = subprocess.run(
    ["sh", "bin/test.sh"],
    capture_output=True,
    text=True,
    env=env,
)
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == 0
=== END AC verify-application-tests ===

=== AC verify-ledger-executable ===
Intent: The ledger executable exists at the application root and rejects an unknown command with the usage exit status.
Requires: executable=sh; scope=test

import os
import subprocess
import sys

assert os.path.isfile("ledger")
assert os.access("ledger", os.X_OK)
env = {k: v for k, v in os.environ.items() if k not in ("DATABASE_URL", "DATABASE_PATH")}
result = subprocess.run(
    ["./ledger", "frobnicate"],
    capture_output=True,
    text=True,
    env=env,
)
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == 2
assert result.stdout == ""
=== END AC verify-ledger-executable ===

## User Acceptance

- None.

## Guardrails

- Do not modify, rewrite, regenerate, or substitute any file under `sources/`.
- Application code never reads `sources/run.sh` or any seed file; seed files reach the database only through `ledger load`.
- No report row, count, or total is hardcoded; every value comes from a query.
- Only the terminal story runs the whole grader.
