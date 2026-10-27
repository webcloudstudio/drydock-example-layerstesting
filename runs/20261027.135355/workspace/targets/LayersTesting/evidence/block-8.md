# Evidence: Block 8 · Service (block-8)

- block type: block
- date: 2026-10-27
- resulting state: closed/verified
- story points (combined assembled cost): 15162
- execution id: 20261027.145729.992Z-56573846

## Stories built
- Implement `ledger report balances`. (feature-report-balances) [story]
- Implement `ledger report monthly`. (feature-report-monthly) [story]
- Implement `ledger report categories`. (feature-report-categories) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1134)
- implements: FEATURE-ReportBalances.md (SP 2430)
- context: ARCHITECTURE_compact.md (SP 332)
- context: DATABASE_compact.md (SP 884)
- stack: common_compact.md (SP 1653)
- stack: cli.md (SP 2689)
- implements: FEATURE-ReportMonthly.md (SP 2192)
- implements: FEATURE-ReportCategories.md (SP 2671)

## Build directory changes
- cli/commands/reports.py
- data/app.db-shm
- data/app.db-wal
- data/logs/test_2026-10-27_105846.log
- ledger_core/reports.py
- tests/test_reports.py

## Pre-build acceptance observation
- RED: report-balances-values (FEATURE-ReportBalances.md)
  intent: Each account row carries the count and formatted balance derived from stored transactions, and the TOTAL row carries the overall count and sum; expectations are computed from the stored rows.
  return code: 1
  stdout:
    usage: unknown command 'report balances'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-balances-values.py", line 25, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: report-balances-order-and-empty (FEATURE-ReportBalances.md)
  intent: Accounts are ordered by code regardless of creation order, and an account with no transactions still appears with count 0 and a zero balance.
  return code: 1
  stdout:
    usage: unknown command 'report balances'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-balances-order-and-empty.py", line 18, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: report-balances-total-consistency (FEATURE-ReportBalances.md)
  intent: The TOTAL row equals the sum of the per-account rows, including negative-free cent arithmetic across accounts.
  return code: 1
  stdout:
    usage: unknown command 'report balances'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-balances-total-consistency.py", line 22, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: report-balances-format (FEATURE-ReportBalances.md)
  intent: Output uses newline endings only, ends with a newline, and no line carries trailing spaces.
  return code: 1
  stdout:
    usage: unknown command 'report balances'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-balances-format.py", line 6, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- GREEN (prepassed): report-balances-usage (FEATURE-ReportBalances.md)
  intent: Extra arguments and an unknown report name exit 2 with nothing on stdout.
  return code: 0
  stdout:
    usage: unknown command 'report balances extra'
    
    
    usage: unknown command 'report nosuchreport'
    
    
    usage: unknown command 'report'
- RED: report-monthly-rows (FEATURE-ReportMonthly.md)
  intent: Monthly rows, ordering, and the TOTAL row are computed from posted transactions; expected counts and sums are derived from the supplied amounts with Decimal.
  return code: 1
  stdout:
    account,name,transactions,balance
    ZZRM1,Monthly Probe,0,0.00
     
    txn_id,date,account,category,amount,memo
    1,2099-01-05,ZZRM1,ZZRMC,100.50,m
     
    txn_id,date,account,category,amount,memo
    2,2099-01-20,ZZRM1,ZZRMC,40.25,m
     
    txn_id,date,account,category,amount,memo
    3,2099-01-21,ZZRM1,ZZRMC,-30.10,m
     
    txn_id,date,account,category,amount,memo
    4,2099-03-02,ZZRM1,ZZRMC,10.00,m
     
     usage: unknown command 'report monthly'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-monthly-rows.py", line 26, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- GREEN (prepassed): report-monthly-usage (FEATURE-ReportMonthly.md)
  intent: Extra arguments to report monthly are a usage error with exit 2 and nothing on standard output.
  return code: 0
  stdout:
    usage: unknown command 'report monthly extra'
