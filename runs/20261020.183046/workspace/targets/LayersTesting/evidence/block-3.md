# Evidence: Block 3 · Service (block-3)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 6413
- execution id: 20261020.184310.662Z-40f20f68

## Stories built
- Initialize and inspect the ledger database schema. (schema-lifecycle) [story]

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: FEATURE-SCHEMA-LIFECYCLE.md (SP 968)
- context: ARCHITECTURE_compact.md (SP 152)
- context: DATABASE_compact.md (SP 326)
- stack: cli.md (SP 1755)
- stack: sqlite.md (SP 1818)

## Build directory changes
- cli/__init__.py
- data/app.db
- ledger_app/services.py
- tests/test_schema_lifecycle.py

## Pre-build acceptance observation
- RED: schema-init-empty (FEATURE-SCHEMA-LIFECYCLE.md)
  intent: Initialization leaves all three declared tables empty and count reports their state.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      rows = []
    --- drydock: end values ---
    Traceback (most recent call last):
      File "schema-init-empty.py", line 18, in <module>
        assert len(rows) == 4
               ^^^^^^^^^^^^^^
    AssertionError
- RED: schema-reinitializes (FEATURE-SCHEMA-LIFECYCLE.md)
  intent: A second initialization removes previously stored rows.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      rows = []
    --- drydock: end values ---
    Traceback (most recent call last):
      File "schema-reinitializes.py", line 18, in <module>
        assert len(rows) == 4
               ^^^^^^^^^^^^^^
    AssertionError
- RED: schema-count-order (FEATURE-SCHEMA-LIFECYCLE.md)
  intent: Count exposes exactly one row for each required table in the documented order.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      rows = []
    --- drydock: end values ---
    Traceback (most recent call last):
      File "schema-count-order.py", line 15, in <module>
        assert [row[0] for row in rows[1:]] == ["accounts", "categories", "transactions"]
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError

## Post-build programmatic acceptance
- PASS: schema-init-empty (FEATURE-SCHEMA-LIFECYCLE.md)
  intent: Initialization leaves all three declared tables empty and count reports their state.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: schema-reinitializes (FEATURE-SCHEMA-LIFECYCLE.md)
  intent: A second initialization removes previously stored rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: schema-count-order (FEATURE-SCHEMA-LIFECYCLE.md)
  intent: Count exposes exactly one row for each required table in the documented order.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
RESULT: SUCCESS

FILES CHANGED:
- ledger_app/services.py
- cli/__init__.py
- tests/test_schema_lifecycle.py

SUMMARY:
Implemented atomic schema reset and ordered row counting. Project tests: 11 passed. Schema lifecycle acceptance: 3 passed. Full harness: 6 passed, 37 later-block checks failed.

BLOCKERS:
- Later build blocks remain unimplemented.
