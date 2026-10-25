# Evidence: Block 1 · Foundational (block-1)

- block type: block
- date: 2026-10-25
- resulting state: closed/verified
- story points (combined assembled cost): 7727
- execution id: 20261025.162723.417Z-93da8fe2

## Stories built
- Stand up the Python project tree, environment, pytest runner, and the `ledger` launcher at the application root. (foundation) [story]

## Stacked context
- implements: python.md (SP 1166)
- compass: COMPASS.md (SP 1156)
- implements: ARCHITECTURE.md (SP 2498)
- stack: common.md (SP 2776)

## Build directory changes
- .env.example
- .gitignore
- bin/test.sh
- ledger
- pyproject.toml
- tests/test_foundation.py
- uv.lock

## Pre-build acceptance observation
- RED: arch-launcher (ARCHITECTURE.md)
  intent: The ledger launcher exists at the application root, is executable, and starts with an interpreter line.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "arch-launcher.py", line 3, in <module>
        assert os.path.isfile("ledger")
               ^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: arch-project-manifest (ARCHITECTURE.md)
  intent: The project declares a Python requirement in pyproject.toml and commits a uv.lock.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "arch-project-manifest.py", line 7, in <module>
        assert os.path.isfile("uv.lock")
               ^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- GREEN (prepassed): arch-no-driver-imports (ARCHITECTURE.md)
  intent: No application file outside the persistence package imports a database driver.
  return code: 0

## Post-build programmatic acceptance
- PASS: arch-launcher (ARCHITECTURE.md)
  intent: The ledger launcher exists at the application root, is executable, and starts with an interpreter line.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: arch-project-manifest (ARCHITECTURE.md)
  intent: The project declares a Python requirement in pyproject.toml and commits a uv.lock.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: arch-no-driver-imports (ARCHITECTURE.md)
  intent: No application file outside the persistence package imports a database driver.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
The foundation files are partly present: `pyproject.toml` is committed but has no test runner, and there is no `uv.lock`, launcher, or `bin/`. I'll add pytest through `uv` (verifying the package name first) and then write the launcher and test script.pytest resolved and `uv.lock` was written. Now the launcher, the test launcher, ignore/env files, and a foundation test.Now I'll set the executable bits and run the declared acceptance checks plus the project test command.Two problems surfaced. First, `set -u` trips inside the venv `activate` script, which reads `OSTYPE` unguarded. Second, pytest found the parent `drydock/pyproject.toml` as its config and inherited its `--maxprocesses` addopt. I'll fix both by giving this project its own pytest config and relaxing `-u` only around `activate`.I left the `set` sequence around `activate` messy; I'll tidy it so only `-u` is relaxed while sourcing.The test suite passes (9/9) and the acceptance checks pass. The `ledger` launcher has the same `-u` issue with `activate`, so I'll apply the same fix there. The `No module named 'cli'` error is expected at this stage because `cli` is a later block.The foundation block is in place: the project tree, the `uv`-managed environment, the pytest runner, and the `ledger` launcher. The declared acceptance checks pass and `sh bin/test.sh` is green with 9 of 9 tests passing.

I did not commit anything. The changes are left in the working tree.

**What's in place**
- `pyproject.toml` declares `requires-python = ">=3.11"`, a `dev` group with `pytest>=9.1.1`, and a `[tool.pytest.ini_options]` block. I added that block so pytest does not pick up the parent `drydock/pyproject.toml` and inherit its `--maxprocesses` option, which had made the first run exit 4.
- `uv.lock` is committed. `.venv/` is created by `uv` and gitignored.
- `ledger` is a POSIX `sh` launcher at the application root. It activates `.venv`, puts the app root on `PYTHONPATH`, and runs `cli.main(sys.argv[1:])`, exiting with its return value. It has no business logic.
- `bin/test.sh` runs `pytest -q` from the project root, logs under `data/logs/` with `tee`, and returns pytest's exit status. It is POSIX `sh`, so I captured the status directly rather than through a pipe.
- `tests/test_foundation.py` has 9 tests. They read the manifest, lock, launcher, gitignore, and env example back from disk and check them.
- `.gitignore` and `.env.example` follow the stack conventions. The env example documents `DATABASE_URL` and `DATABASE_PATH`.

**Acceptance checks**
- `arch-launcher`, `arch-project-manifest`, and `arch-no-driver-imports` all pass when run with the spec's own assertions.

**Known gap for later blocks**
- `./ledger` currently exits 1 with `No module named 'cli'`. That is expected: the `cli` package belongs to a later block, and this step was limited to the foundation.

**Choices I made**
- I did not create `CLAUDE.md`, `Links.md`, or the lifecycle scripts (`start.sh`, `stop.sh`, `build.sh`, and so on). Those are generic stack conventions that don't fit a CLI project, so I left them out. Say if you want them added.
- I did not touch `persistence/`, because the architecture says it is generated by Drydock.
