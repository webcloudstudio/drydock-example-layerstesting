# Evidence: Block 1 · Foundational (block-1)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 6721
- execution id: 20261020.042821.856Z-a6ec597e

## Stories built
- Create the Python project tree, environment, dependency manifest, and lockfile. (scaffold-python) [story]

## Reusable compacts
- ARCHITECTURE_compact.md

## Stacked context
- implements: python.md (SP 1166)
- compass: COMPASS.md (SP 1145)
- implements: ARCHITECTURE.md (SP 1526)
- stack: common.md (SP 2776)

## Build directory changes
- .gitignore
- docs/LAYOUT.md
- pyproject.toml
- tests/test_scaffold.py
- uv.lock

## Pre-build acceptance observation
- UNVERIFIED: scaffold-pyproject (ARCHITECTURE.md)
  intent: The project manifest declares Python 3.11 or newer, pytest, and psycopg.
  return code: 1
  error: unverified acceptance: the assertion raised FileNotFoundError ([Errno 2] No such file or directory: 'pyproject.toml') in its own frame, before reaching the code under test. This is a fault in the acceptance kit or its environment, not a defect in the build.
  stderr:
    Traceback (most recent call last):
      File "scaffold-pyproject.py", line 5, in <module>
        with open("pyproject.toml", "rb") as handle:
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    FileNotFoundError: [Errno 2] No such file or directory: 'pyproject.toml'
- RED: scaffold-environment (ARCHITECTURE.md)
  intent: The lockfile is committed and the virtual environment directory exists.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "scaffold-environment.py", line 3, in <module>
        assert os.path.isfile("uv.lock")
               ^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError

## Post-build programmatic acceptance
- UNVERIFIED: scaffold-pyproject (ARCHITECTURE.md)
  intent: The project manifest declares Python 3.11 or newer, pytest, and psycopg.
  provisioning: not required
  error: excluded check: ERROR environment
- PASS: scaffold-environment (ARCHITECTURE.md)
  intent: The lockfile is committed and the virtual environment directory exists.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
The build directory is essentially empty (only `sources/` and `.git`). I'll create the project with `uv`, which also verifies the package names against the index.`uv` reports this project as a member of a parent workspace at `drydock/`, which could put `uv.lock` and `.venv` outside the build directory. Checking where they landed.`uv` wrote into the Drydock repo root: it added this project as a workspace member in `drydock/pyproject.toml` and changed `drydock/uv.lock`. Both are outside the authorized build directory, so I need to inspect those diffs and revert them.The `uv.lock` diff is additive (110 insertions, no removals), so checking out the committed versions restores the original state. The `.claude/settings.local.json` untracked file predates my work and I'll leave it alone.The shared Drydock `.venv` was also touched: `uv` swapped `typing-extensions` 4.16.0 → 4.15.0 (pytest and psycopg were already present, so only that one package changed). I'll restore it to the original version. Now that the parent no longer declares the workspace member, the build directory should resolve as a standalone project.The build directory now has its own `uv.lock` and `.venv`, and the Drydock parent is back to its original state. Next I'll add the `.gitignore`, a scaffold test suite that reads back the manifest and environment, and a layout record. Then I'll run the declared checks.Now I'll run the declared acceptance checks (the two `scaffold-*` criteria) and the project test command.Both declared checks pass, and `pytest -q` is green with 5 tests. Final check that the Drydock parent repo is untouched:<reusable-compact filename="ARCHITECTURE.md">
Cash ledger: local single-user CLI. Executable `ledger` at app root; `./ledger <command>`.
Layout: `ledger` (cli dispatch), `cli/` (dispatch, CSV stdout, exit codes, usage errors), `amounts.py` (integer cents <-> two-decimal text), `config.py` (DATABASE_URL, then DATABASE_PATH, then data/app.db), `persistence/` (generated; the only place `sqlite3`/`psycopg` may be imported), `schema.sql` (generated DDL), `bin/test.sh` (POSIX runner with slice selector), `tests/` (pytest), `pyproject.toml` + `uv.lock` + `.venv/`.
Stack: Python >=3.11 (pytest); SQLite default; PostgreSQL when DSN is postgres:// or postgresql:// (psycopg[binary]); network only to the PostgreSQL server named by DATABASE_URL.
Decisions: money as integer cents, no floats; each command = one DB transaction via `open_database(dsn)`; manifest declares >=3.11, pytest, psycopg[binary]; uv.lock committed.
Acceptance: `scaffold-pyproject` (requires-python >=3.11; pytest and psycopg present), `scaffold-environment` (uv.lock, .venv, pyproject.toml exist).
</reusable-compact>

