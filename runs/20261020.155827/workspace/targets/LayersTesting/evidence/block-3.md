# Evidence: Block 3 · Service (block-3)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 10521
- execution id: 20261020.160752.768Z-b5882f97

## Stories built
- Initialize and count the ledger schema. (schema-lifecycle) [story]

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 747)
- implements: FEATURE-SCHEMA-LIFECYCLE.md (SP 1048)
- context: ARCHITECTURE_compact.md (SP 130)
- context: DATABASE_compact.md (SP 156)
- stack: common.md (SP 1812)
- stack: cli.md (SP 1755)
- stack: persistence.md (SP 2407)
- stack: sqlite.md (SP 1818)

## Build directory changes
- cli.py
- services.py
- tests/test_schema_lifecycle.py

## Pre-build acceptance observation
- GREEN (prepassed): schema-init-empty (FEATURE-SCHEMA-LIFECYCLE.md)
  intent: Initialization creates an empty ledger schema and emits no output.
  return code: 0
  stdout:
    table,rows
    accounts,0
    categories,0
    transactions,0
- GREEN (prepassed): schema-count-order (FEATURE-SCHEMA-LIFECYCLE.md)
  intent: Count reports all declared tables in the required order.
  return code: 0
  stdout:
    table,rows
    accounts,0
    categories,0
    transactions,0
- GREEN (prepassed): schema-reinitializes (FEATURE-SCHEMA-LIFECYCLE.md)
  intent: A later initialization removes previously stored rows.
  return code: 0
  stdout:
    account,name,transactions,balance
    TEMP,Temporary,0,0.00
    
    
    
    
    table,rows
    accounts,0
    categories,0
    transactions,0

## Post-build programmatic acceptance
- PASS: schema-init-empty (FEATURE-SCHEMA-LIFECYCLE.md)
  intent: Initialization creates an empty ledger schema and emits no output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    table,rows
    accounts,0
    categories,0
    transactions,0
- PASS: schema-count-order (FEATURE-SCHEMA-LIFECYCLE.md)
  intent: Count reports all declared tables in the required order.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    table,rows
    accounts,0
    categories,0
    transactions,0
- PASS: schema-reinitializes (FEATURE-SCHEMA-LIFECYCLE.md)
  intent: A later initialization removes previously stored rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    TEMP,Temporary,0,0.00
    
    
    
    
    table,rows
    accounts,0
    categories,0
    transactions,0

## Build summary
RESULT: SUCCESS

FILES CHANGED:
- cli.py
- services.py
- tests/test_schema_lifecycle.py

SUMMARY:
Implemented explicit schema initialization and ordered row counting. Added lifecycle tests covering empty initialization, ordering, and reinitialization.

Verification:
- `sh bin/test.sh` — passed
- `sh sources/run.sh` — 43/43 passed

BLOCKERS:
- None
