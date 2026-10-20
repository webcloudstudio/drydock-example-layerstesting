# Evidence: Block 7 · Service (block-7)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 9276
- execution id: 20261020.193204.652Z-f4cb03fb

## Stories built
- Load and validate transaction CSV files atomically. (transaction-loading) [story]

## Reusable compacts
- seed_transactions_compact.md
- seed_transactions_bad_compact.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: FEATURE-Transaction-Loading.md (SP 1174)
- context: seed_transactions.csv (SP 1425)
- context: seed_transactions_bad.csv (SP 141)
- context: ARCHITECTURE_compact.md (SP 154)
- context: DATABASE_compact.md (SP 163)
- stack: cli.md (SP 1755)
- stack: persistence_compact.md (SP 1217)
- stack: sqlite.md (SP 1818)

## Build directory changes
- cli/__init__.py
- tests/test_transaction_loading.py

## Pre-build acceptance observation
- GREEN (prepassed): transaction-load-roundtrip (FEATURE-Transaction-Loading.md)
  intent: A valid transaction file persists integer-cent data and remains readable.
  return code: 0
- GREEN (prepassed): transaction-load-atomic-rejection (FEATURE-Transaction-Loading.md)
  intent: A later invalid reference rejects the entire transaction batch.
  return code: 0
- GREEN (prepassed): transaction-load-validation (FEATURE-Transaction-Loading.md)
  intent: Invalid dates, amounts, duplicate IDs, and negative prospective balances are rejected.
  return code: 0

## Post-build programmatic acceptance
- PASS: transaction-load-roundtrip (FEATURE-Transaction-Loading.md)
  intent: A valid transaction file persists integer-cent data and remains readable.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transaction-load-atomic-rejection (FEATURE-Transaction-Loading.md)
  intent: A later invalid reference rejects the entire transaction batch.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transaction-load-validation (FEATURE-Transaction-Loading.md)
  intent: Invalid dates, amounts, duplicate IDs, and negative prospective balances are rejected.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
<reusable-compact filename="seed_transactions.csv">
CSV contract: header `txn_id,date,account,category,amount,memo`; transaction IDs are integers, dates use ISO `YYYY-MM-DD`, amounts are decimal currency values converted to integer cents, accounts/categories reference existing master rows, and memos are strings. The staged dataset contains 120 valid transactions.
</reusable-compact>

<reusable-compact filename="seed_transactions_bad.csv">
CSV contract matches `seed_transactions.csv`. The staged dataset contains 11 rows: 10 valid transactions followed by one transaction referencing `NOSUCH`; the complete batch must be rejected atomically with no rows inserted.
</reusable-compact>

RESULT: SUCCESS

FILES CHANGED:
- cli/__init__.py
- tests/test_transaction_loading.py

SUMMARY:
Implemented exact transaction CSV header/row validation, integer-cent parsing, reference checks, duplicate detection, date/amount validation, prospective balance checks, and atomic rejection behavior. Project tests pass: 24 passed. Terminal acceptance passes: 43 passed, 0 failed.

BLOCKERS:
- None
