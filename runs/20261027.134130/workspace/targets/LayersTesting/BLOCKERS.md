# Blockers: Login Required
- target: LayersTesting
- source: drydock plan LayersTesting --override --plan-override-model sonnet
- declared: 2026-10-27T09:42:29-04:00

<!-- drydock-state: {"owner": "plan LayersTesting", "execution": "20261027.134225.992Z-24eeb4b7", "attempts": 1} -->

## blocker-001: Provider login expired
- kind: environmental
- class: provider authentication required
- auto-continue: no

### Error

provider error: Failed to authenticate: OAuth session expired and could not be refreshed
