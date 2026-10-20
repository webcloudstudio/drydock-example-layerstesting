# FEATURE: Test Runner

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provides the project's automated pytest suite and POSIX test runner. |
| Depends On  | ARCHITECTURE.md, FEATURE-Balance-Reports.md, FEATURE-Category-Reports.md, FEATURE-Monthly-Reports.md |
| Provides    | bin/test.sh, pytest test suite |
| Consumes    | all ledger command capabilities |

## Purpose

The project test runner executes the automated Python test suite from the application root and returns success only when all tests pass.

## Programmatic Acceptance

=== AC test-runner-exists-and-passes ===
Intent: The project provides an executable POSIX test runner whose complete suite passes.

from pathlib import Path
import os
import subprocess

runner = Path("bin/test.sh")
assert runner.is_file()
assert os.access(runner, os.X_OK)

result = subprocess.run(["sh", "bin/test.sh"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC test-runner-exists-and-passes ===

=== AC pytest-suite-is-present ===
Intent: The automated test suite contains at least one runnable pytest test module.

from pathlib import Path

test_files = list(Path("tests").glob("test_*.py"))
assert test_files
=== END AC pytest-suite-is-present ===

## User Acceptance

- None.

## Guardrails

- `bin/test.sh` must be POSIX-compatible and run from the application root.
- The suite must exercise the real temporary database and cover commands, exit codes, validation, atomicity, persistence, balances, and reports.
- The runner must return nonzero when a test fails.
