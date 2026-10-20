# Evidence: Block 9 · Service (block-9)

- block type: block
- date: 2026-10-20
- resulting state: closed/failed
- story points (combined assembled cost): 4906
- execution id: 20261020.152655.059Z-e4891cc5

## Stories built
- Reject any command that would leave an account balance below zero. (INTEG-002) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1145)
- implements: FEATURE-NonNegativeBalance.md (SP 1910)
- context: ARCHITECTURE_compact.md (SP 427)
- context: DATABASE_compact.md (SP 427)

## Build directory changes
- balance.py
- tests/test_balance.py

## Pre-build acceptance observation
- RED: nonneg-rejects-negative-balance (FEATURE-NonNegativeBalance.md)
  intent: A balance below zero raises RejectedError with exit code 3.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "nonneg-rejects-negative-balance.py", line 5, in <module>
        from balance import RejectedError, ensure_non_negative
    ModuleNotFoundError: No module named 'balance'
- RED: nonneg-accepts-zero-balance (FEATURE-NonNegativeBalance.md)
  intent: A balance of exactly zero does not raise.
  return code: 1
  note: proof contains no assertion, raise, or failing exit
  stderr:
    Traceback (most recent call last):
      File "nonneg-accepts-zero-balance.py", line 5, in <module>
        from balance import ensure_non_negative
    ModuleNotFoundError: No module named 'balance'
- RED: nonneg-sums-all-transactions (FEATURE-NonNegativeBalance.md)
  intent: The balance is the sum of all transactions, so a positive total passes even with a negative row.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "nonneg-sums-all-transactions.py", line 5, in <module>
        from balance import ensure_non_negative
    ModuleNotFoundError: No module named 'balance'
- RED: nonneg-rejection-changes-nothing (FEATURE-NonNegativeBalance.md)
  intent: A rejected check leaves every transaction row unchanged.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "nonneg-rejection-changes-nothing.py", line 5, in <module>
        from balance import RejectedError, ensure_non_negative
    ModuleNotFoundError: No module named 'balance'

## Post-build programmatic acceptance
- FAIL: nonneg-rejects-negative-balance (FEATURE-NonNegativeBalance.md)
  intent: A balance below zero raises RejectedError with exit code 3.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 1
  stderr:
    --- drydock: values at failure ---
      operation = Operation(identifier='FEATURE-LEDGER-008', table='categories', verb='create', inputs=('category', 'description'), row=<class 'persistence.schema.CategoryRow'>, columns=('category', 'description'), key=None)
    --- drydock: end values ---
    Traceback (most recent call last):
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 245, in run
        return self._dispatch(operation, cursor, connection, names, values)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 280, in _dispatch
        cursor.execute(self._driver.insert(table, names, key), values)
    sqlite3.OperationalError: no such table: categories
    
    The above exception was the direct cause of the following exception:
    
    Traceback (most recent call last):
      File "nonneg-rejects-negative-balance.py", line 9, in <module>
        db.categories.create(category="OPENING", description="Opening balance")
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 186, in <lambda>
        return lambda **arguments: self._database.run(operation, arguments)
                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 248, in run
        raise PersistenceError(f"{operation.identifier} failed: {exc}") from exc
    persistence.db.PersistenceError: FEATURE-LEDGER-008 failed: no such table: categories
- UNVERIFIED: nonneg-accepts-zero-balance (FEATURE-NonNegativeBalance.md)
  intent: A balance of exactly zero does not raise.
  provisioning: not required
  error: excluded check: ALWAYS_PASSES vacuous
- FAIL: nonneg-sums-all-transactions (FEATURE-NonNegativeBalance.md)
  intent: The balance is the sum of all transactions, so a positive total passes even with a negative row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 1
  stderr:
    --- drydock: values at failure ---
      operation = Operation(identifier='FEATURE-LEDGER-008', table='categories', verb='create', inputs=('category', 'description'), row=<class 'persistence.schema.CategoryRow'>, columns=('category', 'description'), key=None)
    --- drydock: end values ---
    Traceback (most recent call last):
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 245, in run
        return self._dispatch(operation, cursor, connection, names, values)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 280, in _dispatch
        cursor.execute(self._driver.insert(table, names, key), values)
    sqlite3.OperationalError: no such table: categories
    
    The above exception was the direct cause of the following exception:
    
    Traceback (most recent call last):
      File "nonneg-sums-all-transactions.py", line 9, in <module>
        db.categories.create(category="OPENING", description="Opening balance")
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 186, in <lambda>
        return lambda **arguments: self._database.run(operation, arguments)
                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 248, in run
        raise PersistenceError(f"{operation.identifier} failed: {exc}") from exc
    persistence.db.PersistenceError: FEATURE-LEDGER-008 failed: no such table: categories