RESULT: SUCCESS

FILES CHANGED:
- pyproject.toml
- uv.lock
- .gitignore
- tests/test_scaffold.py
- docs/LAYOUT.md

SUMMARY:
- **Manifest:** `pyproject.toml` declares `requires-python = ">=3.11"` with `pytest` and `psycopg[binary]`. `uv add` resolved both names against the package index, so they were verified and not invented.
- **Lockfile and environment:** `uv.lock` is committed in the build directory. `.venv/` was created with `uv venv` (Python 3.11) and synced from the lock. It is gitignored.
- **Tests:** `tests/test_scaffold.py` has 5 tests. Each reads the manifest, lockfile, or environment back from disk and compares it to the expected value. `uv run pytest -q` exits 0 with 5 passed.
- **Acceptance checks:** I ran both declared `scaffold-*` criteria by hand. `scaffold-pyproject` and `scaffold-environment` both pass.
- **Layout record:** `docs/LAYOUT.md` records the Technology Stack and the package layout, including the later-block packages, so later stories add to it without replacing these contracts.
- **Ignore rules:** `.gitignore` follows the common.md hygiene rules and ignores `.venv/`, `data/`, `__pycache__/`, and similar.
- **Suite runs:** I ran only the project's own `pytest` suite. No staged authoritative suite is in scope for this step, so `sources/run.sh` was not run. Coverage this step: 5 passed, 0 failed.

Incident during the build: my first `uv add` ran inside a parent workspace. It added a `[tool.uv.workspace]` entry to the Drydock root `pyproject.toml` and appended to the root `uv.lock`. It also swapped `typing-extensions` 4.16.0 → 4.15.0 in the shared `drydock/.venv`. I reverted both root files with `git checkout` (the root repo is now clean apart from a pre-existing untracked `.claude/settings.local.json`) and restored `typing-extensions` to 4.16.0. Those files are outside the authorized directories, so no further changes will be made there. Nothing was committed, and no git history was changed.

<reusable-compact filename="ARCHITECTURE.md">
Cash ledger: local single-user CLI. Executable `ledger` at app root; `./ledger <command>`.
Layout: `ledger` (cli dispatch), `cli/` (dispatch, CSV stdout, exit codes, usage errors), `amounts.py` (integer cents <-> two-decimal text), `config.py` (DATABASE_URL, then DATABASE_PATH, then data/app.db), `persistence/` (generated; the only place `sqlite3`/`psycopg` may be imported), `schema.sql` (generated DDL), `bin/test.sh` (POSIX runner with slice selector), `tests/` (pytest), `pyproject.toml` + `uv.lock` + `.venv/`.
Stack: Python >=3.11 (pytest); SQLite default; PostgreSQL when DSN is postgres:// or postgresql:// (psycopg[binary]); network only to the PostgreSQL server named by DATABASE_URL.
Decisions: money as integer cents, no floats; each command = one DB transaction via `open_database(dsn)`; manifest declares >=3.11, pytest, psycopg[binary]; uv.lock committed.
Acceptance: `scaffold-pyproject` (requires-python >=3.11; pytest and psycopg present), `scaffold-environment` (uv.lock, .venv, pyproject.toml exist).
</reusable-compact>
