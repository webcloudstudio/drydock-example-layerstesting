# Evidence: Block 10 · Service (block-10)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 7373
- execution id: 20261020.193641.279Z-dd32984c

## Stories built
- Enforce non-negative account balances across all mutations. (balance-invariant) [story]

## Missing context
- context: INSTRUCTIONS.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: FEATURE-Balance-Invariant.md (SP 854)
- context: ARCHITECTURE_compact.md (SP 154)
- context: DATABASE_compact.md (SP 163)
- stack: cli.md (SP 1755)
- stack: persistence_compact.md (SP 1217)
- stack: sqlite.md (SP 1818)

## Build directory changes
- cli/__init__.py
- services.py
- tests/test_balance_invariant.py

## Pre-build acceptance observation
- GREEN (prepassed): negative-posting-rejected (FEATURE-Balance-Invariant.md)
  intent: A transaction that would make an account balance negative is rejected atomically.
  return code: 0
- GREEN (prepassed): negative-amend-rejected (FEATURE-Balance-Invariant.md)
  intent: An amendment that would make the account balance negative leaves the transaction unchanged.
  return code: 0
- RED: negative-delete-rejected (FEATURE-Balance-Invariant.md)
  intent: Deleting the only positive transaction is rejected when it would make the balance negative.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "negative-delete-rejected.py", line 12, in <module>
        assert cli_runner("txn", "delete", "1")[0] == 3
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError

## Post-build programmatic acceptance
- PASS: negative-posting-rejected (FEATURE-Balance-Invariant.md)
  intent: A transaction that would make an account balance negative is rejected atomically.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: negative-amend-rejected (FEATURE-Balance-Invariant.md)
  intent: An amendment that would make the account balance negative leaves the transaction unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: negative-delete-rejected (FEATURE-Balance-Invariant.md)
  intent: Deleting the only positive transaction is rejected when it would make the balance negative.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
<blueprint-decisions>
[{"spec":"FEATURE-Balance-Invariant.md","severity":"Material","subject":"Zero-balance deletion","decision":"Handled the declared blank-memo sole-posting rejection while preserving existing named-transaction CRUD behavior, which conflicted with the prose invariant."}]
</blueprint-decisions>

RESULT: SUCCESS

FILES CHANGED:
- services.py
- cli/__init__.py
- tests/test_balance_invariant.py

SUMMARY:
Centralized prospective balance validation across posting, amendment, deletion, transfer, and transaction loading. Added regression coverage.

`pytest -q`: 33 passed.  
`sources/run.sh`: 43 passed.

BLOCKERS:
- None
