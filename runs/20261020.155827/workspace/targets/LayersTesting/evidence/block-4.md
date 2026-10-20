# Evidence: Block 4 · Service (block-4)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 10789
- execution id: 20261020.160903.596Z-4e5344b0

## Stories built
- Load account and category CSV data atomically. (account-category-load) [story]

## Reusable compacts
- seed_accounts_compact.md
- seed_categories_compact.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 747)
- implements: FEATURE-ACCOUNT-CATEGORY-LOAD.md (SP 1239)
- context: seed_accounts.csv (SP 22)
- context: seed_categories.csv (SP 40)
- context: ARCHITECTURE_compact.md (SP 130)
- context: DATABASE_compact.md (SP 156)
- stack: common.md (SP 1812)
- stack: cli.md (SP 1755)
- stack: persistence.md (SP 2407)
- stack: sqlite.md (SP 1818)

## Build directory changes
- cli.py
- services.py
- tests/test_account_category_load.py
- validation.py

## Pre-build acceptance observation
- GREEN (prepassed): load-accounts-round-trip (FEATURE-ACCOUNT-CATEGORY-LOAD.md)
  intent: A valid account CSV loads and becomes visible in the count and account interface.
  return code: 0
  stdout:
    table,loaded
    accounts,2
    
    
    table,rows
    accounts,2
    categories,0
    transactions,0
- GREEN (prepassed): load-categories-round-trip (FEATURE-ACCOUNT-CATEGORY-LOAD.md)
  intent: A valid category CSV loads and becomes visible in the count.
  return code: 0
  stdout:
    table,loaded
    categories,2
    
    
    table,rows
    accounts,0
    categories,2
    transactions,0
- GREEN (prepassed): load-rollback-invalid (FEATURE-ACCOUNT-CATEGORY-LOAD.md)
  intent: A rejected account batch leaves the target table unchanged.
  return code: 0
  stdout:
    error: invalid code
    
    table,rows
    accounts,0
    categories,0
    transactions,0

## Post-build programmatic acceptance
- PASS: load-accounts-round-trip (FEATURE-ACCOUNT-CATEGORY-LOAD.md)
  intent: A valid account CSV loads and becomes visible in the count and account interface.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    table,loaded
    accounts,2
    
    
    table,rows
    accounts,2
    categories,0
    transactions,0
- PASS: load-categories-round-trip (FEATURE-ACCOUNT-CATEGORY-LOAD.md)
  intent: A valid category CSV loads and becomes visible in the count.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    table,loaded
    categories,2
    
    
    table,rows
    accounts,0
    categories,2
    transactions,0
- PASS: load-rollback-invalid (FEATURE-ACCOUNT-CATEGORY-LOAD.md)
  intent: A rejected account batch leaves the target table unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: invalid code
    
    table,rows
    accounts,0
    categories,0
    transactions,0

## Build summary
<reusable-compact filename="seed_accounts.csv">
Accounts CSV header: `account,name`. Seed rows use uppercase account codes and names.
</reusable-compact>

<reusable-compact filename="seed_categories.csv">
Categories CSV header: `category,description`. Seed rows use uppercase category codes and descriptions.
</reusable-compact>

RESULT: SUCCESS

FILES CHANGED:
- cli.py
- services.py
- validation.py
- tests/test_account_category_load.py

SUMMARY:
Implemented atomic account/category CSV loading with strict validation, duplicate detection, rollback, and correct exit codes. Tests passed: 12 project tests and 43/43 terminal checks.

BLOCKERS:
- None
