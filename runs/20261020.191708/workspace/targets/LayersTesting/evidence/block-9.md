# Evidence: Block 9 · Service (block-9)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 7526
- execution id: 20261020.193443.176Z-1dc7e7f9

## Stories built
- Post, read, amend, and delete ledger transactions. (transaction-management) [story]

## Missing context
- context: INSTRUCTIONS.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: FEATURE-Transaction-Management.md (SP 1007)
- context: ARCHITECTURE_compact.md (SP 154)
- context: DATABASE_compact.md (SP 163)
- stack: cli.md (SP 1755)
- stack: persistence_compact.md (SP 1217)
- stack: sqlite.md (SP 1818)

## Build directory changes
- cli/__init__.py
- tests/test_transaction_management.py
- validation.py

## Pre-build acceptance observation
- GREEN (prepassed): transaction-crud-roundtrip (FEATURE-Transaction-Management.md)
  intent: Posting, reading, amending, and deleting a transaction persist the documented fields.
  return code: 0
- GREEN (prepassed): transaction-validation (FEATURE-Transaction-Management.md)
  intent: Invalid references, amounts, dates, memos, and absent identifiers are rejected.
  return code: 0
- GREEN (prepassed): transaction-id-generation (FEATURE-Transaction-Management.md)
  intent: A posted transaction receives the next identifier after existing rows.
  return code: 0

## Post-build programmatic acceptance
- PASS: transaction-crud-roundtrip (FEATURE-Transaction-Management.md)
  intent: Posting, reading, amending, and deleting a transaction persist the documented fields.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transaction-validation (FEATURE-Transaction-Management.md)
  intent: Invalid references, amounts, dates, memos, and absent identifiers are rejected.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transaction-id-generation (FEATURE-Transaction-Management.md)
  intent: A posted transaction receives the next identifier after existing rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
RESULT: SUCCESS

FILES CHANGED:
- cli/__init__.py
- validation.py
- tests/test_transaction_management.py

SUMMARY:
Implemented transaction validation and exact integer-cent formatting. Added CRUD, atomic rejection, and field-preservation tests.

Verification: `30 passed`; terminal harness `43 passed, 0 failed`.

BLOCKERS:
- None