- FAIL: nonneg-rejection-changes-nothing (FEATURE-NonNegativeBalance.md)
  intent: A rejected check leaves every transaction row unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 1
  stderr:
    --- drydock: values at failure ---
      operation = Operation(identifier='FEATURE-LEDGER-008', table='categories', verb='create', inputs=('category', 'description'), row=<class 'persistence.schema.CategoryRow'>, columns=('category', 'description'), key=None)
    --- drydock: end values ---
    Traceback (most recent call last):
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 245, in run
        return self._dispatch(operation, cursor, connection, names, values)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 280, in _dispatch
        cursor.execute(self._driver.insert(table, names, key), values)
    sqlite3.OperationalError: no such table: categories
    
    The above exception was the direct cause of the following exception:
    
    Traceback (most recent call last):
      File "nonneg-rejection-changes-nothing.py", line 9, in <module>
        db.categories.create(category="OPENING", description="Opening balance")
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 186, in <lambda>
        return lambda **arguments: self._database.run(operation, arguments)
                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 248, in run
        raise PersistenceError(f"{operation.identifier} failed: {exc}") from exc
    persistence.db.PersistenceError: FEATURE-LEDGER-008 failed: no such table: categories

## Repair attempts
- attempt 0 (initial build): failed; 0/4 checks model=claude-haiku-5-5; execution 20261020.152429.991Z-53e47f83; reason: programmatic acceptance failed: nonneg-rejects-negative-balance, nonneg-sums-all-transactions, nonneg-rejection-changes-nothing
- attempt 1 (repair 1): failed; 0/4 checks model=claude-haiku-5-5; execution 20261020.152605.708Z-1693ac29; reason: programmatic acceptance failed: nonneg-rejects-negative-balance, nonneg-sums-all-transactions, nonneg-rejection-changes-nothing
- attempt 2 (repair 2): failed; 0/4 checks model=claude-haiku-5-5; execution 20261020.152655.059Z-e4891cc5; stopped: deterministic acceptance score did not improve on 2 consecutive calls; reason: programmatic acceptance failed: nonneg-rejects-negative-balance, nonneg-sums-all-transactions, nonneg-rejection-changes-nothing

## Agent self-report (advisory)
The build agent declared a failure. This is advisory only; the programmatic acceptance above is the authority for this block's outcome.
- summary: Staged acceptance checks fail at setup because `open_database` does not apply the declared schema to a fresh store.
- detail:
    Each check creates a category on a store with no tables, so it raises `no such table: categories` before `ensure_non_negative` is reached. `persistence/schema.py` and `persistence/db.py` are generated or shipped and must not be hand-edited. Before rerunning, the Drydock persistence generation must make `open_database` apply `schema.sql` to a new store, or the criteria must open their store through `db_session()`. Also, `nonneg-accepts-zero-balance` is reported as vacuous by the harness; that criterion has no assertion that can fail, so it needs repair in the Blueprint.

## Failure
- summary: programmatic acceptance failed: nonneg-rejects-negative-balance, nonneg-sums-all-transactions, nonneg-rejection-changes-nothing
- detail:
    Block "Block 9 · Service" [block-9] failed its acceptance criteria.
      Story "Reject any command that would leave an account balance below zero." [INTEG-002] does not meet its own acceptance criteria:
        - AC nonneg-rejects-negative-balance — A balance below zero raises RejectedError with exit code 3.
            assertion: persistence.db.PersistenceError: FEATURE-LEDGER-008 failed: no such table: categories
            raised at: db.py:248
            process exit code: 1
            error: persistence.db.PersistenceError: FEATURE-LEDGER-008 failed: no such table: categories
            values at failure:
              operation = Operation(identifier='FEATURE-LEDGER-008', table='categories', verb='create', inputs=('category', 'description'), row=<class 'persistence.schema.CategoryRow'>, columns=('category', 'description'), key=None)
            check stderr:
              Traceback (most recent call last):
                File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 245, in run
                  return self._dispatch(operation, cursor, connection, names, values)
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 280, in _dispatch
                  cursor.execute(self._driver.insert(table, names, key), values)
              sqlite3.OperationalError: no such table: categories
              The above exception was the direct cause of the following exception:
              Traceback (most recent call last):
                File "nonneg-rejects-negative-balance.py", line 9, in <module>
                  db.categories.create(category="OPENING", description="Opening balance")
                File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 186, in <lambda>
                  return lambda **arguments: self._database.run(operation, arguments)
                                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 248, in run
                  raise PersistenceError(f"{operation.identifier} failed: {exc}") from exc
              persistence.db.PersistenceError: FEATURE-LEDGER-008 failed: no such table: categories
        - AC nonneg-sums-all-transactions — The balance is the sum of all transactions, so a positive total passes even with a negative row.
            assertion: persistence.db.PersistenceError: FEATURE-LEDGER-008 failed: no such table: categories
            raised at: db.py:248
            process exit code: 1
            error: persistence.db.PersistenceError: FEATURE-LEDGER-008 failed: no such table: categories
            values at failure:
              operation = Operation(identifier='FEATURE-LEDGER-008', table='categories', verb='create', inputs=('category', 'description'), row=<class 'persistence.schema.CategoryRow'>, columns=('category', 'description'), key=None)
            check stderr:
              Traceback (most recent call last):
                File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 245, in run
                  return self._dispatch(operation, cursor, connection, names, values)
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 280, in _dispatch
                  cursor.execute(self._driver.insert(table, names, key), values)
              sqlite3.OperationalError: no such table: categories
              The above exception was the direct cause of the following exception:
              Traceback (most recent call last):
                File "nonneg-sums-all-transactions.py", line 9, in <module>
                  db.categories.create(category="OPENING", description="Opening balance")
                File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 186, in <lambda>
                  return lambda **arguments: self._database.run(operation, arguments)
                                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 248, in run
                  raise PersistenceError(f"{operation.identifier} failed: {exc}") from exc
              persistence.db.PersistenceError: FEATURE-LEDGER-008 failed: no such table: categories
        - AC nonneg-rejection-changes-nothing — A rejected check leaves every transaction row unchanged.
            assertion: persistence.db.PersistenceError: FEATURE-LEDGER-008 failed: no such table: categories
            raised at: db.py:248
            process exit code: 1
            error: persistence.db.PersistenceError: FEATURE-LEDGER-008 failed: no such table: categories
            values at failure:
              operation = Operation(identifier='FEATURE-LEDGER-008', table='categories', verb='create', inputs=('category', 'description'), row=<class 'persistence.schema.CategoryRow'>, columns=('category', 'description'), key=None)
            check stderr:
              Traceback (most recent call last):
                File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 245, in run
                  return self._dispatch(operation, cursor, connection, names, values)
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 280, in _dispatch
                  cursor.execute(self._driver.insert(table, names, key), values)
              sqlite3.OperationalError: no such table: categories
              The above exception was the direct cause of the following exception:
              Traceback (most recent call last):
                File "nonneg-rejection-changes-nothing.py", line 9, in <module>
                  db.categories.create(category="OPENING", description="Opening balance")
                File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 186, in <lambda>
                  return lambda **arguments: self._database.run(operation, arguments)
                                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/persistence/db.py", line 248, in run
                  raise PersistenceError(f"{operation.identifier} failed: {exc}") from exc
              persistence.db.PersistenceError: FEATURE-LEDGER-008 failed: no such table: categories

