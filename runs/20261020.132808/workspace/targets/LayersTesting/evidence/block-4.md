# Evidence: Block 4 · Service (block-4)

- block type: block
- date: 2026-10-20
- resulting state: closed/failed
- story points (combined assembled cost): 4597
- execution id: 20261020.135726.891Z-d04d1df0

## Stories built
- Run every command in one database transaction that rolls back on any failure. (db-transaction) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1145)
- implements: FEATURE-Command-Transaction.md (SP 1427)
- context: ARCHITECTURE_compact.md (SP 367)
- context: DATABASE_compact.md (SP 668)

## Build directory changes
- data/logs/lint_2026-10-20_095619.log
- data/logs/lint_2026-10-20_095652.log
- data/logs/lint_2026-10-20_095735.log
- data/logs/test_2026-10-20_095616.log
- data/logs/test_2026-10-20_095648.log
- data/logs/test_2026-10-20_095731.log
- tests/test_command_transaction.py
- transaction.py

## Pre-build acceptance observation
- RED: command-transaction-commits (FEATURE-Command-Transaction.md)
  intent: A command that returns normally has its write persisted and its return value passed back to the caller.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "command-transaction-commits.py", line 2, in <module>
        from transaction import run_command
    ModuleNotFoundError: No module named 'transaction'
- RED: command-transaction-rolls-back-all-writes (FEATURE-Command-Transaction.md)
  intent: When a command raises after two writes, neither write persists and the exception reaches the caller.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "command-transaction-rolls-back-all-writes.py", line 2, in <module>
        from transaction import run_command
    ModuleNotFoundError: No module named 'transaction'
- RED: command-transaction-propagates-exception (FEATURE-Command-Transaction.md)
  intent: The exception raised by a failing command is the same object the caller receives, not a wrapped or swallowed error.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "command-transaction-propagates-exception.py", line 2, in <module>
        from transaction import run_command
    ModuleNotFoundError: No module named 'transaction'

## Post-build programmatic acceptance
- FAIL: command-transaction-commits (FEATURE-Command-Transaction.md)
  intent: A command that returns normally has its write persisted and its return value passed back to the caller.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.132808/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 1
  stderr:
    --- drydock: values at failure ---
      account_code = 'TXNA1'
      result = 1
    --- drydock: end values ---
    Traceback (most recent call last):
      File "command-transaction-commits.py", line 9, in <module>
        assert result.account == account_code
               ^^^^^^^^^^^^^^
    AttributeError: 'int' object has no attribute 'account'
- PASS: command-transaction-rolls-back-all-writes (FEATURE-Command-Transaction.md)
  intent: When a command raises after two writes, neither write persists and the exception reaches the caller.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.132808/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: command-transaction-propagates-exception (FEATURE-Command-Transaction.md)
  intent: The exception raised by a failing command is the same object the caller receives, not a wrapped or swallowed error.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.132808/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0

## Repair attempts
- attempt 0 (initial build): failed; 2/3 checks model=claude-haiku-5-5; execution 20261020.135416.160Z-3e4560fc; reason: programmatic acceptance failed: command-transaction-commits
- attempt 1 (repair 1): failed; 2/3 checks model=claude-haiku-5-5; execution 20261020.135644.141Z-54e6215e; reason: programmatic acceptance failed: command-transaction-commits
- attempt 2 (repair 2): failed; 2/3 checks model=claude-haiku-5-5; execution 20261020.135726.891Z-d04d1df0; stopped: deterministic acceptance score did not improve on 2 consecutive calls; reason: programmatic acceptance failed: command-transaction-commits

## Failure
- summary: programmatic acceptance failed: command-transaction-commits
- detail:
    Block "Block 4 · Service" [block-4] failed its acceptance criteria.
      Story "Run every command in one database transaction that rolls back on any failure." [db-transaction] does not meet its own acceptance criteria:
        - AC command-transaction-commits — A command that returns normally has its write persisted and its return value passed back to the caller.
            assertion: assert result.account == account_code → AttributeError: 'int' object has no attribute 'account'
            raised at: command-transaction-commits.py:9
            process exit code: 1
            error: AttributeError: 'int' object has no attribute 'account'
            values at failure:
              account_code = 'TXNA1'
              result = 1
            check stderr:
              Traceback (most recent call last):
                File "command-transaction-commits.py", line 9, in <module>
                  assert result.account == account_code
                         ^^^^^^^^^^^^^^
              AttributeError: 'int' object has no attribute 'account'

## Build summary
This is the same failing criterion from the last two passes. I'll rerun it once more to confirm nothing has changed, then stop rather than loop.RESULT: SUCCESS

AC_BROKEN: command-transaction-commits

FILES CHANGED:
- (none this pass; the implementation is unchanged from the previous pass)

SUMMARY:
- `transaction.run_command(db, command)` is complete. It commits once when the command returns, and rolls back and re-raises on any exception. A persistence error such as a lock held by another connection also rolls back and propagates.
- Declared criteria, rerun verbatim:
  - `command-transaction-rolls-back-all-writes`: passes.
  - `command-transaction-propagates-exception`: passes.
  - `command-transaction-commits`: fails at `assert result.account == account_code` with `AttributeError: 'int' object has no attribute 'account'`.
- `sh bin/test.sh`: 93 passed, exit 0 (includes 16 new tests in `tests/test_command_transaction.py`).
- I did not edit the criterion, the spec, or the shipped persistence package.

<blueprint-decisions>
[{"spec":"FEATURE-Command-Transaction.md","severity":"Material","subject":"Deferred-commit view over the shipped Database","decision":"The shipped Database commits after each write, so run_command gives the command a Database built on a driver whose connection commit() is deferred, then commits or rolls back the real connection once. I did not edit the shipped persistence package. Is that acceptable, or should the persistence layer gain a transaction scope instead?"},{"spec":"FEATURE-Command-Transaction.md","severity":"Low","subject":"Module name","decision":"Named the module transaction.py to match the acceptance criteria import, not ARCHITECTURE.md's command_transaction. Should the architecture name be used on replan?"}]
</blueprint-decisions>

FAILURE_DETAIL: AC_BROKEN covers only `command-transaction-commits`. The command succeeds: the row is persisted, and `run_command` returns the value `create` returned. The assertion `result.account == account_code` fails because the shipped `accounts.create` returns the SQLite integer `lastrowid`, and the spec requires `run_command` to return the command's value unchanged. No spec-compliant implementation can satisfy that line. The fix is in the Blueprint: either the criterion checks the persisted row rather than `result.account`, or the `accounts.create` return contract in DATABASE.md changes. I have not rerun the build beyond the checks above, and I will not keep repairing this criterion.

BLOCKERS:
- `command-transaction-commits` cannot pass as written. It needs a criterion or `create` return-contract fix on replan.
