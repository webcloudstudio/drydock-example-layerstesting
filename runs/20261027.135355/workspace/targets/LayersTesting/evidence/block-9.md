# Evidence: Block 9 · Feature (block-9)

- block type: block
- date: 2026-10-27
- resulting state: closed/verified
- story points (combined assembled cost): 13405
- execution id: 20261027.150048.281Z-aa862c27

## Stories built
- Assemble and verify the CSV output contract and exit codes across every command. (feature-command-contract) [story]
- Assemble and verify that every writing command enforces the no-negative-balance rule atomically. (feature-no-negative-balance) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1134)
- implements: FEATURE-CommandContract.md (SP 2535)
- context: ARCHITECTURE_compact.md (SP 332)
- context: DATABASE_compact.md (SP 884)
- stack: common_compact.md (SP 1653)
- stack: cli.md (SP 2689)
- implements: FEATURE-NoNegativeBalance.md (SP 2978)

## Build directory changes
- data/app.db-shm
- data/app.db-wal
- data/logs/test_2026-10-27_110228.log
- tests/test_command_contract.py
- tests/test_no_negative_balance.py

## Pre-build acceptance observation
- GREEN (prepassed): contract-usage-errors (FEATURE-CommandContract.md)
  intent: Unknown commands, unknown tables or reports, and wrong argument counts all exit 2 with empty standard output.
  return code: 0
  stdout:
    ('frobnicate',) 2 usage: unknown command 'frobnicate'
    
    ('report', 'nosuch') 2 usage: unknown command 'report nosuch'
    
    ('report',) 2 usage: unknown command 'report'
    
    ('load', 'nosuch', 'x.csv') 2 usage: unknown command 'load nosuch x.csv'
    
    ('account',) 2 usage: unknown command 'account'
    
    ('account', 'get') 2 usage: wrong number of arguments for 'account get'
    
    ('txn', 'post', 'A') 2 usage: wrong number of arguments for 'txn post'
    
    ('transfer', 'A', 'B') 2 usage: wrong number of arguments for 'transfer'
    
    ('count', 'extra') 2 usage: wrong number of arguments for 'count'
- GREEN (prepassed): contract-csv-format (FEATURE-CommandContract.md)
  intent: Successful commands emit the declared headers, newline-only endings, no trailing spaces, and amounts with exactly two decimals.
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    1,2099-05-05,ZZCF1,ZZCFC,7.50,fmt
- GREEN (prepassed): contract-failures-silent-stdout (FEATURE-CommandContract.md)
  intent: Failing commands write nothing to standard output and exactly one diagnostic line to standard error, with the documented exit code for each failure class.
  return code: 0
  stdout:
    ('account', 'get', 'ZZNOSUCH9') 4 error: account ZZNOSUCH9 does not exist
    
    ('account', 'add', 'lower', 'Bad Code') 3 error: code must be 1 to 12 characters from A-Z and 0-9
    
    ('txn', 'get', '999999999') 4 error: transaction 999999999 does not exist
    
    ('txn', 'post', 'ZZNOSUCH9', 'ZZNOCAT9', '1.00', '2099-01-01') 3 error: account ZZNOSUCH9 does not exist
    
    ('load', 'accounts', '/nonexistent-dir/zz-missing.csv') 1 error: cannot read /nonexistent-dir/zz-missing.csv: No such file or directory
- GREEN (prepassed): contract-rejected-writes-change-nothing (FEATURE-CommandContract.md)
  intent: Rejected writing commands exit 3 and leave the counts of all three tables unchanged.
  return code: 0
  stdout:
    ('account', 'add', 'ZZCR1', 'Duplicate') 3 error: account ZZCR1 already exists
    
    ('account', 'add', 'bad code', 'Name') 3 error: code must be 1 to 12 characters from A-Z and 0-9
    
    ('account', 'delete', 'ZZCR1') 3 error: account ZZCR1 has transactions and cannot be deleted
    
    ('txn', 'post', 'ZZCR1', 'ZZCRC', '1.234', '2099-02-03') 3 error: amount must look like -12.50 with at most two decimals: '1.234'
    
    ('txn', 'post', 'ZZCR1', 'ZZCRC', '1.00', '2026-02-30') 3 error: date is not a real calendar date: 2026-02-30
    
    ('txn', 'post', 'ZZCR1', 'ZZNOCAT9', '1.00', '2099-02-03') 3 error: category ZZNOCAT9 does not exist
    
    ('txn', 'post', 'ZZCR1', 'ZZCRC', '0', '2099-02-03') 3 error: amount must not be zero
    
    ('transfer', 'ZZCR1', 'ZZCR1', '1.00', '2099-02-03') 3 error: transfer needs two different accounts
    
    ('transfer', 'ZZCR1', 'ZZCR2', '0.50', '2099-02-30') 3 error: date is not a real calendar date: 2099-02-30
