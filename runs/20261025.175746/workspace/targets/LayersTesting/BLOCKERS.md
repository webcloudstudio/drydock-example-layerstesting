# Blockers: Uat Stage
- target: LayersTesting
- source: drydock uat LayersTesting
- declared: 2026-10-25T14:39:08-04:00

<!-- drydock-state: {"owner": "uat LayersTesting", "execution": "", "attempts": 1} -->

## blocker-001: initial-build-1
- kind: environmental
- class: uat stage
- auto-continue: no

### Error

drydock build LayersTesting exited 1.

stderr:
error: build failed for LayersTesting: 1 step(s)
  release-verification — closed/failed: programmatic acceptance failed: release-full-grader

Evidence:
  stderr: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/evidence/commands/10-initial-build-1.stderr.log
  stdout: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/evidence/commands/10-initial-build-1.stdout.log

### Why blocked

The build did not complete. UAT stopped before acceptance tests and scoring because the application is unfinished. Resolve the build error above before rerunning UAT.
