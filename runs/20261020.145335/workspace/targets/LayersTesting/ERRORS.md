# BIG ERRORS — action required

- Command: `build`
- Phase: build step
- State: Failed
- Timestamp: 2026-10-20T15:27:46+00:00
- Execution ID: 20261020.152655.059Z-e4891cc5
- Challenge Execution ID: -
- Classification: programmatic acceptance failed: nonneg-rejects-negative-balance, nonneg-sums-all-transactions, nonneg-rejection-changes-nothing
- Evidence / logs: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/workspace/targets/LayersTesting/evidence/block-9.md

## Diagnostic

Block "Block 9 · Service" [block-9] failed its acceptance criteria.
  Story "Reject any command that would leave an account balance below zero." [INTEG-002] does not meet its own acceptance criteria:
    - AC nonneg-rejects-negative-balance — A balance below zero raises RejectedError with exit code 3.
        assertion: persistence.db.PersistenceError: FEATURE-LEDGER-008 failed: no such table: categories
        raised at: db.py:248
        process exit code: 1
        error: persistence.db.PersistenceError: FEATURE-LEDGER-008 failed: no such table: categories
        values at failure:
… (69 more lines truncated)

## Recovery

Run: drydock build LayersTesting
  to continue the build. This story resumes where it left off and is retried against the checks it failed.
