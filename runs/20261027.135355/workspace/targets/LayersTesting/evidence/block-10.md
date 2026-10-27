# Evidence: Block 10 · Feature (block-10)

- block type: block
- date: 2026-10-27
- resulting state: closed/verified
- story points (combined assembled cost): 8492
- execution id: 20261027.150502.024Z-a09c9eac

## Stories built
- Terminal gate: run the supplied grader and the full project test suite. (feature-verification) [story]

## Acceptance tooling authorization
- FEATURE-Verification.md#verification-full-suite: executable=sh; scope=test; authorization=existing Target environment

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1134)
- implements: FEATURE-Verification.md (SP 772)
- context: ARCHITECTURE_compact.md (SP 332)
- context: DATABASE_compact.md (SP 884)
- stack: common_compact.md (SP 1653)
- stack: cli.md (SP 2689)

## Build directory changes
- data/app.db-shm
- data/app.db-wal
- data/logs/test_2026-10-27_110524.log

## Pre-build acceptance observation
- GREEN (prepassed): verification-full-suite (FEATURE-Verification.md)
  intent: The supplied grader and the project's own test suite both exit zero when run from the application root against their own temporary databases.
  return code: 0
  stdout:
    PASS A1: ledger init
    PASS A2: ledger count
    PASS B1: ledger load accounts /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/sources/seed_accounts.csv
    PASS B2: ledger load categories /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/sources/seed_categories.csv
    PASS B3: ledger load transactions /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/sources/seed_transactions.csv
    PASS B4: ledger count
    PASS C1: ledger report balances
    PASS C2: ledger report categories
    PASS C3: ledger report monthly
    PASS D1: ledger load transactions /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/sources/seed_transactions_bad.csv
    PASS D2: ledger load accounts /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/sources/seed_accounts.csv
    PASS D3: ledger count
    PASS E1: ledger account add CASH9 Event Float
    PASS E2: ledger account add CASH9 Event Float
    PASS E3: ledger account get CASH9
    PASS E4: ledger account rename CASH9 Event Cash Box
    PASS E5: ledger account get NOSUCH
    PASS E6: ledger account delete DRAWER1
    PASS E7: ledger account delete CASH9
    PASS E8: ledger account get CASH9
    PASS F1: ledger txn post DRAWER1 SALES 45.50 2026-04-01 walk in sale
    PASS F2: ledger txn get 121
    PASS F3: ledger txn amend 121 54.50
    PASS F4: ledger txn get 999
    PASS F5: ledger txn post DRAWER1 NOSUCH 1.00 2026-04-01
    PASS F6: ledger txn post DRAWER1 SALES 1.234 2026-04-01
    PASS F7: ledger txn post DRAWER1 SALES 1.00 2026-02-30
    PASS F8: ledger txn delete 121
    PASS F9: ledger txn get 121
    PASS F10: ledger txn post PETTY SUPPLY -12.34 2026-04-02 tape
    PASS G1: ledger transfer DRAWER1 SAFE 500.00 2026-04-03
    PASS G2: ledger transfer SAFE PETTY 999.99 2026-04-04
    PASS G3: ledger txn post PETTY SUPPLY -1000.00 2026-04-04
    PASS G4: ledger txn amend 1 1.00
    PASS G5: ledger txn delete 1
    PASS G6: ledger count
    PASS H1: ledger report balances
    PASS H2: ledger report categories
    PASS H3: ledger report monthly
    PASS U1: ledger frobnicate
    PASS U2: ledger report nosuch
    PASS Z1: ledger init
    PASS Z2: ledger count
    LayersTesting: 43 passed, 0 failed (of 43)
    
    === test started at 2026-10-27 11:04:40 ===
    Arguments: 
    Working dir: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting
    ---
    ........................................................................ [ 16%]
    ........................................................................ [ 32%]
    ........................................................................ [ 48%]
    ........................................................................ [ 64%]
    ........................................................................ [ 80%]
    ........................................................................ [ 96%]
    .................                                                        [100%]
    449 passed in 14.00s
    === test finished at 2026-10-27 11:04:56 with exit 0 ===

