# Evidence: Block 7 · Service (block-7)

- block type: block
- date: 2026-10-27
- resulting state: closed/verified
- story points (combined assembled cost): 13314
- execution id: 20261027.145304.850Z-9dffce8d

## Stories built
- Implement `ledger load transactions <csv>` with foreign-key, date, amount, and balance validation before any write. (feature-load-transactions) [story]

## Acceptance tooling authorization
- FEATURE-LoadTransactions.md#load-transactions-success: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-LoadTransactions.md#load-transactions-unknown-reference-stores-nothing: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-LoadTransactions.md#load-transactions-invalid-fields: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-LoadTransactions.md#load-transactions-duplicate-ids-rejected: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-LoadTransactions.md#load-transactions-negative-balance-rejected: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-LoadTransactions.md#load-transactions-balance-considers-whole-file: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-LoadTransactions.md#load-transactions-header-and-usage: executable=python3; scope=test; authorization=existing Target environment

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1134)
- implements: FEATURE-LoadTransactions.md (SP 5523)
- context: ARCHITECTURE_compact.md (SP 332)
- context: DATABASE_compact.md (SP 884)
- stack: common_compact.md (SP 1653)
- stack: cli.md (SP 2689)

## Build directory changes
- cli/commands/load.py
- data/app.db-shm
- data/app.db-wal
- tests/test_load_transactions.py

## Pre-build acceptance observation
- RED: load-transactions-success (FEATURE-LoadTransactions.md)
  intent: a valid file loads every row keeping its txn_id, prints the declared two CSV rows, and each stored row reads back with the cents derived from the input text.
  return code: 1
  stdout:
    error: loading transactions is not implemented yet
  stderr:
    --- drydock: values at failure ---
      code = 1
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-success.py", line 26, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: load-transactions-unknown-reference-stores-nothing (FEATURE-LoadTransactions.md)
  intent: a final row naming an unknown account rejects the whole file with exit 3, and none of the ten valid rows before it is stored.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 1
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-unknown-reference-stores-nothing.py", line 22, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: load-transactions-invalid-fields (FEATURE-LoadTransactions.md)
  intent: each invalid date, amount, memo, or txn_id rejects the file with exit 3 and stores neither the bad row nor the valid row before it.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      bad = ['920000201', '2026-02-30', 'ZZMC1', 'ZZMC3', '10.00', 'impossible date']
      code = 1
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-invalid-fields.py", line 31, in <module>
        assert code == 3, bad
               ^^^^^^^^^
    AssertionError: ['920000201', '2026-02-30', 'ZZMC1', 'ZZMC3', '10.00', 'impossible date']
- RED: load-transactions-duplicate-ids-rejected (FEATURE-LoadTransactions.md)
  intent: a txn_id repeated inside the file, or already stored, rejects the whole file with exit 3 and leaves the stored row unchanged.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 1
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-duplicate-ids-rejected.py", line 24, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: load-transactions-negative-balance-rejected (FEATURE-LoadTransactions.md)
  intent: a file whose combined effect leaves an account below zero is rejected with exit 3 and stores no row, even though each row is individually well formed.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 1
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-negative-balance-rejected.py", line 23, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: load-transactions-balance-considers-whole-file (FEATURE-LoadTransactions.md)
  intent: a withdrawal listed before the deposit that funds it is accepted because the balance rule uses the combined effect of all rows, and both rows are stored.
  return code: 1
  stdout:
    error: loading transactions is not implemented yet
  stderr:
    --- drydock: values at failure ---
      code = 1
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-balance-considers-whole-file.py", line 25, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- GREEN (prepassed): load-transactions-header-and-usage (FEATURE-LoadTransactions.md)
  intent: a wrong header exits 3 with nothing stored, an unreadable file exits 1, and a missing file argument exits 2.
  return code: 0

## Post-build programmatic acceptance
- PASS: load-transactions-success (FEATURE-LoadTransactions.md)
  intent: a valid file loads every row keeping its txn_id, prints the declared two CSV rows, and each stored row reads back with the cents derived from the input text.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    table,loaded
    transactions,3
