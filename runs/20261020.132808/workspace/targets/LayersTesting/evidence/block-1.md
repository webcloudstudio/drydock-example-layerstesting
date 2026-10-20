# Evidence: Block 1 · Foundational (block-1)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 6860
- execution id: 20261020.134803.253Z-0227f27d

## Stories built
- Stand up the Python project root, environment, dependency manifest, and launchers. (python-foundation) [story]

## Stacked context
- implements: python.md (SP 1166)
- compass: COMPASS.md (SP 1145)
- implements: ARCHITECTURE.md (SP 1663)
- stack: common.md (SP 2776)

## Build directory changes
- .gitignore
- ARCHITECTURE.md
- bin/lint.sh
- bin/test.sh
- data/logs/lint_2026-10-20_094923.log
- data/logs/lint_2026-10-20_094929.log
- data/logs/lint_2026-10-20_094930.log
- data/logs/test_2026-10-20_094915.log
- data/logs/test_2026-10-20_094928.log
- pyproject.toml
- tests/test_foundation.py
- uv.lock

## Pre-build acceptance observation
- GREEN (prepassed): arch-python-version (ARCHITECTURE.md)
  intent: The running interpreter is Python 3.11 or newer, as the Technology Stack requires.
  return code: 0
- UNVERIFIED: arch-pyproject (ARCHITECTURE.md)
  intent: pyproject.toml exists at the project root and parses as TOML with a project table.
  return code: 1
  error: unverified acceptance: the assertion raised FileNotFoundError ([Errno 2] No such file or directory: 'pyproject.toml') in its own frame, before reaching the code under test. This is a fault in the acceptance kit or its environment, not a defect in the build.
  stderr:
    Traceback (most recent call last):
      File "arch-pyproject.py", line 3, in <module>
        with open("pyproject.toml", "rb") as handle:
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    FileNotFoundError: [Errno 2] No such file or directory: 'pyproject.toml'
- RED: arch-uv-lock (ARCHITECTURE.md)
  intent: uv.lock is committed at the project root beside pyproject.toml.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "arch-uv-lock.py", line 3, in <module>
        assert Path("uv.lock").is_file()
               ^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError

## Post-build programmatic acceptance
- PASS: arch-python-version (ARCHITECTURE.md)
  intent: The running interpreter is Python 3.11 or newer, as the Technology Stack requires.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.132808/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: arch-pyproject (ARCHITECTURE.md)
  intent: pyproject.toml exists at the project root and parses as TOML with a project table.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.132808/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: arch-uv-lock (ARCHITECTURE.md)
  intent: uv.lock is committed at the project root beside pyproject.toml.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.132808/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
The build directory holds only `sources/` and `.git`, so this step creates the project root from scratch. I'll check the tooling first.Plan for this block: `pyproject.toml` declaring Python ≥3.11 with pytest and ruff, `uv.lock` via `uv`, `.venv` via `uv venv`, `bin/` launchers that activate `.venv`, a test suite that `pytest -q` can run, and a `.gitignore`. I'll write the manifest, then let `uv` resolve the dev dependencies so the package names are checked against the registry.`uv` resolved pytest and ruff from the registry and wrote `uv.lock`; the `pyproject.toml` change is only uv normalizing the dev group. Now the launchers, `.gitignore`, the test suite, and the architecture record.All 15 tests pass and `bin/test.sh` exits 0. The `OSTYPE` line is noise from sourcing `activate` under `set -u`, so I'll replace the `activate` source with an explicit PATH prefix in both launchers.Both launchers pass cleanly. Next, the architecture record, then the three declared acceptance checks run from the project root.The Python project foundation is in place in the build directory. `bin/test.sh` exits 0 with 15 passing tests, and the three declared acceptance checks pass.

- **Manifest and environment:** `pyproject.toml` requires Python ≥3.11 and declares pytest and ruff in the dev group. `uv add` resolved both from the registry and wrote `uv.lock`. `.venv` was created with `uv venv` on the managed Python 3.12.
- **Launchers:** `bin/test.sh` runs `pytest -q` and `bin/lint.sh` runs `ruff check .`. Both are POSIX sh, use the CommandCenter header and tee logging to `data/logs/`, and put `.venv/bin` on `PATH` without sourcing `activate`. `bin/lint.sh` also exits 0.
- **Tests:** `tests/test_foundation.py` covers the manifest, the lock file, the venv interpreter's version, the launchers, and `.gitignore`. Each test reads state back from the file or runs the process and parses its output. It does not match on captured text.
- **Ignore file:** `.gitignore` excludes `.venv/`, `data/`, `.env`, caches, and build artifacts.

Choices I made that you may want to change:
- `ARCHITECTURE.md` is written at the build root, not in the Target's `blueprint/` directory, which is protected. It contains the Technology Stack and module ownership sections, plus the module responsibilities table.
- The `.gitignore` and the two launchers follow `stack/common.md`. I did not add `CLAUDE.md` or `Links.md`, since neither is part of this story.

Also, `python.md` says both SQLite and PostgreSQL ship, but the Blueprint `ARCHITECTURE.md` says this build has no PostgreSQL backend. I followed the Blueprint and recorded that in `ARCHITECTURE.md`. The conflict doesn't affect this step, but it will matter for the persistence block.

I did not run `git add` or `git commit`.

RESULT: SUCCESS

FILES CHANGED:
- .gitignore
- ARCHITECTURE.md
- bin/lint.sh
- bin/test.sh
- pyproject.toml
- tests/test_foundation.py
- uv.lock

SUMMARY:
Created the `ledger` project root with a Python ≥3.11 `pyproject.toml`, a committed `uv.lock` resolved through `uv` (pytest 9.1.1, ruff 0.17.1), and a `.venv` created with `uv venv`. Added POSIX sh launchers `bin/test.sh` (`pytest -q`) and `bin/lint.sh` (`ruff check .`) that put `.venv/bin` on PATH. Added `tests/test_foundation.py` (15 tests) and `.gitignore`. Recorded the Technology Stack and module ownership in `ARCHITECTURE.md` at the build root. Verification: `sh bin/test.sh` exit 0 (15 passed); `sh bin/lint.sh` exit 0; acceptance checks arch-python-version, arch-pyproject, and arch-uv-lock all pass.

<blueprint-decisions>
[{"spec":"ARCHITECTURE.md","severity":"Low","subject":"Location of the recorded architecture sections","decision":"The Blueprint copy under blueprint/ is a protected Drydock artifact, so I wrote the Technology Stack and Module Ownership sections to ARCHITECTURE.md at the build root instead. Is that acceptable, or should it live elsewhere on replan?"}]
</blueprint-decisions>

FAILURE_SUMMARY: not applicable (step succeeded)
