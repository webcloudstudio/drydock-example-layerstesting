# FEATURE: Project Test Suite

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provides the project's automated pytest-based verification suite. |
| Depends On  | ARCHITECTURE.md, FEATURE-BALANCE-REPORT.md, FEATURE-CATEGORY-REPORT.md, FEATURE-MONTHLY-REPORT.md |
| Provides    | `bin/test.sh`, pytest project test suite |
| Consumes    | `./ledger executable`, ledger persistence operations |

## Purpose

The project test suite exercises the ledger against temporary databases and covers commands, exit codes, validation, atomicity, persistence, reports, and non-negative balance rules.

## Verification

`bin/test.sh` is POSIX-compatible, runs pytest from the application root, and returns success only when the complete suite passes.

## Programmatic Acceptance

=== AC project-test-suite ===
Intent: The project test runner completes successfully.

import subprocess

result = subprocess.run(
    ["sh", "bin/test.sh"],
    capture_output=True,
    text=True,
)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC project-test-suite ===

## User Acceptance

- None.

## Guardrails

- Tests use real temporary databases.
- The runner must fail when any automated test fails.
- The suite must not modify supplied scoring assets.
