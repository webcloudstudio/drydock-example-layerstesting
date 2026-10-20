# BIG ERRORS — action required

- Command: `build`
- Phase: build step
- State: Failed
- Timestamp: 2026-10-20T18:51:13+00:00
- Execution ID: 20261020.185011.302Z-be692017
- Challenge Execution ID: -
- Classification: programmatic acceptance failed: transaction-post-read
- Evidence / logs: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.183046/workspace/targets/LayersTesting/evidence/block-5.md

## Diagnostic

Block "Block 5 · Service" [block-5] failed its acceptance criteria.
  Story "Manage posting, lookup, amendment, and deletion of transactions." [transaction-lifecycle] does not meet its own acceptance criteria:
    - AC transaction-post-read — Posting a transaction allocates an id and a subsequent get reads the persisted row.
        assertion: assert cli_runner("load", "categories", "sources/seed_categories.csv")[0] == 1 → AssertionError
        raised at: transaction-post-read.py:13
        process exit code: 1
        check stderr:
          Traceback (most recent call last):
            File "transaction-post-read.py", line 13, in <module>
              assert cli_runner("load", "categories", "sources/seed_categories.csv")[0] == 1
… (2 more lines truncated)

## Recovery

Run: drydock build LayersTesting
  to continue the build. This story resumes where it left off and is retried against the checks it failed.
