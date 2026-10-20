# Evidence: Block 8 · Service (block-8)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 4339
- execution id: 20261020.152247.642Z-e2257c63

## Stories built
- Run each command as one database transaction. (INTEG-001) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1145)
- implements: FEATURE-CommandTransaction.md (SP 1361)
- context: ARCHITECTURE_compact.md (SP 427)
- context: DATABASE_compact.md (SP 427)

## Build directory changes
- cli/transactional.py
- tests/test_transactional.py

## Pre-build acceptance observation
- RED: integ-txn-commit-on-success (FEATURE-CommandTransaction.md)
  intent: run_command commits the writes of a command that returns normally.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "integ-txn-commit-on-success.py", line 2, in <module>
        from cli.transactional import run_command
    ModuleNotFoundError: No module named 'cli.transactional'
- RED: integ-txn-rollback-single-table (FEATURE-CommandTransaction.md)
  intent: run_command rolls back a write made before the command raises, leaving the table empty.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "integ-txn-rollback-single-table.py", line 2, in <module>
        from cli.transactional import run_command
    ModuleNotFoundError: No module named 'cli.transactional'
- RED: integ-txn-rollback-multi-table (FEATURE-CommandTransaction.md)
  intent: run_command rolls back writes to two tables when the command raises after both writes.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "integ-txn-rollback-multi-table.py", line 2, in <module>
        from cli.transactional import run_command
    ModuleNotFoundError: No module named 'cli.transactional'

## Post-build programmatic acceptance
- PASS: integ-txn-commit-on-success (FEATURE-CommandTransaction.md)
  intent: run_command commits the writes of a command that returns normally.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: integ-txn-rollback-single-table (FEATURE-CommandTransaction.md)
  intent: run_command rolls back a write made before the command raises, leaving the table empty.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: integ-txn-rollback-multi-table (FEATURE-CommandTransaction.md)
  intent: run_command rolls back writes to two tables when the command raises after both writes.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
The shipped `Database` commits after every write, so a plain wrapper cannot roll back an earlier write in the same command. I'll hold the commit on the connection the persistence handle returns, for the duration of the command only, and decide the outcome once at the end.Now the tests, following the acceptance assertions plus the failure and cleanup cases.`run_command` is in place. Each command now commits or rolls back as one unit, and the full project suite passes.

I wrote `cli/transactional.py` and `tests/test_transactional.py`. The shipped `Database` commits after every write, so a plain try/except around the command cannot undo an earlier write. Instead, `run_command` holds the commit on the connection that the persistence handle returns, only for the duration of the command. The commit happens once at the end, and any exception rolls back everything. The driver's `connect` is restored afterwards, including on failure. I did not edit anything under `persistence/`.

<blueprint-decisions>
[{"spec":"FEATURE-CommandTransaction.md","severity":"Material","subject":"How atomicity is achieved over the shipped Database","decision":"The shipped persistence/db.py commits inside every create, update and delete, so wrapping the command alone cannot roll back an earlier write. I shadowed driver.connect for the duration of one command with a proxy that makes commit() a no-op, forwards everything else, and commits once after the command returns (or rolls back on any exception). The shadow is removed in a finally block. This needed no change to the shipped persistence files. Alternatives were editing db.py (forbidden: it is a Drydock-shipped file) or adding a transaction primitive to DATABASE.md (outside this step). Is this acceptable, or should it change on replan?"},{"spec":"FEATURE-CommandTransaction.md","severity":"Low","subject":"Module location versus ARCHITECTURE.md","decision":"The spec places run_command in cli.transactional, but ARCHITECTURE.md says cli/ has no DB access. I followed the spec and kept the module under cli/. It touches only the persistence handle, not a driver, so the import boundary holds."}]
</blueprint-decisions>

RESULT: SUCCESS

FILES CHANGED:
- cli/transactional.py
- tests/test_transactional.py

SUMMARY:
- `cli.transactional.run_command(db, command)` calls `command(db)` inside one transaction. It commits and returns the command's value on success. On any exception it rolls back and re-raises the same exception object.
- The new tests (11) cover the three declared acceptance assertions, plus:
  - rollback across multiple tables;
  - a `PersistenceError` raised mid-command rolling back earlier writes;
  - the driver's `connect` being restored after success and after failure;
  - a failed command leaving previously committed rows unchanged.
- Test results:
  - `.venv/bin/python -m pytest -q tests/test_transactional.py`: 11 passed.
  - `sh bin/test.sh` (the declared behavioral gate): 211 passed, 0 failed.
- I did not run `sh sources/run.sh`. That is the terminal story, not this block's gate.
- No files under `sources/`, `persistence/`, or other protected paths were touched. Nothing was committed.

BLOCKERS:
- None.
