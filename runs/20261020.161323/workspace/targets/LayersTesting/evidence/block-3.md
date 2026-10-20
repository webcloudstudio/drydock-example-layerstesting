# Evidence: Block 3 · Service (block-3)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 7838
- execution id: 20261020.162402.491Z-7085ae7d

## Stories built
- Initialize the ledger schema and report table counts. (persist-002) [story]

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: FEATURE-Persistence-Lifecycle.md (SP 648)
- context: ARCHITECTURE_compact.md (SP 203)
- context: DATABASE_compact.md (SP 197)
- stack: common.md (SP 1812)
- stack: sqlite.md (SP 1818)
- stack: cli.md (SP 1755)

## Build directory changes
- cli/__init__.py
- data/app.db
- services.py
- tests/test_architecture.py

## Pre-build acceptance observation
- GREEN (prepassed): persistence-init-clears-state (FEATURE-Persistence-Lifecycle.md)
  intent: Initialization succeeds and the subsequent count observes the empty ledger state.
  return code: 0
- RED: persistence-count-contract (FEATURE-Persistence-Lifecycle.md)
  intent: Count returns a successful structured result for the three declared tables.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      lines = ['table,count', 'accounts,0', 'categories,0', 'transactions,0']
    --- drydock: end values ---
    Traceback (most recent call last):
      File "persistence-count-contract.py", line 8, in <module>
        assert lines[0].split(",") == ["table", "rows"]
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: persistence-reinitialization (FEATURE-Persistence-Lifecycle.md)
  intent: Reinitialization removes previously persisted rows.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      account_code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "persistence-reinitialization.py", line 7, in <module>
        assert account_code == 0
               ^^^^^^^^^^^^^^^^^
    AssertionError

## Post-build programmatic acceptance
- PASS: persistence-init-clears-state (FEATURE-Persistence-Lifecycle.md)
  intent: Initialization succeeds and the subsequent count observes the empty ledger state.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: persistence-count-contract (FEATURE-Persistence-Lifecycle.md)
  intent: Count returns a successful structured result for the three declared tables.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: persistence-reinitialization (FEATURE-Persistence-Lifecycle.md)
  intent: Reinitialization removes previously persisted rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Repair attempts
- attempt 0 (initial build): failed; 2/3 checks model=gpt-5.6-luna; execution 20261020.162240.515Z-3a598d06; reason: programmatic acceptance failed: persistence-reinitialization
- attempt 1 (repair 1): built; 3/3 checks model=gpt-5.6-luna; execution 20261020.162402.491Z-7085ae7d

## Build summary
RESULT: SUCCESS

FILES CHANGED:
- cli/__init__.py
- services.py
- tests/test_architecture.py

SUMMARY:
Implemented `account add` prerequisite and verified lifecycle initialization/count behavior. All 7 project tests and acceptance assertions pass.

BLOCKERS:
- None