## Post-build programmatic acceptance
- PASS: verification-full-suite (FEATURE-Verification.md)
  intent: The supplied grader and the project's own test suite both exit zero when run from the application root against their own temporary databases.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    PASS A1: ledger init
    PASS A2: ledger count
    PASS B1: ledger load accounts /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/sources/seed_accounts.csv
    PASS B2: ledger load categories /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/sources/seed_categories.csv
    PASS B3: ledger load transactions /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/sources/seed_transactions.csv
    PASS B4: ledger count
    PASS C1: ledger report balances
    PASS C2: ledger report categories
    PASS C3: ledger report monthly
    PASS D1: ledger load transactions /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/sources/seed_transactions_bad.csv
    PASS D2: ledger load accounts /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/sources/seed_accounts.csv
    PASS D3: ledger count
    PASS E1: ledger account add CASH9 Event Float
    PASS E2: ledger account add CASH9 Event Float
    PASS E3: ledger account get CASH9
    PASS E4: ledger account rename CASH9 Event Cash Box
    PASS E5: ledger account get NOSUCH
    PASS E6: ledger account delete DRAWER1
    PASS E7: ledger account delete CASH9
    PASS E8: ledger account get CASH9
    PASS F1: ledger txn post DRAWER1 SALES 45.50 2026-04-01 walk in sale
    PASS F2: ledger txn get 121
    PASS F3: ledger txn amend 121 54.50
    PASS F4: ledger txn get 999
    PASS F5: ledger txn post DRAWER1 NOSUCH 1.00 2026-04-01
    PASS F6: ledger txn post DRAWER1 SALES 1.234 2026-04-01
    PASS F7: ledger txn post DRAWER1 SALES 1.00 2026-02-30
    PASS F8: ledger txn delete 121
    PASS F9: ledger txn get 121
    PASS F10: ledger txn post PETTY SUPPLY -12.34 2026-04-02 tape
    PASS G1: ledger transfer DRAWER1 SAFE 500.00 2026-04-03
    PASS G2: ledger transfer SAFE PETTY 999.99 2026-04-04
    PASS G3: ledger txn post PETTY SUPPLY -1000.00 2026-04-04
    PASS G4: ledger txn amend 1 1.00
    PASS G5: ledger txn delete 1
    PASS G6: ledger count
    PASS H1: ledger report balances
    PASS H2: ledger report categories
    PASS H3: ledger report monthly
    PASS U1: ledger frobnicate
    PASS U2: ledger report nosuch
    PASS Z1: ledger init
    PASS Z2: ledger count
    LayersTesting: 43 passed, 0 failed (of 43)
    
    === test started at 2026-10-27 11:06:28 ===
    Arguments: 
    Working dir: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting
    ---
    ........................................................................ [ 16%]
    ........................................................................ [ 32%]
    ........................................................................ [ 48%]
    ........................................................................ [ 64%]
    ........................................................................ [ 80%]
    ........................................................................ [ 96%]
    .................                                                        [100%]
    449 passed in 14.02s
    === test finished at 2026-10-27 11:06:45 with exit 0 ===

## Build summary
I'll start by checking the build directory state and the existing test setup.Both scripts are in place. Now I'll run the grader and the full test suite, capturing output and exit codes.Both gates pass. This is a verification-only step, so I made no file changes.

- **Grader** (`sh sources/run.sh`, run with `DATABASE_URL` and `DATABASE_PATH` unset): exit 0, 43 of 43 checks passed. It used its own temporary SQLite database.
- **Full suite** (`sh bin/test.sh`, same environment scrub): exit 0, 449 tests passed in about 33 seconds.

The test run wrote its log to `data/logs/` as the script's standard preamble requires. Nothing under `sources/` was touched.

RESULT: SUCCESS

FILES CHANGED:
- (none)

SUMMARY:
Terminal gate for feature-verification. I ran the supplied grader and the project test suite from the application root, both with `DATABASE_URL` and `DATABASE_PATH` removed from the environment, as the spec requires.
- `sh sources/run.sh`: exit 0, 43/43 checks passed (A1–Z2, including the bad-CSV and unknown-command cases).
- `sh bin/test.sh`: exit 0, 449 passed, 0 failed.

Both exit statuses are the verdicts. I did not modify anything under `sources/` or any application file.

BLOCKERS:
- None
