# Evidence: Block 4 · Service (block-4)

- block type: block
- date: 2026-10-27
- resulting state: closed/verified
- story points (combined assembled cost): 11123
- execution id: 20261027.142630.745Z-f0980b95

## Stories built
- Validate codes, names, memos, amounts, and dates, and format integer cents as two-decimal text. (feature-validation) [story]
- Check that a proposed set of transaction changes leaves no account balance below zero before any write. (feature-balance-rule) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1134)
- implements: FEATURE-Validation.md (SP 2392)
- context: ARCHITECTURE_compact.md (SP 332)
- context: DATABASE_compact.md (SP 884)
- stack: common_compact.md (SP 1653)
- implements: FEATURE-BalanceRule.md (SP 3464)

## Build directory changes
- data/app.db-shm
- data/app.db-wal
- data/logs/test_2026-10-27_102741.log
- ledger_core/balances.py
- ledger_core/money.py
- ledger_core/validation.py
- tests/test_balances.py
- tests/test_money.py
- tests/test_validation.py

## Pre-build acceptance observation
- RED: validation-code (FEATURE-Validation.md)
  intent: Codes of 1 to 12 characters from A-Z and 0-9 are returned unchanged; empty, lowercase, too long, and other characters are rejected with exit code 3.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "validation-code.py", line 1, in <module>
        from ledger_core.validation import validate_code
    ModuleNotFoundError: No module named 'ledger_core.validation'
- RED: validation-name (FEATURE-Validation.md)
  intent: Names of 1 to 40 characters without comma or newline are accepted; empty, 41 characters, comma, and newline are rejected.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "validation-name.py", line 1, in <module>
        from ledger_core.validation import validate_name
    ModuleNotFoundError: No module named 'ledger_core.validation'
- RED: validation-memo (FEATURE-Validation.md)
  intent: Memos of 0 to 60 characters without comma or newline are accepted, including the empty memo; 61 characters, comma, and newline are rejected.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "validation-memo.py", line 1, in <module>
        from ledger_core.validation import validate_memo
    ModuleNotFoundError: No module named 'ledger_core.validation'
- RED: validation-date (FEATURE-Validation.md)
  intent: Real calendar dates in YYYY-MM-DD form are accepted, including a leap day; impossible dates and other layouts are rejected.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "validation-date.py", line 1, in <module>
        from ledger_core.validation import validate_date
    ModuleNotFoundError: No module named 'ledger_core.validation'
- RED: money-parse-valid (FEATURE-Validation.md)
  intent: Valid amount text parses to the integer cents it denotes, as an int and not a float.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "money-parse-valid.py", line 1, in <module>
        from ledger_core.money import parse_amount
    ModuleNotFoundError: No module named 'ledger_core.money'
- RED: money-parse-invalid (FEATURE-Validation.md)
  intent: Zero, three or more decimals, and text outside -?DIGITS[.D[D]] are rejected with exit code 3.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "money-parse-invalid.py", line 1, in <module>
        from ledger_core.money import parse_amount
    ModuleNotFoundError: No module named 'ledger_core.money'
- RED: money-format (FEATURE-Validation.md)
  intent: Integer cents format with exactly two decimals, a leading minus when negative, and no thousands separator.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "money-format.py", line 1, in <module>
        from ledger_core.money import format_cents
    ModuleNotFoundError: No module named 'ledger_core.money'
- RED: money-round-trip (FEATURE-Validation.md)
  intent: Parsing the formatted text of any nonzero cents value returns the same cents.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "money-round-trip.py", line 1, in <module>
        from ledger_core.money import parse_amount, format_cents
    ModuleNotFoundError: No module named 'ledger_core.money'
- RED: balance-current (FEATURE-BalanceRule.md)
  intent: current_balance sums an account's stored amounts and is zero for an account with no transactions.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "balance-current.py", line 2, in <module>
        from ledger_core.balances import current_balance
    ModuleNotFoundError: No module named 'ledger_core.balances'