- RED: report-monthly-reflects-changes (FEATURE-ReportMonthly.md)
  intent: The report is recomputed from the database: posting one more transaction in a new month adds exactly one month row with the posted amount as inflow.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-monthly-reflects-changes.py", line 20, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: report-categories-values (FEATURE-ReportCategories.md)
  intent: Each category row and the TOTAL row match inflow, outflow, net, and count derived from stored transactions, including a category with mixed signs and an empty category.
  return code: 1
  stdout:
    usage: unknown command 'report categories'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-categories-values.py", line 30, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: report-categories-empty (FEATURE-ReportCategories.md)
  intent: A category with no transactions is listed with count 0 and zero inflow, outflow, and net.
  return code: 1
  stdout:
    usage: unknown command 'report categories'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-categories-empty.py", line 17, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: report-categories-order (FEATURE-ReportCategories.md)
  intent: Categories are ordered by code regardless of creation order, and the TOTAL row is last.
  return code: 1
  stdout:
    usage: unknown command 'report categories'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-categories-order.py", line 13, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: report-categories-net-identity (FEATURE-ReportCategories.md)
  intent: For every row including TOTAL, net equals inflow minus outflow, and outflow is never written with a leading minus.
  return code: 1
  stdout:
    usage: unknown command 'report categories'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-categories-net-identity.py", line 21, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: report-categories-format (FEATURE-ReportCategories.md)
  intent: Output uses newline endings only, ends with a newline, and no line carries trailing spaces.
  return code: 1
  stdout:
    usage: unknown command 'report categories'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-categories-format.py", line 6, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- GREEN (prepassed): report-categories-usage (FEATURE-ReportCategories.md)
  intent: Extra arguments exit 2 with nothing on stdout.
  return code: 0
  stdout:
    usage: unknown command 'report categories extra'

## Post-build programmatic acceptance
- PASS: report-balances-values (FEATURE-ReportBalances.md)
  intent: Each account row carries the count and formatted balance derived from stored transactions, and the TOTAL row carries the overall count and sum; expectations are computed from the stored rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    ZZRB1,Report One,2,1211.11
    ZZRB2,Report Two,1,0.05
    TOTAL,,3,1211.16
- PASS: report-balances-order-and-empty (FEATURE-ReportBalances.md)
  intent: Accounts are ordered by code regardless of creation order, and an account with no transactions still appears with count 0 and a zero balance.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    ZZRB3,Empty ZZRB3,0,0.00
    ZZRB4,Empty ZZRB4,0,0.00
    TOTAL,,0,0.00
- PASS: report-balances-total-consistency (FEATURE-ReportBalances.md)
  intent: The TOTAL row equals the sum of the per-account rows, including negative-free cent arithmetic across accounts.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    ZZRB5,Total One,1,700.01
    ZZRB6,Total Two,1,300.02
    TOTAL,,2,1000.03
- PASS: report-balances-format (FEATURE-ReportBalances.md)
  intent: Output uses newline endings only, ends with a newline, and no line carries trailing spaces.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    TOTAL,,0,0.00
- PASS: report-balances-usage (FEATURE-ReportBalances.md)
  intent: Extra arguments and an unknown report name exit 2 with nothing on stdout.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    usage: wrong number of arguments for 'report balances'
    
    
    usage: unknown command 'report nosuchreport'
    
    
    usage: unknown command 'report'
- PASS: report-monthly-rows (FEATURE-ReportMonthly.md)
  intent: Monthly rows, ordering, and the TOTAL row are computed from posted transactions; expected counts and sums are derived from the supplied amounts with Decimal.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    ZZRM1,Monthly Probe,0,0.00
     
    txn_id,date,account,category,amount,memo
    1,2099-01-05,ZZRM1,ZZRMC,100.50,m
     
    txn_id,date,account,category,amount,memo
    2,2099-01-20,ZZRM1,ZZRMC,40.25,m
     
    txn_id,date,account,category,amount,memo
    3,2099-01-21,ZZRM1,ZZRMC,-30.10,m
     
    txn_id,date,account,category,amount,memo
    4,2099-03-02,ZZRM1,ZZRMC,10.00,m
     
    month,transactions,inflow,outflow,net
    2099-01,3,140.75,30.10,110.65
    2099-03,1,10.00,0.00,10.00
    TOTAL,4,150.75,30.10,120.65
- PASS: report-monthly-usage (FEATURE-ReportMonthly.md)
  intent: Extra arguments to report monthly are a usage error with exit 2 and nothing on standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    usage: wrong number of arguments for 'report monthly'
- PASS: report-monthly-reflects-changes (FEATURE-ReportMonthly.md)
  intent: The report is recomputed from the database: posting one more transaction in a new month adds exactly one month row with the posted amount as inflow.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    1,2098-07-10,ZZRM2,ZZRMD,12.34,m
- PASS: report-categories-values (FEATURE-ReportCategories.md)
  intent: Each category row and the TOTAL row match inflow, outflow, net, and count derived from stored transactions, including a category with mixed signs and an empty category.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    category,description,transactions,inflow,outflow,net
    ZZRCE,Empty Category,0,0.00,0.00,0.00
    ZZRCM,Mixed Category,3,1000.50,25.12,975.38
    TOTAL,,3,1000.50,25.12,975.38
