# Evidence: Block 6 · Service (block-6)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 8792
- execution id: 20261020.193039.079Z-e18e6928

## Stories built
- Load and validate account and category CSV files atomically. (account-loading) [story]

## Reusable compacts
- seed_accounts_compact.md
- seed_categories_compact.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: FEATURE-Account-Category-Loading.md (SP 1019)
- context: seed_accounts.csv (SP 22)
- context: seed_categories.csv (SP 40)
- context: ARCHITECTURE_compact.md (SP 154)
- context: DATABASE_compact.md (SP 163)
- stack: cli.md (SP 1755)
- stack: persistence.md (SP 2407)
- stack: sqlite.md (SP 1818)

## Build directory changes
- cli/__init__.py
- tests/test_account_category_loading.py

## Pre-build acceptance observation
- GREEN (prepassed): account-category-load-roundtrip (FEATURE-Account-Category-Loading.md)
  intent: Valid account and category files are loaded and their persisted rows are readable.
  return code: 0
- RED: account-category-load-rejects-without-write (FEATURE-Account-Category-Loading.md)
  intent: An unreadable or invalid master-data file is rejected without changing persisted data.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      d = '/tmp/tmpciy4d2d_'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-category-load-rejects-without-write.py", line 17, in <module>
        assert cli_runner("load", "accounts", str(Path(d) / "missing.csv"))[0] == 1
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: account-category-load-validation (FEATURE-Account-Category-Loading.md)
  intent: Duplicate and invalid master-data fields return the rejected-command status.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      invalid = PosixPath('/tmp/tmp0hq5x03f/invalid.csv')
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-category-load-validation.py", line 14, in <module>
        assert cli_runner("load", "categories", str(invalid))[0] == 3
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError

## Post-build programmatic acceptance
- PASS: account-category-load-roundtrip (FEATURE-Account-Category-Loading.md)
  intent: Valid account and category files are loaded and their persisted rows are readable.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-category-load-rejects-without-write (FEATURE-Account-Category-Loading.md)
  intent: An unreadable or invalid master-data file is rejected without changing persisted data.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-category-load-validation (FEATURE-Account-Category-Loading.md)
  intent: Duplicate and invalid master-data fields return the rejected-command status.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
<reusable-compact filename="seed_accounts.csv">
CSV contract: header `account,name`; account codes are uppercase alphanumeric, 1–12 characters; names are non-empty, up to 40 characters. Seed rows: DRAWER1, DRAWER2, PETTY, SAFE.
</reusable-compact>

<reusable-compact filename="seed_categories.csv">
CSV contract: header `category,description`; category codes are uppercase alphanumeric, 1–12 characters; descriptions are non-empty, up to 40 characters. Seed categories: OPENING, PAYROLL, REFUND, RENT, SALES, SUPPLY, TRANSFER.
</reusable-compact>

RESULT: SUCCESS

FILES CHANGED:
- cli/__init__.py
- tests/test_account_category_loading.py

SUMMARY:
Implemented strict, atomic-style prevalidated account/category CSV loading with exact headers, validation, duplicate/conflict rejection, and correct error classification. Tests pass; staged grader reports 43/43 checks passed.

BLOCKERS:
- None
