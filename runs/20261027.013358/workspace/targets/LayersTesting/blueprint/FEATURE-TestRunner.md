# FEATURE: Test Runner

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | The POSIX `bin/test.sh` runner for the application's own pytest suite. |
| Depends On | ARCHITECTURE.md |
| Provides | bin/test.sh |
| Consumes | python-project |

## Purpose

Give the application one command that runs its automated tests from the application root and exits
zero only when every test passes. This is the verification command for every behavioral story.

## Interface

`sh bin/test.sh`:

- changes to the application root regardless of the caller's directory;
- activates `.venv` when it exists;
- runs `pytest -q`;
- exits with pytest's exit status, so it is zero only when every test passes.

The script uses POSIX sh only. No test may itself invoke `bin/test.sh`. At least one meaningful
project test exists under `tests/` so the runner has something to run.

## Database Interface

- None — this feature reaches no repository.

## Programmatic Acceptance

=== AC runner-script-exists ===
Intent: The runner script exists at bin/test.sh and invokes pytest.

from pathlib import Path

script = Path("bin/test.sh")
assert script.is_file()
text = script.read_text()
assert "pytest" in text
=== END AC runner-script-exists ===

=== AC runner-posix-syntax ===
Intent: The runner parses under a POSIX shell without syntax errors.

import subprocess

result = subprocess.run(["sh", "-n", "bin/test.sh"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC runner-posix-syntax ===

=== AC runner-has-tests ===
Intent: The tests directory contains at least one test module for the runner to collect.

from pathlib import Path

modules = sorted(Path("tests").glob("test_*.py"))
print([str(m) for m in modules])
assert len(modules) >= 1
=== END AC runner-has-tests ===

## User Acceptance

- None.

## Guardrails

- The script is POSIX sh, not bash.
- No test invokes `bin/test.sh`.
