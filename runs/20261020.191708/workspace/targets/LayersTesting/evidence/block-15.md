# Evidence: Block 15 · Service (block-15)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 4249
- execution id: 20261020.194916.183Z-a5456b18

## Stories built
- Provide the automated project test runner and test suite. (project-tests) [story]

## Missing context
- context: INSTRUCTIONS.md
- stack: pytest.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: FEATURE-Project-Tests.md (SP 707)
- context: ARCHITECTURE_compact.md (SP 154)
- context: DATABASE_compact.md (SP 163)
- stack: common.md (SP 1812)

## Build directory changes
- bin/test.sh
- tests/test_project_test_runner.py

## Pre-build acceptance observation
- GREEN (prepassed): project-test-runner (FEATURE-Project-Tests.md)
  intent: The project test runner exists, is executable, and passes the automated suite.
  return code: 0
  stdout:
    ............................................                             [100%]
- GREEN (prepassed): project-test-runner-is-repeatable (FEATURE-Project-Tests.md)
  intent: Running the project test runner twice succeeds independently.
  return code: 0
  stdout:
    ............................................                             [100%]
    
    
    ............................................                             [100%]
- GREEN (prepassed): project-test-surface (FEATURE-Project-Tests.md)
  intent: The project suite exercises the executable ledger command surface.
  return code: 0

## Post-build programmatic acceptance
- PASS: project-test-runner (FEATURE-Project-Tests.md)
  intent: The project test runner exists, is executable, and passes the automated suite.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ..............................................                           [100%]
- PASS: project-test-runner-is-repeatable (FEATURE-Project-Tests.md)
  intent: Running the project test runner twice succeeds independently.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ..............................................                           [100%]
    
    
    ..............................................                           [100%]
- PASS: project-test-surface (FEATURE-Project-Tests.md)
  intent: The project suite exercises the executable ledger command surface.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
RESULT: SUCCESS

FILES CHANGED:
- bin/test.sh
- tests/test_project_test_runner.py

SUMMARY:
Added a caller-independent POSIX test runner and project runner/surface tests. `pytest` passed twice with 46 tests; terminal harness passed 43/43 checks.

BLOCKERS:
- None
