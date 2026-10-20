# Evidence: Block 4 · Service (block-4)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 6922
- execution id: 20261020.184602.647Z-eb37fd22

## Stories built
- Load validated account, category, and transaction CSV files atomically. (bulk-loading) [story]

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: FEATURE-BULK-LOADING.md (SP 1460)
- context: ARCHITECTURE_compact.md (SP 152)
- context: DATABASE_compact.md (SP 326)
- stack: cli.md (SP 1755)
- stack: sqlite.md (SP 1818)

## Build directory changes
- data/app.db
- ledger_app/services.py
- persistence/schema.py
- tests/test_bulk_loading.py

## Pre-build acceptance observation
- RED: bulk-load-valid-accounts (FEATURE-BULK-LOADING.md)
  intent: A valid account CSV loads successfully and reports the supplied row count.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      loaded = []
      rows = [['account', 'name'], ['A1', 'Main'], ['A2', 'Reserve']]
    --- drydock: end values ---
    Traceback (most recent call last):
      File "bulk-load-valid-accounts.py", line 19, in <module>
        assert loaded[-1][1] == str(len(rows) - 1)
               ~~~~~~^^^^
    IndexError: list index out of range
- RED: bulk-load-invalid-row-is-atomic (FEATURE-BULK-LOADING.md)
  intent: A malformed row rejects the complete account file without storing earlier valid rows.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 0
    --- drydock: end values ---
    Traceback (most recent call last):
      File "bulk-load-invalid-row-is-atomic.py", line 17, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: bulk-load-unknown-reference-is-atomic (FEATURE-BULK-LOADING.md)
  intent: A transaction file with an unknown account is rejected before any transaction is written.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 0
    --- drydock: end values ---
    Traceback (most recent call last):
      File "bulk-load-unknown-reference-is-atomic.py", line 28, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError

## Post-build programmatic acceptance
- PASS: bulk-load-valid-accounts (FEATURE-BULK-LOADING.md)
  intent: A valid account CSV loads successfully and reports the supplied row count.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: bulk-load-invalid-row-is-atomic (FEATURE-BULK-LOADING.md)
  intent: A malformed row rejects the complete account file without storing earlier valid rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: bulk-load-unknown-reference-is-atomic (FEATURE-BULK-LOADING.md)
  intent: A transaction file with an unknown account is rejected before any transaction is written.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Repair attempts
- attempt 0 (initial build): failed; 2/3 checks model=gpt-5.6-luna; execution 20261020.184435.996Z-62d4872c; reason: programmatic acceptance failed: bulk-load-unknown-reference-is-atomic
- attempt 1 (repair 1): built; 3/3 checks model=gpt-5.6-luna; execution 20261020.184602.647Z-eb37fd22

## Build summary
<blueprint-decisions>
[{"spec":"FEATURE-BULK-LOADING.md","severity":"Material","subject":"Category creation access","decision":"Added the missing generated categories.create operation required by the specified category loader."}]
</blueprint-decisions>

RESULT: SUCCESS

FILES CHANGED:
- persistence/schema.py

SUMMARY:
Implemented the missing category persistence operation. All three bulk-loading acceptance checks pass, and the project suite passes: 15 tests.

The broader terminal harness reports 13 passed and 30 failures from later, out-of-scope ledger features.

BLOCKERS:
- None for this build block.
