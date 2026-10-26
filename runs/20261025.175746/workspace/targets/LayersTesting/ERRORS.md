# BIG ERRORS — action required

- Command: `build`
- Phase: build step
- State: Failed
- Timestamp: 2026-10-25T18:39:02+00:00
- Execution ID: 20261025.183727.078Z-7deb4acd
- Challenge Execution ID: -
- Classification: programmatic acceptance failed: release-full-grader
- Evidence / logs: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/workspace/targets/LayersTesting/evidence/block-5.md

## Diagnostic

Block "Block 5 · Feature" [block-5] failed its acceptance criteria.
  Story "Terminal gate running the full supplied grader." [release-verification] does not meet its own acceptance criteria:
    - AC release-full-grader — The completed ledger passes every check of the supplied end-to-end grader, which exits zero only when all 43 checks pass.
        assertion: assert result.returncode == 0 → AssertionError
        cases: pass=1 fail=3 total=4 from=result.stdout
        raised at: release-full-grader.py:13
        process exit code: 1
        values at failure:
… (20 more lines truncated)

## Recovery

Run: drydock build LayersTesting
  to continue the build. This story resumes where it left off and is retried against the checks it failed.