- RED: balance-insert (FEATURE-BalanceRule.md)
  intent: An insert that lands the balance at zero passes, one cent below zero is rejected with exit 3, and nothing is written either way.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "balance-insert.py", line 2, in <module>
        from ledger_core.balances import check_no_negative, Insert
    ModuleNotFoundError: No module named 'ledger_core.balances'
- RED: balance-insert-new-account (FEATURE-BalanceRule.md)
  intent: An account with no transactions accepts a positive insert and rejects a negative one.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "balance-insert-new-account.py", line 2, in <module>
        from ledger_core.balances import check_no_negative, Insert
    ModuleNotFoundError: No module named 'ledger_core.balances'
- RED: balance-edit (FEATURE-BalanceRule.md)
  intent: Editing the larger credit below what the debits need is rejected; editing it to exactly cover them passes.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "balance-edit.py", line 2, in <module>
        from ledger_core.balances import check_no_negative, Edit
    ModuleNotFoundError: No module named 'ledger_core.balances'
- RED: balance-delete (FEATURE-BalanceRule.md)
  intent: Deleting the credit that funds a debit is rejected; deleting the debit passes.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "balance-delete.py", line 2, in <module>
        from ledger_core.balances import check_no_negative, Delete
    ModuleNotFoundError: No module named 'ledger_core.balances'
- RED: balance-combined (FEATURE-BalanceRule.md)
  intent: Several changes to one account are judged by their net effect regardless of order; a credit and a debit that net to a non-negative balance pass in either order.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "balance-combined.py", line 2, in <module>
        from ledger_core.balances import check_no_negative, Insert
    ModuleNotFoundError: No module named 'ledger_core.balances'
- RED: balance-multi-account (FEATURE-BalanceRule.md)
  intent: When one of several affected accounts would go negative the whole set is rejected and nothing is written.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "balance-multi-account.py", line 2, in <module>
        from ledger_core.balances import check_no_negative, Insert
    ModuleNotFoundError: No module named 'ledger_core.balances'

## Post-build programmatic acceptance
- PASS: validation-code (FEATURE-Validation.md)
  intent: Codes of 1 to 12 characters from A-Z and 0-9 are returned unchanged; empty, lowercase, too long, and other characters are rejected with exit code 3.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: validation-name (FEATURE-Validation.md)
  intent: Names of 1 to 40 characters without comma or newline are accepted; empty, 41 characters, comma, and newline are rejected.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: validation-memo (FEATURE-Validation.md)
  intent: Memos of 0 to 60 characters without comma or newline are accepted, including the empty memo; 61 characters, comma, and newline are rejected.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: validation-date (FEATURE-Validation.md)
  intent: Real calendar dates in YYYY-MM-DD form are accepted, including a leap day; impossible dates and other layouts are rejected.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: money-parse-valid (FEATURE-Validation.md)
  intent: Valid amount text parses to the integer cents it denotes, as an int and not a float.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: money-parse-invalid (FEATURE-Validation.md)
  intent: Zero, three or more decimals, and text outside -?DIGITS[.D[D]] are rejected with exit code 3.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: money-format (FEATURE-Validation.md)
  intent: Integer cents format with exactly two decimals, a leading minus when negative, and no thousands separator.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: money-round-trip (FEATURE-Validation.md)
  intent: Parsing the formatted text of any nonzero cents value returns the same cents.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: balance-current (FEATURE-BalanceRule.md)
  intent: current_balance sums an account's stored amounts and is zero for an account with no transactions.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: balance-insert (FEATURE-BalanceRule.md)
  intent: An insert that lands the balance at zero passes, one cent below zero is rejected with exit 3, and nothing is written either way.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: balance-insert-new-account (FEATURE-BalanceRule.md)
  intent: An account with no transactions accepts a positive insert and rejects a negative one.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: balance-edit (FEATURE-BalanceRule.md)
  intent: Editing the larger credit below what the debits need is rejected; editing it to exactly cover them passes.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: balance-delete (FEATURE-BalanceRule.md)
  intent: Deleting the credit that funds a debit is rejected; deleting the debit passes.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: balance-combined (FEATURE-BalanceRule.md)
  intent: Several changes to one account are judged by their net effect regardless of order; a credit and a debit that net to a non-negative balance pass in either order.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: balance-multi-account (FEATURE-BalanceRule.md)
  intent: When one of several affected accounts would go negative the whole set is rejected and nothing is written.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
