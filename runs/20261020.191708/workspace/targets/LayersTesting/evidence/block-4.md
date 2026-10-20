# Evidence: Block 4 · Foundational (block-4)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 4085
- execution id: 20261020.192834.528Z-6a1c8a15

## Stories built
- Provide the executable ledger command dispatcher and output contract. (cli-dispatch) [story]

## Missing context
- context: INSTRUCTIONS.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: FEATURE-CLI-Dispatcher.md (SP 602)
- context: ARCHITECTURE_compact.md (SP 154)
- context: DATABASE_compact.md (SP 163)
- stack: cli.md (SP 1755)

## Build directory changes
- cli/__init__.py
- data/app.db
- persistence/schema.py
- schema.sql
- tests/test_architecture.py
- validation.py

## Pre-build acceptance observation
- GREEN (prepassed): cli-dispatch-executable (FEATURE-CLI-Dispatcher.md)
  intent: The application root contains an executable ledger entry point.
  return code: 0
- RED: cli-dispatch-init-and-count (FEATURE-CLI-Dispatcher.md)
  intent: The dispatcher reaches schema initialization and produces structured count output.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      rows = [['0']]
    --- drydock: end values ---
    Traceback (most recent call last):
      File "cli-dispatch-init-and-count.py", line 10, in <module>
        assert rows[0] == ["table", "rows"]
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: cli-dispatch-error-channel (FEATURE-CLI-Dispatcher.md)
  intent: Rejected commands return a failure code without standard-output data and provide diagnostics on standard error.
  return code: 2

## Post-build programmatic acceptance
- PASS: cli-dispatch-executable (FEATURE-CLI-Dispatcher.md)
  intent: The application root contains an executable ledger entry point.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-dispatch-init-and-count (FEATURE-CLI-Dispatcher.md)
  intent: The dispatcher reaches schema initialization and produces structured count output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-dispatch-error-channel (FEATURE-CLI-Dispatcher.md)
  intent: Rejected commands return a failure code without standard-output data and provide diagnostics on standard error.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Repair attempts
- attempt 0 (initial build): failed; 2/3 checks model=gpt-5.6-luna; execution 20261020.192552.042Z-b6392c35; reason: programmatic acceptance failed: cli-dispatch-error-channel
- attempt 1 (repair 1): built; 3/3 checks model=gpt-5.6-luna; execution 20261020.192834.528Z-6a1c8a15

## Build summary
RESULT: SUCCESS

FILES CHANGED:
- validation.py
- cli/__init__.py
- tests/test_architecture.py

SUMMARY:
Added code validation so `BAD-CODE` returns exit code 3 with stderr-only diagnostics. All tests pass, including the 43-check terminal harness.

BLOCKERS:
- None
