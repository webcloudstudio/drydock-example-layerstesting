# Evidence: Block 1 · Foundational (block-1)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 2499
- execution id: 20261020.184023.438Z-f4b70418

## Stories built
- Define the ledger application architecture and module boundaries. (architecture) [story]

## Reusable compacts
- ARCHITECTURE_compact.md

## Stacked context
- implements: python.md (SP 761)
- compass: COMPASS.md (SP 755)
- implements: ARCHITECTURE.md (SP 936)

## Build directory changes
- .env.example
- cli.py
- ledger
- ledger_app/__init__.py
- ledger_app/config.py
- ledger_app/errors.py
- ledger_app/services.py
- pyproject.toml
- tests/test_architecture.py
- uv.lock

## Pre-build acceptance observation
- RED: architecture-config-precedence (ARCHITECTURE.md)
  intent: The configuration boundary exposes the documented database-source precedence.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "architecture-config-precedence.py", line 2, in <module>
        from ledger_app.config import database_dsn
    ModuleNotFoundError: No module named 'ledger_app'
- RED: architecture-error-boundary (ARCHITECTURE.md)
  intent: The application exposes distinct typed outcomes for usage, rejection, and not-found failures.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "architecture-error-boundary.py", line 1, in <module>
        from ledger_app.errors import NotFoundError, RejectedError, UsageError
    ModuleNotFoundError: No module named 'ledger_app'

## Post-build programmatic acceptance
- PASS: architecture-config-precedence (ARCHITECTURE.md)
  intent: The configuration boundary exposes the documented database-source precedence.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: architecture-error-boundary (ARCHITECTURE.md)
  intent: The application exposes distinct typed outcomes for usage, rejection, and not-found failures.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
<reusable-compact filename="ARCHITECTURE.md">
Python ledger layers: executable `ledger`; `cli` for parsing, dispatch, and exit mapping; `ledger_app.config` for `DATABASE_URL` → `DATABASE_PATH` → `data/app.db`; `ledger_app.services` for workflows and business rules; shipped `persistence` for all database access. Exit codes: 0 success, 1 operational failure, 2 usage error, 3 rejection, 4 not found. Application code must not import database drivers or read `sources/`. Amounts use integer cents.
</reusable-compact>

RESULT: SUCCESS

FILES CHANGED:
- ledger_app/__init__.py
- ledger_app/config.py
- ledger_app/errors.py
- ledger_app/services.py
- cli.py
- ledger
- pyproject.toml
- uv.lock
- .env.example
- tests/test_architecture.py

SUMMARY:
Implemented the layered Python architecture, configuration precedence, typed error boundaries, CLI entry point, service dispatch boundary, executable launcher, tests, and lockfile. Declared acceptance assertions pass; project tests: 2 passed.

BLOCKERS:
- None
