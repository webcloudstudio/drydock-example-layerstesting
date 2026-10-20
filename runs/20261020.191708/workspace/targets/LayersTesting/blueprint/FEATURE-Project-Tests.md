# FEATURE: Project Test Suite

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provide the automated project test runner and comprehensive ledger test suite. |
| Depends On  | FEATURE-CLI-Validation.md, FEATURE-Account-Management.md, FEATURE-Transaction-Management.md, FEATURE-Transfers.md, FEATURE-Report-Balances.md, FEATURE-Report-Categories.md, FEATURE-Report-Monthly.md |
| Provides    | bin/test.sh, pytest suite |
| Consumes    | ledger command surface |

## Purpose

Provide a POSIX-compatible `bin/test.sh` that runs the complete pytest suite from the application root and returns success only when every project test passes.

## Test Scope

The suite covers:

- command dispatch and usage errors;
- database initialization and configuration;
- account and category loading;
- transaction loading and atomic rejection;
- account and transaction CRUD;
- balance invariants and atomic transfers;
- balance, category, and monthly reports;
- validation boundaries and all documented exit codes.

The suite uses temporary databases and does not modify supplied sources.

## Programmatic Acceptance

=== AC project-test-runner ===
Intent: The project test runner exists, is executable, and passes the automated suite.
import os
import subprocess

runner = "bin/test.sh"
assert os.path.isfile(runner)
assert os.access(runner, os.X_OK)

result = subprocess.run(["sh", runner], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0

=== END AC project-test-runner ===

=== AC project-test-runner-is-repeatable ===
Intent: Running the project test runner twice succeeds independently.
import subprocess

first = subprocess.run(["sh", "bin/test.sh"], capture_output=True, text=True)
print(first.stdout)
print(first.stderr)
assert first.returncode == 0

second = subprocess.run(["sh", "bin/test.sh"], capture_output=True, text=True)
print(second.stdout)
print(second.stderr)
assert second.returncode == 0

=== END AC project-test-runner-is-repeatable ===

=== AC project-test-surface ===
Intent: The project suite exercises the executable ledger command surface.
from cli.testing import cli_runner
import os
import tempfile

with tempfile.TemporaryDirectory() as directory:
    os.environ["DATABASE_URL"] = os.path.join(directory, "ledger.db")
    assert cli_runner("init")[0] == 0
    assert cli_runner("count")[0] == 0
    assert cli_runner("report", "balances")[0] == 0
    assert cli_runner("report", "categories")[0] == 0
    assert cli_runner("report", "monthly")[0] == 0

=== END AC project-test-surface ===

## User Acceptance

- None.

## Guardrails

- `bin/test.sh` is POSIX-compatible.
- The runner exits zero only when every automated test passes.
- Tests use real temporary databases and preserve supplied source files.