- GREEN (prepassed): nonneg-load (FEATURE-NoNegativeBalance.md)
  intent: A transactions load whose earlier rows are individually valid but whose combined effect makes the balance negative is rejected whole with exit 3 and stores none of its rows.
  return code: 0
  stdout:
    error: account ZZNL1 would be overdrawn by 1000 cents
- GREEN (prepassed): nonneg-post (FEATURE-NoNegativeBalance.md)
  intent: Posting an outflow larger than the balance exits 3 and leaves the balance and transaction count unchanged.
  return code: 0
  stdout:
    error: account ZZNP1 would be overdrawn by 1 cents
- GREEN (prepassed): nonneg-amend (FEATURE-NoNegativeBalance.md)
  intent: Amending a deposit down so the account would go negative exits 3 and the original amount remains.
  return code: 0
  stdout:
    error: account ZZNA1 would be overdrawn by 1000 cents
- GREEN (prepassed): nonneg-delete (FEATURE-NoNegativeBalance.md)
  intent: Deleting a deposit that funds a later outflow exits 3, keeps the row, and leaves the balance unchanged.
  return code: 0
  stdout:
    error: account ZZND1 would be overdrawn by 6000 cents
- GREEN (prepassed): nonneg-transfer (FEATURE-NoNegativeBalance.md)
  intent: A transfer larger than the source balance exits 3 and stores neither row; both balances and the table count are unchanged.
  return code: 0
  stdout:
    error: account ZZNT1 would be overdrawn by 1 cents

## Post-build programmatic acceptance
- PASS: contract-usage-errors (FEATURE-CommandContract.md)
  intent: Unknown commands, unknown tables or reports, and wrong argument counts all exit 2 with empty standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ('frobnicate',) 2 usage: unknown command 'frobnicate'
    
    ('report', 'nosuch') 2 usage: unknown command 'report nosuch'
    
    ('report',) 2 usage: unknown command 'report'
    
    ('load', 'nosuch', 'x.csv') 2 usage: unknown command 'load nosuch x.csv'
    
    ('account',) 2 usage: unknown command 'account'
    
    ('account', 'get') 2 usage: wrong number of arguments for 'account get'
    
    ('txn', 'post', 'A') 2 usage: wrong number of arguments for 'txn post'
    
    ('transfer', 'A', 'B') 2 usage: wrong number of arguments for 'transfer'
    
    ('count', 'extra') 2 usage: wrong number of arguments for 'count'
- PASS: contract-csv-format (FEATURE-CommandContract.md)
  intent: Successful commands emit the declared headers, newline-only endings, no trailing spaces, and amounts with exactly two decimals.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    1,2099-05-05,ZZCF1,ZZCFC,7.50,fmt
- PASS: contract-failures-silent-stdout (FEATURE-CommandContract.md)
  intent: Failing commands write nothing to standard output and exactly one diagnostic line to standard error, with the documented exit code for each failure class.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ('account', 'get', 'ZZNOSUCH9') 4 error: account ZZNOSUCH9 does not exist
    
    ('account', 'add', 'lower', 'Bad Code') 3 error: code must be 1 to 12 characters from A-Z and 0-9
    
    ('txn', 'get', '999999999') 4 error: transaction 999999999 does not exist
    
    ('txn', 'post', 'ZZNOSUCH9', 'ZZNOCAT9', '1.00', '2099-01-01') 3 error: account ZZNOSUCH9 does not exist
    
    ('load', 'accounts', '/nonexistent-dir/zz-missing.csv') 1 error: cannot read /nonexistent-dir/zz-missing.csv: No such file or directory
