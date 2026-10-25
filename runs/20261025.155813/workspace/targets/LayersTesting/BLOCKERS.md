# Blockers: Login Required
- target: LayersTesting
- source: drydock plan LayersTesting --override --plan-override-model sonnet
- declared: 2026-10-25T12:00:40-04:00

<!-- drydock-state: {"owner": "plan LayersTesting", "execution": "20261025.160037.802Z-c543153b", "attempts": 1} -->

## blocker-001: Provider login expired
- kind: environmental
- class: provider authentication required
- auto-continue: no

### Error

provider error: Failed to authenticate: OAuth session expired and could not be refreshed
