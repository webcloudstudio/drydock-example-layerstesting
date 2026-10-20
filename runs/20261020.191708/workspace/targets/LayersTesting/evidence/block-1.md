# Evidence: Block 1 · Foundational (block-1)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 2736
- execution id: 20261020.192229.000Z-69c8fe37

## Stories built
- Define the ledger application boundaries and technical structure. (architecture) [story]

## Reusable compacts
- ARCHITECTURE_compact.md

## Stacked context
- implements: python.md (SP 761)
- compass: COMPASS.md (SP 755)
- implements: ARCHITECTURE.md (SP 918)
- context: TECHNOLOGY_STACK.md (SP 239)

## Build directory changes
- bin/test.sh
- cli.py
- configuration.py
- ledger
- persistence/__init__.py
- pyproject.toml
- reports.py
- services.py
- tests/test_architecture.py
- uv.lock
- validation.py

## Pre-build acceptance observation
- RED: architecture-imports (ARCHITECTURE.md)
  intent: The built application exposes the selected CLI and persistence foundation packages.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "architecture-imports.py", line 3, in <module>
        cli_module = import_module("cli")
                     ^^^^^^^^^^^^^^^^^^^^
      File "/home/barlo/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/importlib/__init__.py", line 90, in import_module
        return _bootstrap._gcd_import(name[level:], package, level)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
      File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
      File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
    ModuleNotFoundError: No module named 'cli'
- RED: architecture-cli-contract (ARCHITECTURE.md)
  intent: The CLI foundation exposes an in-process callable accepting an argument list.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.

## Post-build programmatic acceptance
- PASS: architecture-imports (ARCHITECTURE.md)
  intent: The built application exposes the selected CLI and persistence foundation packages.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: architecture-cli-contract (ARCHITECTURE.md)
  intent: The CLI foundation exposes an in-process callable accepting an argument list.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
<reusable-compact filename="ARCHITECTURE.md">
Expose `cli.main(argv)` and `persistence.open_database(dsn)`. Use boundaries for configuration, validation/services, persistence callers, reporting, and CLI dispatch. Resolve databases via `DATABASE_URL`, `DATABASE_PATH`, then `data/app.db`. Keep all monetary values as integer cents; application code must not access database drivers directly. CLI exit codes: 0 success, 1 operational failure, 2 usage error, 3 rejected input/invariant violation, 4 absent record.
</reusable-compact>

RESULT: SUCCESS

FILES CHANGED:
- pyproject.toml
- uv.lock
- cli.py
- configuration.py
- validation.py
- services.py
- reports.py
- persistence/__init__.py
- ledger
- bin/test.sh
- tests/test_architecture.py

SUMMARY:
Implemented the foundational Python architecture, CLI contract, configuration precedence, validation/service/report boundaries, persistence facade, executable launcher, and tests. `pytest`, `sh bin/test.sh`, and launcher checks pass.

BLOCKERS:
- None
