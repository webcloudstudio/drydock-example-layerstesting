# Evidence: Block 13 · Service (block-13)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 7351
- execution id: 20261020.194524.137Z-55265864

## Stories built
- Report transaction totals by category. (category-report) [story]

## Missing context
- context: INSTRUCTIONS.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: FEATURE-Report-Categories.md (SP 841)
- context: ARCHITECTURE_compact.md (SP 154)
- context: DATABASE_compact.md (SP 163)
- stack: cli.md (SP 1755)
- stack: persistence_compact.md (SP 1217)
- stack: sqlite.md (SP 1818)

## Build directory changes
- cli/__init__.py
- data/app.db
- tests/test_category_report.py

## Pre-build acceptance observation
- RED: category-report-includes-zero-activity (FEATURE-Report-Categories.md)
  intent: The category report includes categories with no transactions.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "category-report-includes-zero-activity.py", line 13, in <module>
        assert cli_runner("txn", "post", "A", "ACTIVE", "5.00", "receipt")[0] == 0
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: category-report-calculates-flows (FEATURE-Report-Categories.md)
  intent: The category report calculates inflow, outflow, and net from persisted integer cents.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "category-report-calculates-flows.py", line 12, in <module>
        assert cli_runner("txn", "post", "A", "C", "10.00", "in")[0] == 0
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- GREEN (prepassed): category-report-rejects-unknown-report (FEATURE-Report-Categories.md)
  intent: An unknown category report name returns a usage error without output.
  return code: 0

## Post-build programmatic acceptance
- PASS: category-report-includes-zero-activity (FEATURE-Report-Categories.md)
  intent: The category report includes categories with no transactions.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: category-report-calculates-flows (FEATURE-Report-Categories.md)
  intent: The category report calculates inflow, outflow, and net from persisted integer cents.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: category-report-rejects-unknown-report (FEATURE-Report-Categories.md)
  intent: An unknown category report name returns a usage error without output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Repair attempts
- attempt 0 (initial build): failed; 1/3 checks model=gpt-5.6-luna; execution 20261020.194327.525Z-9a0d5c95; reason: programmatic acceptance failed: category-report-includes-zero-activity, category-report-calculates-flows
- attempt 1 (repair 1): failed; 3/3 checks model=gpt-5.6-luna; execution 20261020.194430.959Z-8f4ad769; reason: acceptance regression: transaction-validation
- attempt 2 (repair 2): built; 3/3 checks model=gpt-5.6-luna; execution 20261020.194524.137Z-55265864

## Build summary
RESULT: SUCCESS

FILES CHANGED:
- cli/__init__.py

SUMMARY:
Fixed transaction shorthand parsing so malformed date-shaped inputs are rejected while memo shorthand remains supported. Category acceptance checks pass, project tests pass (40), and `sources/run.sh` passes all 43 checks.

BLOCKERS:
- None
