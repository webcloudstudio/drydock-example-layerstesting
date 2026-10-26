# Evidence: Block 5 · Feature (block-5)

- block type: block
- date: 2026-10-25
- resulting state: closed/failed
- story points (combined assembled cost): 4798
- execution id: 20261025.183727.078Z-7deb4acd

## Stories built
- Terminal gate running the full supplied grader. (release-verification) [story]

## Acceptance tooling authorization
- VERIFICATION.md#release-full-grader: executable=sh; scope=test; authorization=existing Target environment

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1156)
- implements: VERIFICATION.md (SP 989)
- stack: common_compact.md (SP 1653)

## Pre-build acceptance observation
- RED: release-full-grader (VERIFICATION.md)
  intent: The completed ledger passes every check of the supplied end-to-end grader, which exits zero only when all 43 checks pass.
  return code: 1
  stdout:
    FAIL A1: ledger init
      exit: expected 0, got 1
      stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions
    FAIL A2: ledger count
      exit: expected 0, got 1
      1,4d0
      < table,rows
      < accounts,0
      < categories,0
      < transactions,0
      stderr: error: FEATURE-ACCOUNTS-003 failed: no such table: accounts
    FAIL B1: ledger load accounts /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/sources/seed_accounts.csv
      exit: expected 0, got 1
      1,2d0
      < table,loaded
      < accounts,4
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL B2: ledger load categories /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/sources/seed_categories.csv
      exit: expected 0, got 1
      1,2d0
      < table,loaded
      < categories,7
      stderr: error: FEATURE-CATEGORIES-002 failed: no such table: categories
    FAIL B3: ledger load transactions /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/sources/seed_transactions.csv
      exit: expected 0, got 1
      1,2d0
      < table,loaded
      < transactions,120
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL B4: ledger count
      exit: expected 0, got 1
      1,4d0
      < table,rows
      < accounts,4
      < categories,7
      < transactions,120
      stderr: error: FEATURE-ACCOUNTS-003 failed: no such table: accounts
    FAIL C1: ledger report balances
      exit: expected 0, got 1
      1,6d0
      < account,name,transactions,balance
      < DRAWER1,Front Drawer,39,2299.38
      < DRAWER2,Back Drawer,39,1378.32
      < PETTY,Petty Cash,21,306.25
      < SAFE,Store Safe,21,250.00
      < TOTAL,,120,4233.95
      stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions
    FAIL C2: ledger report categories
      exit: expected 0, got 1
      1,9d0
      < category,description,transactions,inflow,outflow,net
      < OPENING,Opening balance,2,5200.00,0.00,5200.00
      < PAYROLL,Payroll,6,0.00,7200.00,-7200.00
      < REFUND,Customer refunds,12,0.00,101.25,-101.25
      < RENT,Rent,3,0.00,2700.00,-2700.00
      < SALES,Sales receipts,64,9578.95,0.00,9578.95
      < SUPPLY,Supplies,15,0.00,543.75,-543.75
      < TRANSFER,Internal transfer,18,5100.00,5100.00,0.00
      < TOTAL,,120,19878.95,15645.00,4233.95
      stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions
    FAIL C3: ledger report monthly
      exit: expected 0, got 1
      1,5d0
      < month,transactions,inflow,outflow,net
      < 2026-01,40,9659.45,5215.00,4444.45
      < 2026-02,40,4979.65,5215.00,-235.35
      < 2026-03,40,5239.85,5215.00,24.85
      < TOTAL,120,19878.95,15645.00,4233.95
      stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions
    FAIL D1: ledger load transactions /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/sources/seed_transactions_bad.csv
      exit: expected 3, got 1
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL D2: ledger load accounts /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/sources/seed_accounts.csv
      exit: expected 3, got 1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL D3: ledger count
      exit: expected 0, got 1
      1,4d0
      < table,rows
      < accounts,4
      < categories,7
      < transactions,120
      stderr: error: FEATURE-ACCOUNTS-003 failed: no such table: accounts
    FAIL E1: ledger account add CASH9 Event Float
      exit: expected 0, got 1
      1,2d0
      < account,name,transactions,balance
      < CASH9,Event Float,0,0.00
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL E2: ledger account add CASH9 Event Float
      exit: expected 3, got 1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL E3: ledger account get CASH9
      exit: expected 0, got 1
      1,2d0
      < account,name,transactions,balance
      < CASH9,Event Float,0,0.00
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL E4: ledger account rename CASH9 Event Cash Box
      exit: expected 0, got 1
      1,2d0
      < account,name,transactions,balance
      < CASH9,Event Cash Box,0,0.00
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL E5: ledger account get NOSUCH
      exit: expected 4, got 1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL E6: ledger account delete DRAWER1
      exit: expected 3, got 1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL E7: ledger account delete CASH9
      exit: expected 0, got 1
      1,2d0
      < deleted
      < CASH9
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL E8: ledger account get CASH9
      exit: expected 4, got 1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL F1: ledger txn post DRAWER1 SALES 45.50 2026-04-01 walk in sale
      exit: expected 0, got 1
      1,2d0
      < txn_id,date,account,category,amount,memo
      < 121,2026-04-01,DRAWER1,SALES,45.50,walk in sale
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL F2: ledger txn get 121
      exit: expected 0, got 1
      1,2d0
      < txn_id,date,account,category,amount,memo
      < 121,2026-04-01,DRAWER1,SALES,45.50,walk in sale
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL F3: ledger txn amend 121 54.50
      exit: expected 0, got 1
      1,2d0
      < txn_id,date,account,category,amount,memo
      < 121,2026-04-01,DRAWER1,SALES,54.50,walk in sale
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL F4: ledger txn get 999
      exit: expected 4, got 1
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL F5: ledger txn post DRAWER1 NOSUCH 1.00 2026-04-01
      exit: expected 3, got 1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    PASS F6: ledger txn post DRAWER1 SALES 1.234 2026-04-01
    PASS F7: ledger txn post DRAWER1 SALES 1.00 2026-02-30
    FAIL F8: ledger txn delete 121
      exit: expected 0, got 1
      1,2d0
      < deleted
      < 121
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL F9: ledger txn get 121
      exit: expected 4, got 1
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL F10: ledger txn post PETTY SUPPLY -12.34 2026-04-02 tape
      exit: expected 0, got 1
      1,2d0
      < txn_id,date,account,category,amount,memo
      < 121,2026-04-02,PETTY,SUPPLY,-12.34,tape
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL G1: ledger transfer DRAWER1 SAFE 500.00 2026-04-03
      exit: expected 0, got 1
      1,3d0
      < txn_id,date,account,category,amount,memo
      < 122,2026-04-03,DRAWER1,TRANSFER,-500.00,transfer to SAFE
      < 123,2026-04-03,SAFE,TRANSFER,500.00,transfer from DRAWER1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL G2: ledger transfer SAFE PETTY 999.99 2026-04-04
      exit: expected 3, got 1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL G3: ledger txn post PETTY SUPPLY -1000.00 2026-04-04
      exit: expected 3, got 1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL G4: ledger txn amend 1 1.00
      exit: expected 3, got 1
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL G5: ledger txn delete 1
      exit: expected 3, got 1
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL G6: ledger count
      exit: expected 0, got 1
      1,4d0
      < table,rows
      < accounts,4
      < categories,7
      < transactions,123
      stderr: error: FEATURE-ACCOUNTS-003 failed: no such table: accounts
    FAIL H1: ledger report balances
      exit: expected 0, got 1
      1,6d0
      < account,name,transactions,balance
      < DRAWER1,Front Drawer,40,1799.38
      < DRAWER2,Back Drawer,39,1378.32
      < PETTY,Petty Cash,22,293.91
      < SAFE,Store Safe,22,750.00
      < TOTAL,,123,4221.61
      stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions
    FAIL H2: ledger report categories
      exit: expected 0, got 1
      1,9d0
      < category,description,transactions,inflow,outflow,net
      < OPENING,Opening balance,2,5200.00,0.00,5200.00
      < PAYROLL,Payroll,6,0.00,7200.00,-7200.00
      < REFUND,Customer refunds,12,0.00,101.25,-101.25
      < RENT,Rent,3,0.00,2700.00,-2700.00
      < SALES,Sales receipts,64,9578.95,0.00,9578.95
      < SUPPLY,Supplies,16,0.00,556.09,-556.09
      < TRANSFER,Internal transfer,20,5600.00,5600.00,0.00
      < TOTAL,,123,20378.95,16157.34,4221.61
      stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions
    FAIL H3: ledger report monthly
      exit: expected 0, got 1
      1,6d0
      < month,transactions,inflow,outflow,net
      < 2026-01,40,9659.45,5215.00,4444.45
      < 2026-02,40,4979.65,5215.00,-235.35
      < 2026-03,40,5239.85,5215.00,24.85
      < 2026-04,3,500.00,512.34,-12.34
      < TOTAL,123,20378.95,16157.34,4221.61
      stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions
    PASS U1: ledger frobnicate
    PASS U2: ledger report nosuch
    FAIL Z1: ledger init
      exit: expected 0, got 1
      stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions
    FAIL Z2: ledger count
      exit: expected 0, got 1
      1,4d0
      < table,rows
      < accounts,0
      < categories,0
      < transactions,0
      stderr: error: FEATURE-ACCOUNTS-003 failed: no such table: accounts
    LayersTesting: 4 passed, 39 failed (of 43)
  stderr:
    --- drydock: progress ---
    cases: pass=1 fail=3 total=4 from=result.stdout
    --- drydock: end progress ---
    --- drydock: values at failure ---
      result = CompletedProcess(args=['sh', 'sources/run.sh'], returncode=1, stdout='FAIL A1: ledger init\n  exit: expected 0, got 1\n  stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions\nFAIL A2: ledger count\n  exit: expected 0, got 1\n  1,4d0\n  < table,rows\n  < accounts,0\n  < categories,0\n  < transactions,0\n  stderr: error: FEATURE-ACCOUNTS-003 failed: no such table: accounts\nFA… (+9127 chars)
    --- drydock: end values ---
    Traceback (most recent call last):
      File "release-full-grader.py", line 13, in <module>
        assert result.returncode == 0
    AssertionError

## Post-build programmatic acceptance
- FAIL: release-full-grader (VERIFICATION.md)
  intent: The completed ledger passes every check of the supplied end-to-end grader, which exits zero only when all 43 checks pass.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 1
  stdout:
    FAIL A1: ledger init
      exit: expected 0, got 1
      stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions
    FAIL A2: ledger count
      exit: expected 0, got 1
      1,4d0
      < table,rows
      < accounts,0
      < categories,0
      < transactions,0
      stderr: error: FEATURE-ACCOUNTS-003 failed: no such table: accounts
    FAIL B1: ledger load accounts /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/sources/seed_accounts.csv
      exit: expected 0, got 1
      1,2d0
      < table,loaded
      < accounts,4
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL B2: ledger load categories /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/sources/seed_categories.csv
      exit: expected 0, got 1
      1,2d0
      < table,loaded
      < categories,7
      stderr: error: FEATURE-CATEGORIES-002 failed: no such table: categories
    FAIL B3: ledger load transactions /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/sources/seed_transactions.csv
      exit: expected 0, got 1
      1,2d0
      < table,loaded
      < transactions,120
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL B4: ledger count
      exit: expected 0, got 1
      1,4d0
      < table,rows
      < accounts,4
      < categories,7
      < transactions,120
      stderr: error: FEATURE-ACCOUNTS-003 failed: no such table: accounts
    FAIL C1: ledger report balances
      exit: expected 0, got 1
      1,6d0
      < account,name,transactions,balance
      < DRAWER1,Front Drawer,39,2299.38
      < DRAWER2,Back Drawer,39,1378.32
      < PETTY,Petty Cash,21,306.25
      < SAFE,Store Safe,21,250.00
      < TOTAL,,120,4233.95
      stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions
    FAIL C2: ledger report categories
      exit: expected 0, got 1
      1,9d0
      < category,description,transactions,inflow,outflow,net
      < OPENING,Opening balance,2,5200.00,0.00,5200.00
      < PAYROLL,Payroll,6,0.00,7200.00,-7200.00
      < REFUND,Customer refunds,12,0.00,101.25,-101.25
      < RENT,Rent,3,0.00,2700.00,-2700.00
      < SALES,Sales receipts,64,9578.95,0.00,9578.95
      < SUPPLY,Supplies,15,0.00,543.75,-543.75
      < TRANSFER,Internal transfer,18,5100.00,5100.00,0.00
      < TOTAL,,120,19878.95,15645.00,4233.95
      stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions
    FAIL C3: ledger report monthly
      exit: expected 0, got 1
      1,5d0
      < month,transactions,inflow,outflow,net
      < 2026-01,40,9659.45,5215.00,4444.45
      < 2026-02,40,4979.65,5215.00,-235.35
      < 2026-03,40,5239.85,5215.00,24.85
      < TOTAL,120,19878.95,15645.00,4233.95
      stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions
    FAIL D1: ledger load transactions /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/sources/seed_transactions_bad.csv
      exit: expected 3, got 1
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL D2: ledger load accounts /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/sources/seed_accounts.csv
      exit: expected 3, got 1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL D3: ledger count
      exit: expected 0, got 1
      1,4d0
      < table,rows
      < accounts,4
      < categories,7
      < transactions,120
      stderr: error: FEATURE-ACCOUNTS-003 failed: no such table: accounts
    FAIL E1: ledger account add CASH9 Event Float
      exit: expected 0, got 1
      1,2d0
      < account,name,transactions,balance
      < CASH9,Event Float,0,0.00
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL E2: ledger account add CASH9 Event Float
      exit: expected 3, got 1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL E3: ledger account get CASH9
      exit: expected 0, got 1
      1,2d0
      < account,name,transactions,balance
      < CASH9,Event Float,0,0.00
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL E4: ledger account rename CASH9 Event Cash Box
      exit: expected 0, got 1
      1,2d0
      < account,name,transactions,balance
      < CASH9,Event Cash Box,0,0.00
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL E5: ledger account get NOSUCH
      exit: expected 4, got 1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL E6: ledger account delete DRAWER1
      exit: expected 3, got 1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL E7: ledger account delete CASH9
      exit: expected 0, got 1
      1,2d0
      < deleted
      < CASH9
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL E8: ledger account get CASH9
      exit: expected 4, got 1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL F1: ledger txn post DRAWER1 SALES 45.50 2026-04-01 walk in sale
      exit: expected 0, got 1
      1,2d0
      < txn_id,date,account,category,amount,memo
      < 121,2026-04-01,DRAWER1,SALES,45.50,walk in sale
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL F2: ledger txn get 121
      exit: expected 0, got 1
      1,2d0
      < txn_id,date,account,category,amount,memo
      < 121,2026-04-01,DRAWER1,SALES,45.50,walk in sale
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL F3: ledger txn amend 121 54.50
      exit: expected 0, got 1
      1,2d0
      < txn_id,date,account,category,amount,memo
      < 121,2026-04-01,DRAWER1,SALES,54.50,walk in sale
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL F4: ledger txn get 999
      exit: expected 4, got 1
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL F5: ledger txn post DRAWER1 NOSUCH 1.00 2026-04-01
      exit: expected 3, got 1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    PASS F6: ledger txn post DRAWER1 SALES 1.234 2026-04-01
    PASS F7: ledger txn post DRAWER1 SALES 1.00 2026-02-30
    FAIL F8: ledger txn delete 121
      exit: expected 0, got 1
      1,2d0
      < deleted
      < 121
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL F9: ledger txn get 121
      exit: expected 4, got 1
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL F10: ledger txn post PETTY SUPPLY -12.34 2026-04-02 tape
      exit: expected 0, got 1
      1,2d0
      < txn_id,date,account,category,amount,memo
      < 121,2026-04-02,PETTY,SUPPLY,-12.34,tape
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL G1: ledger transfer DRAWER1 SAFE 500.00 2026-04-03
      exit: expected 0, got 1
      1,3d0
      < txn_id,date,account,category,amount,memo
      < 122,2026-04-03,DRAWER1,TRANSFER,-500.00,transfer to SAFE
      < 123,2026-04-03,SAFE,TRANSFER,500.00,transfer from DRAWER1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL G2: ledger transfer SAFE PETTY 999.99 2026-04-04
      exit: expected 3, got 1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL G3: ledger txn post PETTY SUPPLY -1000.00 2026-04-04
      exit: expected 3, got 1
      stderr: error: FEATURE-ACCOUNTS-002 failed: no such table: accounts
    FAIL G4: ledger txn amend 1 1.00
      exit: expected 3, got 1
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL G5: ledger txn delete 1
      exit: expected 3, got 1
      stderr: error: FEATURE-TRANSACTIONS-002 failed: no such table: transactions
    FAIL G6: ledger count
      exit: expected 0, got 1
      1,4d0
      < table,rows
      < accounts,4
      < categories,7
      < transactions,123
      stderr: error: FEATURE-ACCOUNTS-003 failed: no such table: accounts
    FAIL H1: ledger report balances
      exit: expected 0, got 1
      1,6d0
      < account,name,transactions,balance
      < DRAWER1,Front Drawer,40,1799.38
      < DRAWER2,Back Drawer,39,1378.32
      < PETTY,Petty Cash,22,293.91
      < SAFE,Store Safe,22,750.00
      < TOTAL,,123,4221.61
      stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions
    FAIL H2: ledger report categories
      exit: expected 0, got 1
      1,9d0
      < category,description,transactions,inflow,outflow,net
      < OPENING,Opening balance,2,5200.00,0.00,5200.00
      < PAYROLL,Payroll,6,0.00,7200.00,-7200.00
      < REFUND,Customer refunds,12,0.00,101.25,-101.25
      < RENT,Rent,3,0.00,2700.00,-2700.00
      < SALES,Sales receipts,64,9578.95,0.00,9578.95
      < SUPPLY,Supplies,16,0.00,556.09,-556.09
      < TRANSFER,Internal transfer,20,5600.00,5600.00,0.00
      < TOTAL,,123,20378.95,16157.34,4221.61
      stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions
    FAIL H3: ledger report monthly
      exit: expected 0, got 1
      1,6d0
      < month,transactions,inflow,outflow,net
      < 2026-01,40,9659.45,5215.00,4444.45
      < 2026-02,40,4979.65,5215.00,-235.35
      < 2026-03,40,5239.85,5215.00,24.85
      < 2026-04,3,500.00,512.34,-12.34
      < TOTAL,123,20378.95,16157.34,4221.61
      stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions
    PASS U1: ledger frobnicate
    PASS U2: ledger report nosuch
    FAIL Z1: ledger init
      exit: expected 0, got 1
      stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions
    FAIL Z2: ledger count
      exit: expected 0, got 1
      1,4d0
      < table,rows
      < accounts,0
      < categories,0
      < transactions,0
      stderr: error: FEATURE-ACCOUNTS-003 failed: no such table: accounts
    LayersTesting: 4 passed, 39 failed (of 43)
  stderr:
    --- drydock: progress ---
    cases: pass=1 fail=3 total=4 from=result.stdout
    --- drydock: end progress ---
    --- drydock: values at failure ---
      result = CompletedProcess(args=['sh', 'sources/run.sh'], returncode=1, stdout='FAIL A1: ledger init\n  exit: expected 0, got 1\n  stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions\nFAIL A2: ledger count\n  exit: expected 0, got 1\n  1,4d0\n  < table,rows\n  < accounts,0\n  < categories,0\n  < transactions,0\n  stderr: error: FEATURE-ACCOUNTS-003 failed: no such table: accounts\nFA… (+9127 chars)
    --- drydock: end values ---
    Traceback (most recent call last):
      File "release-full-grader.py", line 13, in <module>
        assert result.returncode == 0
    AssertionError

## Repair attempts
- attempt 0 (initial build): failed; 0/1 checks; 1/4 cases model=claude-haiku-5-5; execution 20261025.183317.023Z-dea1d34b; reason: programmatic acceptance failed: release-full-grader
- attempt 1 (repair 1): failed; 0/1 checks; 1/4 cases model=claude-haiku-5-5; execution 20261025.183515.208Z-e2c2bf0f; reason: programmatic acceptance failed: release-full-grader
- attempt 2 (repair 2): failed; 0/1 checks; 1/4 cases model=claude-haiku-5-5; execution 20261025.183727.078Z-7deb4acd; stopped: deterministic acceptance score did not improve on 2 consecutive calls; reason: programmatic acceptance failed: release-full-grader

## Agent self-report (advisory)
The build agent declared a failure. This report is advisory; Drydock's execution and deterministic checks determine the block's outcome.
- summary: Grader needs a provisioned schema on a fresh database, which the Init and DATABASE specs forbid any command from creating.
- detail:
    With `schema.sql` applied to the database beforehand, all 43 checks pass (verified in `/tmp/lt-exp`). The specs place schema creation in the DATABASE step and forbid any command from issuing DDL, but the grader's fresh database never passes through that step. Amend DATABASE.md and FEATURE-Init.md, and record Q-001, to choose where provisioning happens (for example, an idempotent ensure-schema on open). Then rerun `sh sources/run.sh`.

## Failure
- summary: programmatic acceptance failed: release-full-grader
- detail:
    Block "Block 5 · Feature" [block-5] failed its acceptance criteria.
      Story "Terminal gate running the full supplied grader." [release-verification] does not meet its own acceptance criteria:
        - AC release-full-grader — The completed ledger passes every check of the supplied end-to-end grader, which exits zero only when all 43 checks pass.
            assertion: assert result.returncode == 0 → AssertionError
            cases: pass=1 fail=3 total=4 from=result.stdout
            raised at: release-full-grader.py:13
            process exit code: 1
            values at failure:
              result = CompletedProcess(args=['sh', 'sources/run.sh'], returncode=1, stdout='FAIL A1: ledger init\n  exit: expected 0, got 1\n  stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions\nFAIL A2: ledger count\n  exit: expected 0, got 1\n  1,4d0\n  < table,rows\n  < accounts,0\n  < categories,0\n  < transactions,0\n  stderr: error: FEATURE-ACCOUNTS-003 failed: no such table: accounts\nFA… (+9127 chars)
            observed output:
              FAIL Z1: ledger init
                exit: expected 0, got 1
                stderr: error: FEATURE-TRANSACTIONS-003 failed: no such table: transactions
              FAIL Z2: ledger count
                exit: expected 0, got 1
                1,4d0
                < table,rows
                < accounts,0
                < categories,0
                < transactions,0
                stderr: error: FEATURE-ACCOUNTS-003 failed: no such table: accounts
              LayersTesting: 4 passed, 39 failed (of 43)
              … 222 earlier line(s) omitted, --full for all
            check stderr:
              Traceback (most recent call last):
                File "release-full-grader.py", line 13, in <module>
                  assert result.returncode == 0
              AssertionError

## Build summary
This is the same repair request as before, and the blocker is unchanged. I'll rerun the grader once to confirm the build directory's state hasn't moved.RESULT: FAILED

Nothing has changed since the last pass. The grader still reports 4 passed, 39 failed, exit 1, and the working tree is clean. I did not edit the code, because the only fix that passes the grader breaks two explicit guardrails. This needs a spec decision before anyone edits code.

**Why I stopped**

- The grader creates an empty database and runs `ledger init`, so the schema has to exist before any command runs.
- `FEATURE-Init.md` says the schema "is provisioned by the DATABASE step, so init issues no DDL (decision Q-001)."
- `DATABASE.md` says "no command issues DDL."
- Nothing in the Target provisions a database that the grader creates itself. Q-001 is cited but has no decision record.
- Earlier I confirmed that applying `schema.sql` to a scratch database makes the grader pass 43 of 43. That shows the application logic is correct and the gap is only provisioning.

**What needs deciding**

Pick one, and I'll implement it:

1. **Ensure-schema on open (recommended):** the DATABASE step adds an idempotent schema apply when a store is opened. No command issues DDL explicitly, and the DATABASE and Init specs are amended to say so, with Q-001 recorded.
2. **Launcher bootstrap:** `ledger` applies `schema.sql` before it runs the CLI. This is the smallest change, but it puts DDL outside the persistence boundary.
3. **Keep the spec as written:** the gate fails until the grader provisions its own database. The grader is staged and can't be changed.

I wrote nothing to the build directory this pass. The `/tmp/lt-exp/` scratch database is still there.

FILES CHANGED:
- none

SUMMARY:
Re-ran the grader on the unchanged build: 4 passed, 39 failed (of 43), exit 1. The tree is clean, and no code was changed. The remaining failure is a specification conflict about where the schema is provisioned, not a defect in any command. I did not run `bin/test.sh`, because this block's criterion is the grader.

BLOCKERS:
- Schema provisioning for a fresh database conflicts with the Init and DATABASE specs, which forbid any command from issuing DDL. Decision needed on option 1, 2, or 3 above.

FAILURE_SUMMARY: Grader needs a provisioned schema on a fresh database, which the Init and DATABASE specs forbid any command from creating.
FAILURE_DETAIL: With `schema.sql` applied to the database beforehand, all 43 checks pass (verified in `/tmp/lt-exp`). The specs place schema creation in the DATABASE step and forbid any command from issuing DDL, but the grader's fresh database never passes through that step. Amend DATABASE.md and FEATURE-Init.md, and record Q-001, to choose where provisioning happens (for example, an idempotent ensure-schema on open). Then rerun `sh sources/run.sh`.
