# FEATURE: Test Runner

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | `bin/test.sh` runs the project suite against a temporary database and accepts an optional slice selector. |
| Depends On  | ARCHITECTURE.md |
| Provides    | `sh bin/test.sh [SLICE]` |

## Purpose

`bin/test.sh` is the single entry point for the project's automated tests. Story-level builds run
a slice of the suite. The terminal story runs the whole suite.

## Behavior

- `sh bin/test.sh` runs `pytest -q` from the application root with no selector.
- `sh bin/test.sh SLICE` passes `SLICE` to pytest as a `-k` expression, narrowing the run to the
  matching tests.
- Before running pytest, the script exports `DATABASE_URL` pointing at a fresh temporary SQLite
  file, so tests never touch the user's database.
- The script exits `0` only when every selected test passes, and a nonzero status otherwise.
- The script uses the interpreter in `.venv` when it exists.
- The script is POSIX `sh`.

## Programmatic Acceptance

=== AC test-runner-syntax ===
Intent: The test runner is valid POSIX shell syntax.

import subprocess

result = subprocess.run(["sh", "-n", "bin/test.sh"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC test-runner-syntax ===

=== AC test-runner-selector ===
Intent: The slice selector runs only the matching tests and reports their result in the exit status.

import os
import subprocess

probes = {
    "tests/test_ac_probe_pass.py": "def test_probe_pass():\n    assert True\n",
    "tests/test_ac_probe_fail.py": "def test_probe_fail():\n    assert False\n",
}
os.makedirs("tests", exist_ok=True)
try:
    for path, source in probes.items():
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(source)
    passing = subprocess.run(["sh", "bin/test.sh", "probe_pass"], capture_output=True, text=True)
    failing = subprocess.run(["sh", "bin/test.sh", "probe_fail"], capture_output=True, text=True)
finally:
    for path in probes:
        if os.path.exists(path):
            os.remove(path)
print(passing.stdout)
print(passing.stderr)
print(failing.stdout)
print(failing.stderr)
assert passing.returncode == 0
assert failing.returncode != 0
=== END AC test-runner-selector ===

## User Acceptance

- None.

## Guardrails

- `bin/test.sh` uses POSIX `sh` only. No bash-only constructs.
- `bin/test.sh` never points the suite at a database the user configured. It always exports a
  fresh temporary `DATABASE_URL` first.