I'll start by inspecting the build directory and the existing files.The `ledger_core` package exists, so I'll add `validation.py`, `money.py`, and `balances.py` alongside it. Next I need the persistence row shape and the test-isolation fixture.Rows come back as dataclasses, so balance code should read attributes such as `.amount`. Before writing tests, I'll check how existing tests use the `db_session` fixture and the rollback context.I have what I need. I'll write the three domain modules first, then tests. Validation comes first.Next, the money module: integer-only parsing and formatting.The `or "0"` in the fraction expression is dead code, since `"".ljust(2, "0")` is already `"00"`. I'll remove it.Now the balance rule. Edits and deletes take their account and stored amount from the database, so the check judges the net effect per account.Now the tests. I'll start with validation, covering the declared boundaries and the rejection paths.Balance tests follow. They use the rollback session from `persistence.testing`, as the acceptance criteria do, and check results by reading the store back.One test has a sloppy argument (`0 + 1`) and doesn't cover what its name claims. I'll make it deliberately net to zero for its own account while another account is already negative.Next I'll run the project's declared test command, `bin/test.sh`, which runs the whole suite.All 155 tests pass. I'll confirm the set of files I changed in the working tree, and check the `ledger_core` boundary rules are covered by the passing foundation tests.The Validation and Balance Rule stories are built, and the project suite passes: 155 tests, exit 0, run with `sh bin/test.sh`.

- **Validation:** codes, names, memos, dates, and amounts are checked as specified, and cents are formatted as two-decimal text. Money uses integer arithmetic only, so the foundation's no-float scan still passes.
- **Balance rule:** `check_no_negative` nets the changes per account and rejects any account that would go below zero, before anything is written.
- **Tests:** new tests cover every declared assertion's cases plus boundaries and rejection paths. Balance tests use the rollback session and read state back through the persistence interface.

I did not run the spec's acceptance blocks verbatim. The new tests cover the same cases, so Drydock's run is the check on the declared text. Nothing is committed.

```text
<blueprint-decisions>
[{"spec":"FEATURE-BalanceRule.md","severity":"Low","subject":"Edit or Delete of a missing transaction","decision":"The spec does not say what happens when txn_id is absent. I raise NotFound (exit 4), matching the CLI error table for absent transactions on amend and delete. Is that acceptable?"},{"spec":"FEATURE-Validation.md","severity":"Low","subject":"Carriage return in names and memos","decision":"The spec forbids only comma and newline. I also reject carriage return (\\r), because it would break the CSV output. Is that acceptable?"}]
</blueprint-decisions>
```

RESULT: SUCCESS

FILES CHANGED:
- ledger_core/validation.py
- ledger_core/money.py
- ledger_core/balances.py
- tests/test_validation.py
- tests/test_money.py
- tests/test_balances.py

SUMMARY:
Implemented `validate_code`, `validate_name`, `validate_memo`, `validate_date`, `parse_amount`, and `format_cents` in `ledger_core`, plus `Insert`/`Edit`/`Delete`, `current_balance`, and `check_no_negative` in `ledger_core/balances.py`. Violations raise `Rejected` (exit 3). Missing transactions on Edit/Delete raise `NotFound` (exit 4). Checks were run with `sh bin/test.sh`: 155 passed, exit 0. The new tests mirror the declared acceptance cases and add boundary and negative-path coverage. The spec's acceptance blocks were not run verbatim.

BLOCKERS:
- None.
