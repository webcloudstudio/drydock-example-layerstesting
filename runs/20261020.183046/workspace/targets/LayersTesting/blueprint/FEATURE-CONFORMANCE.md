# FEATURE: Conformance Verification

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provide the project test entry point and execute the complete supplied ledger conformance suite. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-ACCOUNT-LIFECYCLE.md, FEATURE-AGGREGATE-REPORTS.md, FEATURE-BALANCE-REPORTS.md, FEATURE-BULK-LOADING.md, FEATURE-CLI-FOUNDATION.md, FEATURE-FINANCIAL-INVARIANTS.md, FEATURE-SCHEMA-LIFECYCLE.md, FEATURE-TRANSACTION-LIFECYCLE.md, FEATURE-TRANSFERS.md |
| Provides    | bin/test.sh, complete supplied conformance verification |
| Consumes    | ./ledger, accounts repository, categories repository, transactions repository |

## Purpose

The project provides a POSIX-compatible `bin/test.sh` that runs the committed pytest suite from the application root. The terminal verification also runs `sh sources/run.sh` without filtering or reinterpretation. The supplied grader and seed files remain unchanged.

## Test Harness

- `bin/test.sh` runs `pytest -q` and exits zero only when the project test suite passes.
- `sources/run.sh` is the authoritative full conformance gate.
- The conformance run uses a fresh database and validates initialization, loading, reports, lifecycle operations, transfers, atomic rejection, balance invariants, and usage errors.
- Diagnostics from the harness are available for repair, while the harness exit status is the acceptance verdict.

## Programmatic Acceptance

Requires: executable=sh; scope=test

=== AC conformance-test-entrypoint ===
Intent: The project test entry point exists, is executable, and exits successfully.
Requires: executable=sh; scope=test

import os
import subprocess

test_script = os.path.join(os.getcwd(), "bin", "test.sh")
assert os.path.isfile(test_script)
assert os.access(test_script, os.X_OK)

result = subprocess.run(
    ["sh", "bin/test.sh"],
    capture_output=True,
    text=True,
)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC conformance-test-entrypoint ===

=== AC conformance-full-suite ===
Intent: The terminal story passes the complete supplied ledger conformance suite without filtering.
Suite: full
Requires: executable=sh; scope=test

import subprocess

result = subprocess.run(
    ["sh", "sources/run.sh"],
    capture_output=True,
    text=True,
)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC conformance-full-suite ===

## User Acceptance

- None.

## Guardrails

- Do not modify, rewrite, regenerate, or substitute any file under `sources/`.
- Do not filter, skip, or reinterpret the supplied conformance suite.
- Application code must not read the grader or seed files.
- The complete supplied suite is run only as the terminal project verification.
