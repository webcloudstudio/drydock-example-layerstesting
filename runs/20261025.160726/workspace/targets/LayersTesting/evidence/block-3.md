# Evidence: Block 3 · Service (block-3)

- block type: block
- date: 2026-10-25
- resulting state: closed/verified
- story points (combined assembled cost): 9033
- execution id: 20261025.163158.865Z-1985f6fc

## Stories built
- Provide shared amount parsing and formatting, field validators, date validation, and the projected-balance guard. (ledger-core) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1156)
- implements: FEATURE-LedgerCore.md (SP 3376)
- context: ARCHITECTURE_compact.md (SP 327)
- context: DATABASE_compact.md (SP 453)
- stack: persistence_compact.md (SP 2693)

## Build directory changes
- cli/core.py
- data/logs/test_2026-10-25_123242.log
- tests/test_ledger_core.py

## Pre-build acceptance observation
- RED: core-parse-amount (FEATURE-LedgerCore.md)
  intent: parse_amount converts valid decimal text to integer cents.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "core-parse-amount.py", line 1, in <module>
        from cli.core import parse_amount
    ModuleNotFoundError: No module named 'cli.core'
- RED: core-parse-amount-rejects (FEATURE-LedgerCore.md)
  intent: parse_amount rejects zero, excess decimals, and malformed text with Rejected.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "core-parse-amount-rejects.py", line 1, in <module>
        from cli.core import parse_amount
    ModuleNotFoundError: No module named 'cli.core'
- RED: core-format-amount (FEATURE-LedgerCore.md)
  intent: format_amount prints two decimals, a leading minus when negative, and no thousands separator.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "core-format-amount.py", line 1, in <module>
        from cli.core import format_amount, parse_amount
    ModuleNotFoundError: No module named 'cli.core'
- RED: core-validate-code (FEATURE-LedgerCore.md)
  intent: validate_code accepts 1 to 12 characters of A-Z and 0-9 and rejects everything else.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "core-validate-code.py", line 1, in <module>
        from cli.core import validate_code
    ModuleNotFoundError: No module named 'cli.core'
- RED: core-validate-text (FEATURE-LedgerCore.md)
  intent: Names and memos enforce their length bounds and forbid comma and newline.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "core-validate-text.py", line 1, in <module>
        from cli.core import validate_memo, validate_name
    ModuleNotFoundError: No module named 'cli.core'
- RED: core-validate-date (FEATURE-LedgerCore.md)
  intent: validate_date accepts real YYYY-MM-DD dates and rejects impossible or malformed ones.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "core-validate-date.py", line 1, in <module>
        from cli.core import validate_date
    ModuleNotFoundError: No module named 'cli.core'
- RED: core-balance-guard (FEATURE-LedgerCore.md)
  intent: balance_guard accepts a change that keeps every balance at or above zero, rejects one that goes below, and writes nothing.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "core-balance-guard.py", line 1, in <module>
        from cli.core import account_balance, balance_guard
    ModuleNotFoundError: No module named 'cli.core'
- RED: core-balance-guard-multi-account (FEATURE-LedgerCore.md)
  intent: balance_guard rejects when any one account in the change set would go negative.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "core-balance-guard-multi-account.py", line 1, in <module>
        from cli.core import balance_guard
    ModuleNotFoundError: No module named 'cli.core'
- UNVERIFIED: core-no-floating-point (FEATURE-LedgerCore.md)
  intent: The core module uses no float literal and no float conversion.
  return code: 1
  error: unverified acceptance: the assertion raised FileNotFoundError ([Errno 2] No such file or directory: 'cli/core.py') in its own frame, before reaching the code under test. This is a fault in the acceptance kit or its environment, not a defect in the build.
  stderr:
    Traceback (most recent call last):
      File "core-no-floating-point.py", line 3, in <module>
        with open("cli/core.py", encoding="utf-8") as fh:
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    FileNotFoundError: [Errno 2] No such file or directory: 'cli/core.py'

## Post-build programmatic acceptance
- PASS: core-parse-amount (FEATURE-LedgerCore.md)
  intent: parse_amount converts valid decimal text to integer cents.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: core-parse-amount-rejects (FEATURE-LedgerCore.md)
  intent: parse_amount rejects zero, excess decimals, and malformed text with Rejected.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: core-format-amount (FEATURE-LedgerCore.md)
  intent: format_amount prints two decimals, a leading minus when negative, and no thousands separator.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: core-validate-code (FEATURE-LedgerCore.md)
  intent: validate_code accepts 1 to 12 characters of A-Z and 0-9 and rejects everything else.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: core-validate-text (FEATURE-LedgerCore.md)
  intent: Names and memos enforce their length bounds and forbid comma and newline.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: core-validate-date (FEATURE-LedgerCore.md)
  intent: validate_date accepts real YYYY-MM-DD dates and rejects impossible or malformed ones.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: core-balance-guard (FEATURE-LedgerCore.md)
  intent: balance_guard accepts a change that keeps every balance at or above zero, rejects one that goes below, and writes nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: core-balance-guard-multi-account (FEATURE-LedgerCore.md)
  intent: balance_guard rejects when any one account in the change set would go negative.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: core-no-floating-point (FEATURE-LedgerCore.md)
  intent: The core module uses no float literal and no float conversion.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
Baseline is green (42 passed). Writing `cli/core.py` now.Now the tests: each declared acceptance assertion gets its own test, plus boundary and negative-path tests.All 110 tests pass (42 existing + 68 new), and `bin/test.sh` exits 0. Let me confirm the rollback left the store clean and check the changed files.Built `cli/core.py` (the ledger-core block) with tests. The project suite passes: 110 tests, 42 existing and 68 new, and `sh bin/test.sh` exits 0.

- **`cli/core.py`** provides the nine functions the spec lists. Amounts are integer cents throughout, with no float anywhere. The validators and `balance_guard` raise `Rejected` and never write.
- **`tests/test_ledger_core.py`** has a test for every declared acceptance assertion (`core-parse-amount`, `core-validate-date`, `core-balance-guard`, and the others), plus boundary and negative-path tests. The guard tests run inside the shared rollback session, and I confirmed afterwards that no test rows persisted in the store.

I did not run `sources/run.sh`. It is the terminal story for the whole ledger and is not part of this block's gate.

Choice I made that you may want to change: `balance_guard` does not check whether an account exists. The spec does not say it should, so commands will need to check existence themselves.

FILES CHANGED:
- cli/core.py
- tests/test_ledger_core.py

SUMMARY:
- `parse_amount` accepts `-?DIGITS[.D[D]]` using ASCII-only matching, rejects zero, and returns integer cents.
- `format_amount` always prints two decimals, with a leading minus when negative.
- `validate_code`, `validate_name`, `validate_memo`, and `validate_text` enforce their length bounds and forbid comma and line breaks.
- `validate_date` checks the `YYYY-MM-DD` shape and then confirms a real calendar date.
- `account_balance` sums `db.transactions.list(account=...)`.
- `balance_guard` computes each account's resulting balance in sorted order and raises `Rejected` on the first negative result.
- Checks run: `pytest -q` gives 110 passed. `sh bin/test.sh` exits 0.

RESULT: SUCCESS

<blueprint-decisions>
[{"spec":"FEATURE-LedgerCore.md","severity":"Low","subject":"balance_guard on unknown accounts","decision":"balance_guard does not verify that an account exists; it computes the balance as zero for an unknown code. Existence checks belong to the calling commands. Is that acceptable, or should the guard reject unknown accounts?"}]
</blueprint-decisions>