- PASS: contract-rejected-writes-change-nothing (FEATURE-CommandContract.md)
  intent: Rejected writing commands exit 3 and leave the counts of all three tables unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ('account', 'add', 'ZZCR1', 'Duplicate') 3 error: account ZZCR1 already exists
    
    ('account', 'add', 'bad code', 'Name') 3 error: code must be 1 to 12 characters from A-Z and 0-9
    
    ('account', 'delete', 'ZZCR1') 3 error: account ZZCR1 has transactions and cannot be deleted
    
    ('txn', 'post', 'ZZCR1', 'ZZCRC', '1.234', '2099-02-03') 3 error: amount must look like -12.50 with at most two decimals: '1.234'
    
    ('txn', 'post', 'ZZCR1', 'ZZCRC', '1.00', '2026-02-30') 3 error: date is not a real calendar date: 2026-02-30
    
    ('txn', 'post', 'ZZCR1', 'ZZNOCAT9', '1.00', '2099-02-03') 3 error: category ZZNOCAT9 does not exist
    
    ('txn', 'post', 'ZZCR1', 'ZZCRC', '0', '2099-02-03') 3 error: amount must not be zero
    
    ('transfer', 'ZZCR1', 'ZZCR1', '1.00', '2099-02-03') 3 error: transfer needs two different accounts
    
    ('transfer', 'ZZCR1', 'ZZCR2', '0.50', '2099-02-30') 3 error: date is not a real calendar date: 2099-02-30
- PASS: nonneg-load (FEATURE-NoNegativeBalance.md)
  intent: A transactions load whose earlier rows are individually valid but whose combined effect makes the balance negative is rejected whole with exit 3 and stores none of its rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account ZZNL1 would be overdrawn by 1000 cents
- PASS: nonneg-post (FEATURE-NoNegativeBalance.md)
  intent: Posting an outflow larger than the balance exits 3 and leaves the balance and transaction count unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account ZZNP1 would be overdrawn by 1 cents
- PASS: nonneg-amend (FEATURE-NoNegativeBalance.md)
  intent: Amending a deposit down so the account would go negative exits 3 and the original amount remains.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account ZZNA1 would be overdrawn by 1000 cents
- PASS: nonneg-delete (FEATURE-NoNegativeBalance.md)
  intent: Deleting a deposit that funds a later outflow exits 3, keeps the row, and leaves the balance unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account ZZND1 would be overdrawn by 6000 cents
- PASS: nonneg-transfer (FEATURE-NoNegativeBalance.md)
  intent: A transfer larger than the source balance exits 3 and stores neither row; both balances and the table count are unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account ZZNT1 would be overdrawn by 1 cents

## Build summary
I'll start by checking the build directory and the current state of the code.The core code for both stories already exists. Next I'll run the existing test suite to see where things stand.The existing suite passes (415 tests). Before writing the new tests, I'll check the local test style and confirm the stories' acceptance checks run against the current code.Existing tests use `ledger_store` and `store_open` fixtures. I'll check `tests/conftest.py` so the new tests follow the same isolation pattern.I have what I need. The implementation already covers both stories, so the remaining work is to add tests that prove each declared acceptance check. I'll write the four `feature-command-contract` checks and the five `feature-no-negative-balance` checks as tests, keeping every assertion and expected value from the specs. The only change is setup: they use the project's existing `ledger_store` fixture (fresh store per test) rather than `db_session`, which matches how the other command tests isolate state.Next, the no-negative-balance checks, one test per writing command plus the whole-file load case.I left an unused helper and an unused `os` import in that file. I'll remove them before running.Now I'll run the two new test files, verbose, to see each named check result.All 34 new checks pass. Now I'll run the declared verification gate, `sh bin/test.sh`, over the full suite.Both stories' declared checks now run as tests and pass. The code needed no changes: the existing modules already satisfy the specs.

I added two test files and changed no application code:

- `tests/test_command_contract.py` covers the four `feature-command-contract` checks: usage errors exit 2, CSV format, failure exit classes with one stderr line, and rejected writes leaving counts unchanged.
- `tests/test_no_negative_balance.py` covers the five `feature-no-negative-balance` checks: load, post, amend, delete, and transfer.

Each declared assertion and its expected values are kept. I changed only the setup: the checks use the project's `ledger_store` fixture (a fresh store per test), as the other command tests do, instead of `db_session`. Each check acts through `cli_runner` and reads state back through `count`, `get`, or the persistence interface.

Verification run:
- `pytest -v` on the two new files: 34 passed.
- `sh bin/test.sh` (full suite): 449 passed, exit 0. This includes the 415 existing tests.

I did not run `sources/run.sh`, because it is the terminal story and is not part of this block. I did not commit anything.

RESULT: SUCCESS

FILES CHANGED:
- tests/test_command_contract.py
- tests/test_no_negative_balance.py

SUMMARY:
Both stories were already implemented in `cli/`, `ledger_core/`, and `persistence/`, so this step only proves the declared checks. The new tests cover every declared acceptance check for both stories, with the expected values from the specs. Full suite via `sh bin/test.sh`: 449 passed, exit 0.

BLOCKERS:
- none
