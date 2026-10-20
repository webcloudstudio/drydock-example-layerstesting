# Evidence: Block 4 · Service (block-4)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 8221
- execution id: 20261020.162505.310Z-f8d7313e

## Stories built
- Validate ledger identifiers, values, dates, and relationships. (persist-003) [story]

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: FEATURE-Validation.md (SP 1017)
- context: ARCHITECTURE_compact.md (SP 203)
- context: DATABASE_compact.md (SP 197)
- stack: common.md (SP 1812)
- stack: sqlite.md (SP 1818)
- stack: cli.md (SP 1755)

## Build directory changes
- cli/__init__.py
- services.py
- tests/test_validation.py
- validation.py

## Pre-build acceptance observation
- RED: validation-invalid-amount (FEATURE-Validation.md)
  intent: Invalid decimal precision is rejected with the declared rejection status and no output.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
      expected_code = 3
    --- drydock: end values ---
    Traceback (most recent call last):
      File "validation-invalid-amount.py", line 10, in <module>
        assert code == expected_code
               ^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: validation-invalid-date (FEATURE-Validation.md)
  intent: Nonexistent calendar dates are rejected with the declared rejection status.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
      expected_code = 3
    --- drydock: end values ---
    Traceback (most recent call last):
      File "validation-invalid-date.py", line 5, in <module>
        assert code == expected_code
               ^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: validation-negative-balance (FEATURE-Validation.md)
  intent: A command that would make an account balance negative is rejected without standard output.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
      expected_code = 3
    --- drydock: end values ---
    Traceback (most recent call last):
      File "validation-negative-balance.py", line 5, in <module>
        assert code == expected_code
               ^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: validation-unknown-reference (FEATURE-Validation.md)
  intent: Unknown account or category references are rejected before a transaction is written.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
      expected_code = 3
    --- drydock: end values ---
    Traceback (most recent call last):
      File "validation-unknown-reference.py", line 5, in <module>
        assert code == expected_code
               ^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: validation-atomic-rejection (FEATURE-Validation.md)
  intent: A rejected transaction leaves the persisted transaction count unchanged.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      reject_code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "validation-atomic-rejection.py", line 8, in <module>
        assert reject_code == 3
               ^^^^^^^^^^^^^^^^
    AssertionError

## Post-build programmatic acceptance
- PASS: validation-invalid-amount (FEATURE-Validation.md)
  intent: Invalid decimal precision is rejected with the declared rejection status and no output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: validation-invalid-date (FEATURE-Validation.md)
  intent: Nonexistent calendar dates are rejected with the declared rejection status.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: validation-negative-balance (FEATURE-Validation.md)
  intent: A command that would make an account balance negative is rejected without standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: validation-unknown-reference (FEATURE-Validation.md)
  intent: Unknown account or category references are rejected before a transaction is written.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: validation-atomic-rejection (FEATURE-Validation.md)
  intent: A rejected transaction leaves the persisted transaction count unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
RESULT: SUCCESS

FILES CHANGED:
- cli/__init__.py
- services.py
- validation.py
- tests/test_validation.py

SUMMARY:
Implemented shared validation, integer-cent amount parsing, date checks, reference validation, atomic rejection behavior, and `txn post`. All tests pass: 11 passed.

BLOCKERS:
- None
