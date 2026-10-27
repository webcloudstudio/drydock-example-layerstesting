# BIG ERRORS — action required

- Command: `plan`
- Phase: plan verify
- State: Error
- Timestamp: 2026-10-27T01:53:08+00:00
- Execution ID: 20261027.014929.359Z-842e60f3
- Challenge Execution ID: -
- Classification: plan cannot be built as written
- Evidence / logs: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.013358/workspace/logs

## Diagnostic

plan verify: LayersTesting
  4 criteria cannot run as written
  ✗  FEATURE-OperationalFailures.md [operational-postgres-refused]: criterion changes the configured database; use the provisioned store
  ✗  FEATURE-OperationalFailures.md [operational-unreachable-database]: criterion changes the configured database; use the provisioned store
  ✗  FEATURE-OperationalFailures.md [operational-invalid-database-file]: criterion changes the configured database; use the provisioned store
  ✗  FEATURE-OperationalFailures.md [operational-usage-before-database]: criterion changes the configured database; use the provisioned store
  Run: drydock plan repair LayersTesting

## Recovery

Run: drydock plan repair LayersTesting
