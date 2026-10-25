# Evidence: Block 7 · Feature (block-7)

- block type: block
- date: 2026-10-25
- resulting state: closed/verified
- story points (combined assembled cost): 4826
- execution id: 20261025.165832.068Z-dc3c86c5

## Stories built
- Run the supplied grader as the terminal release check. (verification) [story]

## Acceptance tooling authorization
- VERIFICATION.md#release-grader-passes: executable=sh; scope=test; authorization=existing Target environment

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1156)
- implements: VERIFICATION.md (SP 1039)
- stack: common_compact.md (SP 1653)

## Pre-build acceptance observation
- GREEN (prepassed): release-ledger-executable (VERIFICATION.md)
  intent: An executable named ledger exists at the application root.
  return code: 0
- GREEN (prepassed): release-grader-passes (VERIFICATION.md)
  intent: The supplied grader exits zero when run unfiltered against the finished application.
  return code: 0
  stdout:
    PASS A1: ledger init
    PASS A2: ledger count
    PASS B1: ledger load accounts /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/sources/seed_accounts.csv
    PASS B2: ledger load categories /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/sources/seed_categories.csv
    PASS B3: ledger load transactions /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/sources/seed_transactions.csv
    PASS B4: ledger count
    PASS C1: ledger report balances
    PASS C2: ledger report categories
    PASS C3: ledger report monthly
    PASS D1: ledger load transactions /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/sources/seed_transactions_bad.csv
    PASS D2: ledger load accounts /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/sources/seed_accounts.csv
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
    
    
    grader tally (passed, failed): ('43', '0')

## Post-build programmatic acceptance
- PASS: release-ledger-executable (VERIFICATION.md)
  intent: An executable named ledger exists at the application root.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: release-grader-passes (VERIFICATION.md)
  intent: The supplied grader exits zero when run unfiltered against the finished application.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    PASS A1: ledger init
    PASS A2: ledger count
    PASS B1: ledger load accounts /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/sources/seed_accounts.csv
    PASS B2: ledger load categories /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/sources/seed_categories.csv
    PASS B3: ledger load transactions /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/sources/seed_transactions.csv
    PASS B4: ledger count
    PASS C1: ledger report balances
    PASS C2: ledger report categories
    PASS C3: ledger report monthly
    PASS D1: ledger load transactions /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/sources/seed_transactions_bad.csv
    PASS D2: ledger load accounts /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/sources/seed_accounts.csv
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
    
    
    grader tally (passed, failed): ('43', '0')

## Build summary
I'll start by checking what's in the build directory, then run the grader.The ledger executable is present and the working tree is clean, so `sources/` is untouched. Now I'll run the grader unfiltered, with the same environment stripping the acceptance criterion uses.The grader exited 0 with 43/43 passing. I'll confirm the run didn't alter anything under `sources/`.The grader passes unfiltered: `sh sources/run.sh` exited 0 with 43 of 43 checks passing. This was a verification-only step, so I changed no files.

- **Grader:** exit code 0, `LayersTesting: 43 passed, 0 failed (of 43)`. I ran it with `DATABASE_URL` and `DATABASE_PATH` unset, as the acceptance criterion does, so the grader used its own temporary database.
- **Executable criterion (`release-ledger-executable`):** `ledger` exists at the application root and is executable.
- **Guardrail:** `git status` and `git diff` show nothing changed under `sources/`.

I did not run the Python acceptance criteria through the Drydock harness or `bin/test.sh`. This step only asks for the grader, and the stories list it as the sole check.

RESULT: SUCCESS

FILES CHANGED:
- (none)

SUMMARY:
Ran `sh sources/run.sh` unfiltered from the application root with `DATABASE_URL` and `DATABASE_PATH` removed from the environment. Exit status 0; the grader reports 43 passed, 0 failed of 43. Confirmed `ledger` is present and executable at the application root. Confirmed `sources/` has no modifications before or after the run. Invocations: grader, 1 run, 43/43 passed.

BLOCKERS:
- none