- PASS: load-transactions-unknown-reference-stores-nothing (FEATURE-LoadTransactions.md)
  intent: a final row naming an unknown account rejects the whole file with exit 3, and none of the ten valid rows before it is stored.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: load-transactions-invalid-fields (FEATURE-LoadTransactions.md)
  intent: each invalid date, amount, memo, or txn_id rejects the file with exit 3 and stores neither the bad row nor the valid row before it.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: load-transactions-duplicate-ids-rejected (FEATURE-LoadTransactions.md)
  intent: a txn_id repeated inside the file, or already stored, rejects the whole file with exit 3 and leaves the stored row unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: load-transactions-negative-balance-rejected (FEATURE-LoadTransactions.md)
  intent: a file whose combined effect leaves an account below zero is rejected with exit 3 and stores no row, even though each row is individually well formed.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: load-transactions-balance-considers-whole-file (FEATURE-LoadTransactions.md)
  intent: a withdrawal listed before the deposit that funds it is accepted because the balance rule uses the combined effect of all rows, and both rows are stored.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    table,loaded
    transactions,2
- PASS: load-transactions-header-and-usage (FEATURE-LoadTransactions.md)
  intent: a wrong header exits 3 with nothing stored, an unreadable file exits 1, and a missing file argument exits 2.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
Existing load commands and core validators cover most of what this step needs. I'll get a baseline test run before editing.Baseline is green: 365 passed. Now I'll replace the transactions placeholder with the validating loader, reusing the existing `read_rows`, validators, `check_no_negative`, and `run_all`.I wrote the undo wrong: `_remove` calls its argument positionally, but `transactions.delete` takes `txn_id=` as a keyword. Fixing that with a dedicated undo helper.Now the tests. I'll follow `tests/test_load.py`: act through `cli_runner`, read back through the store, and cover the declared acceptance cases plus boundaries and a rollback path.That last test is wrong: a `-0.01` row on an empty account is overdrawn and would be rejected, and the `or True` assertion checks nothing. I'll rewrite the whole file cleanly.Running the new tests first, then the full suite and the grader.The suite is green at 389 passed. The grader shows 37 of 43 passing; the six failures are all `ledger report`, which is outside this block. Let me confirm the load-transaction checks specifically pass.RESULT: SUCCESS

`ledger load transactions <csv>` now validates the whole file before its first write and inserts all rows as one unit. The pytest suite passes (389 tests, including 24 new ones). The grader is at 37 of 43: all 6 failures are `ledger report` checks (C1–C3, H1–H3), which belong to a later block. Every load-transactions check passes, including B3 (120 seed rows) and D1 (the bad file, which exits 3 with nothing stored).

FILES CHANGED:
- cli/commands/load.py
- tests/test_load_transactions.py

SUMMARY:
- **`cli/commands/load.py`**: replaced the placeholder with `load_transactions`. Validation runs over every row first: `txn_id` parses as an integer, repeated ids in the file and ids already stored are rejected, the date is a real `YYYY-MM-DD` date, the account and category exist in the store, the amount parses to integer cents with at most two decimals and is not zero, and the memo is 0–60 characters with no comma or newline. Then `check_no_negative` runs over all rows together as inserts, so the net effect per account decides. Only after that does `run_all` insert the rows, keeping each file `txn_id`. Output is `table,loaded` and `transactions,<n>`.
- **`tests/test_load_transactions.py`**: covers the five declared acceptance scenarios, plus boundaries (header-only file, 60-character memo, one-decimal amount, a withdrawal that leaves exactly zero), overdraft against a stored balance, unknown account and category, the row-11 case, each invalid field, duplicate ids, wrong header, missing file, usage counts, and rollback when an insert fails partway. Tests act through `cli_runner` and read back through the store.

Choices I made:
- Atomicity uses the existing `run_all` compensating-delete pattern from `ledger_core/atomic.py`, not a real database transaction. The persistence layer exposes no multi-write transaction, and the account and category loaders already work this way.
- `parse_txn_id` accepts negative integers, since the spec says only "an integer". Say if you want positive ids only.
- Nothing was committed, per the build instructions.