- PASS: report-categories-empty (FEATURE-ReportCategories.md)
  intent: A category with no transactions is listed with count 0 and zero inflow, outflow, and net.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    category,description,transactions,inflow,outflow,net
    ZZRCE2,Nothing here,0,0.00,0.00,0.00
    TOTAL,,0,0.00,0.00,0.00
- PASS: report-categories-order (FEATURE-ReportCategories.md)
  intent: Categories are ordered by code regardless of creation order, and the TOTAL row is last.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    category,description,transactions,inflow,outflow,net
    ZZRCA,Order ZZRCA,0,0.00,0.00,0.00
    ZZRCB,Order ZZRCB,0,0.00,0.00,0.00
    TOTAL,,0,0.00,0.00,0.00
- PASS: report-categories-net-identity (FEATURE-ReportCategories.md)
  intent: For every row including TOTAL, net equals inflow minus outflow, and outflow is never written with a leading minus.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    category,description,transactions,inflow,outflow,net
    ZZRCN,Net Category,2,10.00,15.00,-5.00
    TOTAL,,2,10.00,15.00,-5.00
- PASS: report-categories-format (FEATURE-ReportCategories.md)
  intent: Output uses newline endings only, ends with a newline, and no line carries trailing spaces.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    category,description,transactions,inflow,outflow,net
    TOTAL,,0,0.00,0.00,0.00
- PASS: report-categories-usage (FEATURE-ReportCategories.md)
  intent: Extra arguments exit 2 with nothing on stdout.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    usage: wrong number of arguments for 'report categories'

## Build summary
I'll start by inspecting the build directory and the files this block depends on.The `report` command group doesn't exist yet, and `ledger_core` already has the money and transaction helpers I need. I'll check the existing CLI test conventions before writing anything.I have what I need. The plan:

- `ledger_core/reports.py`: pure integer-cent aggregation (count, inflow, outflow, net), with no storage access.
- `cli/commands/reports.py`: the three `report` handlers, registered as `("report", "balances")`, `("report", "monthly")`, and `("report", "categories")`. Each reads its rows through `db.<table>.list()`.
- `tests/test_reports.py`: behavioral tests on a fresh store per test, reading results back as CSV.

I'll write the aggregation module first.Now the command module. Each handler reads the rows, groups them in integer cents, and returns CSV rows.Next, the tests. I'm using a fixed dataset whose expected report values I worked out by hand in integer cents, so the expectations aren't computed by the code under test. Each test gets a fresh store.Now I'll run the new test file on its own, then the full suite through the declared `bin/test.sh`.The full suite passes: 415 tests, exit 0. As a last check I'll run the real `./ledger` launcher against a throwaway store, since the tests go through `cli_runner` and not the shell.`report balances`, `report monthly`, and `report categories` are implemented. The full suite passes (415 tests) and the real launcher output matches the seed-data expectations in `sources/run.sh` for C1–C3.

I did not run `sources/run.sh` itself. This block doesn't declare it, and the terminal-story check belongs to a later step.

- **`ledger_core/reports.py`** (new): integer-cent aggregation of count, inflow, outflow, and net. No storage access and no floats.
- **`cli/commands/reports.py`** (new): the three report handlers. Each reads rows through `db.<table>.list()`, groups them in cents, and formats with `format_cents`. Nothing is hardcoded and nothing is written.
- **`tests/test_reports.py`** (new): 24 tests on a fresh store each. Expected values are hand-computed from a fixed dataset, and results are read back by parsing CSV. They cover values, ordering, zero-count and empty-ledger cases, TOTAL rows, newline/trailing-space format, a monthly change after a new posting, and usage errors with exit 2.

Verification:
- `pytest -q tests/test_reports.py`: 24 passed.
- `sh bin/test.sh`: 415 passed, exit 0.
- Manual run of `./ledger` against a throwaway store loaded with the seed files: all three reports print the expected rows, and `report balances extra` and bare `report` both exit 2.

Choices I made that you can redirect:
- The aggregation lives in `ledger_core/reports.py`, not inside the command module, so it can be tested without the CLI.
- Accounts, categories, and months are sorted explicitly in Python rather than relying on the order the persistence layer returns.

No files were committed.

RESULT: SUCCESS

FILES CHANGED:
- ledger_core/reports.py
- cli/commands/reports.py
- tests/test_reports.py

SUMMARY:
Implemented `ledger report balances`, `ledger report monthly`, and `ledger report categories` as integer-cent computations over stored transactions and accounts/categories. Added 24 behavioral tests in `tests/test_reports.py`. `sh bin/test.sh` passes with 415 tests and exit 0. Smoke-tested `./ledger` on the seed data; the output matches `sources/run.sh` checks C1–C3. I did not run `sources/run.sh` itself, since this block does not declare it.

BLOCKERS:
- None
