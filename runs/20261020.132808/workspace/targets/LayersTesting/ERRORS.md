# BIG ERRORS — action required

- Command: `build`
- Phase: build step
- State: Failed
- Timestamp: 2026-10-20T13:57:52+00:00
- Execution ID: 20261020.135726.891Z-d04d1df0
- Challenge Execution ID: -
- Classification: programmatic acceptance failed: command-transaction-commits
- Evidence / logs: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.132808/workspace/targets/LayersTesting/evidence/block-4.md

## Diagnostic

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
… (4 more lines truncated)

## Recovery

Run: drydock build LayersTesting
  to continue the build. This story resumes where it left off and is retried against the checks it failed.
