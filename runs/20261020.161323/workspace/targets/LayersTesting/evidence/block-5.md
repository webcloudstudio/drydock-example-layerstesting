# Evidence: Block 5 · Service (block-5)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 8190
- execution id: 20261020.162649.393Z-b6d27a68

## Stories built
- Load account and category CSV files atomically. (load-001) [story]

## Reusable compacts
- seed_accounts_compact.md
- seed_categories_compact.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: FEATURE-Bulk-Reference-Loading.md (SP 935)
- context: seed_accounts.csv (SP 22)
- context: seed_categories.csv (SP 40)
- context: ARCHITECTURE_compact.md (SP 203)
- context: DATABASE_compact.md (SP 197)
- stack: common.md (SP 1812)
- stack: sqlite.md (SP 1818)
- stack: cli.md (SP 1755)

## Build directory changes
- cli/__init__.py
- data/app.db
- persistence/__init__.py
- persistence/schema.py
- services.py
- tests/test_bulk_loading.py
- tests/test_persistence_boundary.py

## Pre-build acceptance observation
- RED: reference-load-accounts (FEATURE-Bulk-Reference-Loading.md)
  intent: The account fixture loads through the public command and reports a successful result.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "reference-load-accounts.py", line 9, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: reference-load-categories (FEATURE-Bulk-Reference-Loading.md)
  intent: The category fixture loads through the public command and produces seven persisted categories.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "reference-load-categories.py", line 9, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: reference-load-rejects-duplicate (FEATURE-Bulk-Reference-Loading.md)
  intent: A duplicate reference load is rejected without changing the existing account count.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      first_code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "reference-load-rejects-duplicate.py", line 9, in <module>
        assert first_code == 0
               ^^^^^^^^^^^^^^^
    AssertionError
- RED: reference-load-header-validation (FEATURE-Bulk-Reference-Loading.md)
  intent: A missing or unreadable reference file is rejected without standard output.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
      expected_code = 1
    --- drydock: end values ---
    Traceback (most recent call last):
      File "reference-load-header-validation.py", line 5, in <module>
        assert code == expected_code
               ^^^^^^^^^^^^^^^^^^^^^
    AssertionError

## Post-build programmatic acceptance
- PASS: reference-load-accounts (FEATURE-Bulk-Reference-Loading.md)
  intent: The account fixture loads through the public command and reports a successful result.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: reference-load-categories (FEATURE-Bulk-Reference-Loading.md)
  intent: The category fixture loads through the public command and produces seven persisted categories.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: reference-load-rejects-duplicate (FEATURE-Bulk-Reference-Loading.md)
  intent: A duplicate reference load is rejected without changing the existing account count.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: reference-load-header-validation (FEATURE-Bulk-Reference-Loading.md)
  intent: A missing or unreadable reference file is rejected without standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
<reusable-compact filename="seed_accounts.csv">
CSV header: `account,name`. Seed accounts: DRAWER1 (Front Drawer), DRAWER2 (Back Drawer), PETTY (Petty Cash), SAFE (Store Safe).
</reusable-compact>

<reusable-compact filename="seed_categories.csv">
CSV header: `category,description`. Seed categories: OPENING, PAYROLL, REFUND, RENT, SALES, SUPPLY, TRANSFER.
</reusable-compact>

RESULT: SUCCESS

FILES CHANGED:
- cli/__init__.py
- services.py
- persistence/schema.py
- persistence/__init__.py
- tests/test_persistence_boundary.py
- tests/test_bulk_loading.py

SUMMARY:
Implemented atomic account/category CSV validation and loading, required output, duplicate rejection, error handling, and tests. Block tests: 15 passed. Full harness remains incomplete for other build blocks: 13/43 passed.

BLOCKERS:
- None for this build block.