## Build summary
This is the same repair request as the last two passes, and the failure is unchanged. I'll confirm the build directory and the generated `open_database` are still in the same state before reporting.The `git status` output is empty, but last pass it listed `balance.py` and `tests/test_balance.py` as untracked. I need to find out why before reporting.The files are intact. The harness checkpointed them into commit `0808893` (`Build block-9: FEATURE-NonNegativeBalance.md [failed]`), so the working tree is clean.

No files changed in this pass. The four declared checks still fail, and the fix is outside this block.

- **Cause:** each staged script calls `open_database(path)` on a fresh file and then creates a category. The generated `open_database` (`persistence/schema.py:153`) only builds the `Database` object and never applies `schema.sql`. The first insert hits a store with no tables.
- **Why I didn't edit it:** `persistence/schema.py` and `persistence/db.py` are generated or shipped and marked do-not-edit. Making the checks pass would mean changing generated code or the criteria, and neither is this block's to change.
- **Not `AC_BROKEN`:** the scripts raise during setup, so the assertions never run. The token is for a command that succeeds while its assertion fails.
- **`nonneg-accepts-zero-balance`:** the feedback reports this one as "excluded check: ALWAYS_PASSES vacuous". That comes from the harness, not from the balance code. The script has no assertion that could fail, so I cannot make it meaningful from this block.
- **Verified:** with the schema applied, the same script bodies passed in the earlier pass. `sh bin/test.sh` still reports 227 passed.

To unblock, the persistence generator (or `DATABASE.md`) must apply the declared schema when `open_database` opens a fresh store. Alternatively, the criteria must open their store through `persistence.testing.db_session()`. Then rerun this block.

RESULT: FAILED

FILES CHANGED:
- (none in this pass)

SUMMARY:
Rechecked the build directory. `balance.py` and `tests/test_balance.py` are present and unchanged from the previous pass, and `sh bin/test.sh` reports 227 passed. The four declared checks still fail at setup on `open_database(path)`, which does not apply the declared schema to a fresh store. Nothing in this block's files can fix that without editing generated persistence code.

BLOCKERS:
- The staged acceptance checks cannot run until `open_database` on a fresh store applies the declared schema, or until the criteria open their store through `persistence.testing.db_session()`. Both changes are outside this block.

FAILURE_SUMMARY: Staged acceptance checks fail at setup because `open_database` does not apply the declared schema to a fresh store.
FAILURE_DETAIL: Each check creates a category on a store with no tables, so it raises `no such table: categories` before `ensure_non_negative` is reached. `persistence/schema.py` and `persistence/db.py` are generated or shipped and must not be hand-edited. Before rerunning, the Drydock persistence generation must make `open_database` apply `schema.sql` to a new store, or the criteria must open their store through `db_session()`. Also, `nonneg-accepts-zero-balance` is reported as vacuous by the harness; that criterion has no assertion that can fail, so it needs repair in the Blueprint.
