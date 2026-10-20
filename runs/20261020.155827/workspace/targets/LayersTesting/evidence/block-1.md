# Evidence: Block 1 · Foundational (block-1)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 4218
- execution id: 20261020.160400.584Z-98e7f549

## Stories built
- Define the ledger architecture and application boundaries. (architecture) [story]

## Reusable compacts
- ARCHITECTURE_compact.md

## Stacked context
- implements: python.md (SP 761)
- compass: COMPASS.md (SP 747)
- implements: ARCHITECTURE.md (SP 833)
- stack: common.md (SP 1812)

## Build directory changes
- .env.example
- .gitignore
- bin/test.sh
- cli.py
- config.py
- ledger
- persistence/__init__.py
- persistence/db.py
- pyproject.toml
- reports.py
- services.py
- tests/test_architecture.py
- uv.lock
- validation.py

## Pre-build acceptance observation
- RED: architecture-boundaries (ARCHITECTURE.md)
  intent: The built application exposes the selected persistence and CLI foundation entry points.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "architecture-boundaries.py", line 4, in <module>
        assert Path("ledger").is_file()
               ^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: architecture-launcher (ARCHITECTURE.md)
  intent: The root launcher is executable and delegates to the CLI entry point.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      launcher = PosixPath('ledger')
    --- drydock: end values ---
    Traceback (most recent call last):
      File "architecture-launcher.py", line 5, in <module>
        assert launcher.is_file()
               ^^^^^^^^^^^^^^^^^^
    AssertionError

## Post-build programmatic acceptance
- PASS: architecture-boundaries (ARCHITECTURE.md)
  intent: The built application exposes the selected persistence and CLI foundation entry points.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: architecture-launcher (ARCHITECTURE.md)
  intent: The root launcher is executable and delegates to the CLI entry point.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
<reusable-compact filename="ARCHITECTURE.md">
Python CLI ledger with executable `ledger`; configuration precedence is `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`. CLI routing, validation, transactional services, reporting, and persistence are separate boundaries. All database access goes through `persistence.open_database`; amounts use integer cents; commands are atomic; reports query stored data.
</reusable-compact>

RESULT: SUCCESS

FILES CHANGED:
- .env.example
- .gitignore
- bin/test.sh
- cli.py
- config.py
- ledger
- persistence/__init__.py
- persistence/db.py
- pyproject.toml
- reports.py
- services.py
- tests/test_architecture.py
- uv.lock
- validation.py

SUMMARY:
Implemented the foundational Python CLI architecture, executable launcher, configuration precedence, transactional persistence boundary, validation, reporting, and deterministic tests. All 4 tests and declared architecture acceptance checks pass.

BLOCKERS:
- None
