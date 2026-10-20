# Evidence: Block 12 · Service (block-12)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 7296
- execution id: 20261020.194213.440Z-13a35b79

## Stories built
- Report balances and transaction counts by account. (balance-report) [story]

## Missing context
- context: INSTRUCTIONS.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: FEATURE-Report-Balances.md (SP 786)
- context: ARCHITECTURE_compact.md (SP 154)
- context: DATABASE_compact.md (SP 163)
- stack: cli.md (SP 1755)
- stack: persistence_compact.md (SP 1217)
- stack: sqlite.md (SP 1818)

## Build directory changes
- cli/__init__.py
- tests/test_balance_report.py

## Pre-build acceptance observation
- GREEN (prepassed): balance-report-empty (FEATURE-Report-Balances.md)
  intent: The balances report succeeds for an initialized empty ledger and reports no account rows.
  return code: 0
- RED: balance-report-computes-persisted-state (FEATURE-Report-Balances.md)
  intent: The report reflects persisted account counts and balances after transactions.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      rows = [['account', 'name', 'transactions', 'balance'], ['B', 'Second', '1', '3.25'], ['A', 'First', '1', '12.50'], ['TOTAL', '', '2', '15.75']]
    --- drydock: end values ---
    Traceback (most recent call last):
      File "balance-report-computes-persisted-state.py", line 19, in <module>
        assert [row[0] for row in rows[1:-1]] == ["A", "B"]
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- GREEN (prepassed): balance-report-missing-database (FEATURE-Report-Balances.md)
  intent: A balances report against an unavailable database path returns an operational failure.
  return code: 0

## Post-build programmatic acceptance
- PASS: balance-report-empty (FEATURE-Report-Balances.md)
  intent: The balances report succeeds for an initialized empty ledger and reports no account rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: balance-report-computes-persisted-state (FEATURE-Report-Balances.md)
  intent: The report reflects persisted account counts and balances after transactions.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: balance-report-missing-database (FEATURE-Report-Balances.md)
  intent: A balances report against an unavailable database path returns an operational failure.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
RESULT: SUCCESS

FILES CHANGED:
- cli/__init__.py
- tests/test_balance_report.py

SUMMARY:
Implemented account-code ordering and dynamic balance reporting. Added focused tests. `sh bin/test.sh` passes 39 tests; `sources/run.sh` passes all 43 checks.

BLOCKERS:
- None
