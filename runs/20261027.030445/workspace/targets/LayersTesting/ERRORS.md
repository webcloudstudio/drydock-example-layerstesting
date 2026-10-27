# BIG ERRORS — action required

- Command: `plan`
- Phase: plan verify
- State: Error
- Timestamp: 2026-10-27T03:21:52+00:00
- Execution ID: 20261027.030722.960Z-9740bc17
- Challenge Execution ID: -
- Classification: plan cannot be built as written
- Evidence / logs: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.030445/workspace/logs

## Diagnostic

plan verify: LayersTesting
  7 criteria cannot run as written
  ✗  FEATURE-DatabaseSelection.md [config-url-prefix-stripped]: criterion changes the configured database; use the provisioned store
  ✗  FEATURE-DatabaseSelection.md [config-url-without-prefix]: criterion changes the configured database; use the provisioned store
  ✗  FEATURE-DatabaseSelection.md [config-database-path-fallback]: criterion changes the configured database; use the provisioned store
  ✗  FEATURE-DatabaseSelection.md [config-default-path]: criterion changes the configured database; use the provisioned store
  ✗  FEATURE-DatabaseSelection.md [config-open-store-unavailable]: criterion changes the configured database; use the provisioned store
  ✗  FEATURE-LedgerCount.md [count-store-unavailable]: criterion changes the configured database; use the provisioned store
  ✗  FEATURE-LedgerInit.md [init-store-unavailable]: criterion changes the configured database; use the provisioned store
  Run: drydock plan repair LayersTesting

## Recovery

Run: drydock plan repair LayersTesting
