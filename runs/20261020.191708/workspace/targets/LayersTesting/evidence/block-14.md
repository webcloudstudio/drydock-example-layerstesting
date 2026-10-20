# Evidence: Block 14 · Service (block-14)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 7326
- execution id: 20261020.194744.437Z-3bbce025

## Stories built
- Report transaction totals by calendar month. (monthly-report) [story]

## Missing context
- context: INSTRUCTIONS.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: FEATURE-Report-Monthly.md (SP 820)
- context: ARCHITECTURE_compact.md (SP 154)
- context: DATABASE_compact.md (SP 163)
- stack: cli.md (SP 1755)
- stack: persistence_compact.md (SP 1217)
- stack: sqlite.md (SP 1818)

## Build directory changes
- cli/__init__.py
- data/app.db
- reports.py
- tests/test_monthly_report.py

## Pre-build acceptance observation
- RED: monthly-report-groups-months (FEATURE-Report-Monthly.md)
  intent: The monthly report groups persisted transactions by ascending calendar month.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      months = ['2026-10']
    --- drydock: end values ---
    Traceback (most recent call last):
      File "monthly-report-groups-months.py", line 19, in <module>
        assert months == ["2026-01"]
               ^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: monthly-report-separates-months (FEATURE-Report-Monthly.md)
  intent: Transactions in separate months produce separate monthly rows and a computed total.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      rows = [['month', 'transactions', 'inflow', 'outflow', 'net'], ['2026-10', '2', '2.00', '1.25', '0.75'], ['TOTAL', '2', '2.00', '1.25', '0.75']]
    --- drydock: end values ---
    Traceback (most recent call last):
      File "monthly-report-separates-months.py", line 18, in <module>
        assert len(rows) == 4
               ^^^^^^^^^^^^^^
    AssertionError
- GREEN (prepassed): monthly-report-empty (FEATURE-Report-Monthly.md)
  intent: An initialized empty ledger produces only the monthly header and total row.
  return code: 0

## Post-build programmatic acceptance
- PASS: monthly-report-groups-months (FEATURE-Report-Monthly.md)
  intent: The monthly report groups persisted transactions by ascending calendar month.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: monthly-report-separates-months (FEATURE-Report-Monthly.md)
  intent: Transactions in separate months produce separate monthly rows and a computed total.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: monthly-report-empty (FEATURE-Report-Monthly.md)
  intent: An initialized empty ledger produces only the monthly header and total row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Repair attempts
- attempt 0 (initial build): failed; 1/3 checks model=gpt-5.6-luna; execution 20261020.194628.023Z-de5fc6e8; reason: programmatic acceptance failed: monthly-report-groups-months, monthly-report-separates-months
- attempt 1 (repair 1): built; 3/3 checks model=gpt-5.6-luna; execution 20261020.194744.437Z-3bbce025

## Build summary
RESULT: SUCCESS

FILES CHANGED:
- cli/__init__.py
- reports.py
- tests/test_monthly_report.py

SUMMARY:
Fixed shorthand transaction dates so monthly grouping passes. Full test suite: 44 passed. Terminal harness: 43 passed, 0 failed.

BLOCKERS:
- None
