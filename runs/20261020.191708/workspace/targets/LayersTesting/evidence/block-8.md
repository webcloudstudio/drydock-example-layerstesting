# Evidence: Block 8 · Service (block-8)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 7436
- execution id: 20261020.193309.606Z-09487d6c

## Stories built
- Add, read, rename, and delete ledger accounts. (account-management) [story]

## Missing context
- context: INSTRUCTIONS.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: FEATURE-Account-Management.md (SP 928)
- context: ARCHITECTURE_compact.md (SP 154)
- context: DATABASE_compact.md (SP 163)
- stack: cli.md (SP 1755)
- stack: persistence_compact.md (SP 1217)
- stack: sqlite.md (SP 1818)

## Build directory changes
- cli/__init__.py
- tests/test_account_management.py
- validation.py

## Pre-build acceptance observation
- GREEN (prepassed): account-crud-roundtrip (FEATURE-Account-Management.md)
  intent: Account creation, retrieval, rename, and deletion persist through the public CLI.
  return code: 0
- GREEN (prepassed): account-rejection-contract (FEATURE-Account-Management.md)
  intent: Duplicate, invalid, absent, and in-use account operations return their specified statuses.
  return code: 0
- RED: account-in-use-protection (FEATURE-Account-Management.md)
  intent: An account with a transaction cannot be deleted.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "account-in-use-protection.py", line 12, in <module>
        assert cli_runner("txn", "post", "A1", "C1", "1.00", "2026-01-01")[0] == 0
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError

## Post-build programmatic acceptance
- PASS: account-crud-roundtrip (FEATURE-Account-Management.md)
  intent: Account creation, retrieval, rename, and deletion persist through the public CLI.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-rejection-contract (FEATURE-Account-Management.md)
  intent: Duplicate, invalid, absent, and in-use account operations return their specified statuses.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-in-use-protection (FEATURE-Account-Management.md)
  intent: An account with a transaction cannot be deleted.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
RESULT: SUCCESS

FILES CHANGED:
- cli/__init__.py
- validation.py
- tests/test_account_management.py

SUMMARY:
Implemented account CRUD validation, balance reporting, duplicate/not-found handling, and transaction-use deletion protection. Added supporting category creation and comprehensive tests.

Verified: project tests passed; all 43 harness checks passed; declared account acceptance passed.

BLOCKERS:
- None
