# BIG ERRORS — action required

- Command: `build`
- Phase: build step
- State: Failed
- Timestamp: 2026-10-20T04:37:12+00:00
- Execution ID: 20261020.043648.991Z-80fda342
- Challenge Execution ID: -
- Classification: programmatic acceptance failed: db-selection-unreachable
- Evidence / logs: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/workspace/targets/LayersTesting/evidence/block-3.md

## Diagnostic

Block "Block 3 · Service" [block-3] failed its acceptance criteria.
  Story "Select the database from DATABASE_URL, DATABASE_PATH, or data/app.db." [foundation-002] does not meet its own acceptance criteria:
    - AC db-selection-unreachable — An unreachable PostgreSQL server raises PersistenceError instead of returning a database.
        assertion: psycopg.OperationalError: connection failed: connection to server at "127.0.0.1", port 1 failed: Connection refused
        cases: pass=0 fail=1 total=1 from=e.ConnStatus._member_map_
        raised at: connection.py:126
        process exit code: 1
        error: psycopg.OperationalError: connection failed: connection to server at "127.0.0.1", port 1 failed: Connection refused
        values at failure:
… (18 more lines truncated)

## Recovery

Run: drydock build LayersTesting
  to continue the build. This story resumes where it left off and is retried against the checks it failed.
