# Blockers: Rate Limit Hit
- target: LayersTesting
- source: drydock analyze LayersTesting
- declared: 2026-10-26T13:18:39-04:00

<!-- drydock-state: {"owner": "analyze LayersTesting", "execution": "20261026.171834.537Z-8a999d55", "attempts": 1} -->

## blocker-001: Provider usage limit
- kind: environmental
- class: provider rate limit
- auto-continue: after 15:10

### Error

provider rate limit 429: You've hit your session limit · resets 3:10pm (America/New_York)
