# Evidence: Block 3 · Service (block-3)

- block type: block
- date: 2026-10-25
- resulting state: closed/verified
- story points (combined assembled cost): 26194
- execution id: 20261025.182019.449Z-aebc7831

## Stories built
- Provide account summaries and the non-negative balance check used by every mutating command. (balance-rules) [story]
- Implement ledger init to reset the ledger to empty. (init-command) [story]
- Implement ledger count. (count-command) [story]
- Implement ledger load categories with all-or-nothing validation. (load-categories) [story]
- Implement ledger load accounts with all-or-nothing validation. (load-accounts) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1156)
- implements: FEATURE-BalanceRules.md (SP 2920)
- context: ARCHITECTURE_compact.md (SP 475)
- context: DATABASE.md (SP 7219)
- stack: common_compact.md (SP 1653)
- stack: cli.md (SP 2689)
- implements: FEATURE-Init.md (SP 1333)
- implements: FEATURE-Count.md (SP 1371)
- implements: FEATURE-LoadCategories.md (SP 2980)
- implements: FEATURE-LoadAccounts.md (SP 3089)

## Build directory changes
- cli/balance.py
- cli/commands/count.py
- cli/commands/init.py
- cli/commands/load_accounts.py
- cli/commands/load_categories.py
- cli/loader.py
- cli/validate.py
- data/logs/test_2026-10-25_142120.log
- data/logs/test_2026-10-25_142213.log
- tests/conftest.py
- tests/test_balance_rules.py
- tests/test_count.py
- tests/test_init.py
- tests/test_load_accounts.py
- tests/test_load_categories.py

## Pre-build acceptance observation
- RED: balancerules-summary (FEATURE-BalanceRules.md)
  intent: account_summary returns the stored transaction count and the integer-cent sum of its amounts.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "balancerules-summary.py", line 2, in <module>
        from cli.balance import account_summary
    ModuleNotFoundError: No module named 'cli.balance'
- RED: balancerules-summary-empty (FEATURE-BalanceRules.md)
  intent: An account with no transactions has a zero count and zero balance.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "balancerules-summary-empty.py", line 2, in <module>
        from cli.balance import account_summary
    ModuleNotFoundError: No module named 'cli.balance'
- RED: balancerules-balances (FEATURE-BalanceRules.md)
  intent: balances returns the per-account sums computed from stored rows.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "balancerules-balances.py", line 2, in <module>
        from cli.balance import balances
    ModuleNotFoundError: No module named 'cli.balance'
- RED: balancerules-check-boundary (FEATURE-BalanceRules.md)
  intent: check_balances accepts a change that lands exactly on zero and rejects one cent below.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "balancerules-check-boundary.py", line 2, in <module>
        from cli.balance import check_balances
    ModuleNotFoundError: No module named 'cli.balance'
- RED: balancerules-check-any-account (FEATURE-BalanceRules.md)
  intent: check_balances rejects when any one of several accounts would go negative.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "balancerules-check-any-account.py", line 2, in <module>
        from cli.balance import check_balances
    ModuleNotFoundError: No module named 'cli.balance'
- RED: balancerules-check-writes-nothing (FEATURE-BalanceRules.md)
  intent: A rejected balance check leaves the stored transactions unchanged.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "balancerules-check-writes-nothing.py", line 2, in <module>
        from cli.balance import check_balances
    ModuleNotFoundError: No module named 'cli.balance'
- RED: balancerules-next-id (FEATURE-BalanceRules.md)
  intent: next_txn_id is one more than the largest stored id, or 1 when the table is empty.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "balancerules-next-id.py", line 2, in <module>
        from cli.balance import next_txn_id
    ModuleNotFoundError: No module named 'cli.balance'
- RED: init-empties-ledger (FEATURE-Init.md)
  intent: Init removes every account, category, and transaction and exits 0 with no standard output.
  return code: 1
  stdout:
    error: unknown command: init
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "init-empties-ledger.py", line 14, in <module>
        assert code == 0
    AssertionError
- RED: init-rerun (FEATURE-Init.md)
  intent: Rerunning init on an already empty ledger still exits 0 and leaves it empty.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      first = (2, '', 'error: unknown command: init\n')
    --- drydock: end values ---
    Traceback (most recent call last):
      File "init-rerun.py", line 7, in <module>
        assert first[0] == 0
    AssertionError
- GREEN (prepassed): init-argument-usage (FEATURE-Init.md)
  intent: Init with an extra argument is a usage error that changes nothing.
  return code: 0
  stdout:
    error: unknown command: init extra
- RED: count-reports-stored-rows (FEATURE-Count.md)
  intent: Count prints the table header and the stored row count of each table in the declared order.
  return code: 1
  stdout:
    error: unknown command: count
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "count-reports-stored-rows.py", line 18, in <module>
        assert code == 0
    AssertionError
- RED: count-tracks-changes (FEATURE-Count.md)
  intent: Count reflects rows added after a previous count.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "count-tracks-changes.py", line 16, in <module>
        before = accounts_count()
                 ^^^^^^^^^^^^^^^^
      File "count-tracks-changes.py", line 10, in accounts_count
        assert code == 0
    AssertionError
- RED: count-after-init (FEATURE-Count.md)
  intent: After init every table reports zero rows.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "count-after-init.py", line 9, in <module>
        assert cli_runner("init")[0] == 0
    AssertionError
- GREEN (prepassed): count-argument-usage (FEATURE-Count.md)
  intent: Count with an extra argument is a usage error with no standard output.
  return code: 0
  stdout:
    error: unknown command: count extra
- RED: load-categories-valid (FEATURE-LoadCategories.md)
  intent: A valid categories file loads, reports the loaded count, and every row reads back from the store.
  return code: 1
  stdout:
    error: unknown command: load categories /tmp/tmp7tul4kdy/categories.csv
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-categories-valid.py", line 19, in <module>
        assert code == 0
    AssertionError
- RED: load-categories-atomic-invalid-row (FEATURE-LoadCategories.md)
  intent: A file with an invalid last row exits 3, prints nothing to stdout, and stores none of the preceding valid rows.
  return code: 1
  stdout:
    error: unknown command: load categories /tmp/tmpi6q1vl2f/categories.csv
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-categories-atomic-invalid-row.py", line 19, in <module>
        assert code == 3
    AssertionError
- RED: load-categories-field-rules (FEATURE-LoadCategories.md)
  intent: Over-long codes, empty descriptions, and over-long descriptions each reject the whole file with exit 3.
  return code: 1
  stdout:
    error: unknown command: load categories /tmp/tmpl2al7_7a/categories0.csv
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-categories-field-rules.py", line 24, in <module>
        assert code == 3
    AssertionError
- RED: load-categories-duplicates (FEATURE-LoadCategories.md)
  intent: A code repeated inside the file, or already stored, rejects the whole file with exit 3 and stores nothing new.
  return code: 1
  stdout:
    error: unknown command: load categories /tmp/tmpkyuuhiix/store.csv
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-categories-duplicates.py", line 22, in <module>
        assert code == 3
    AssertionError
- RED: load-categories-header-and-usage (FEATURE-LoadCategories.md)
  intent: A mismatched header exits 3, a missing file exits 1, and a missing file argument exits 2.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
      out = ''
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-categories-header-and-usage.py", line 16, in <module>
        assert code == 3 and out == ""
    AssertionError
- RED: load-accounts-valid (FEATURE-LoadAccounts.md)
  intent: A valid accounts file loads, reports the loaded count, and every row reads back from the store.
  return code: 1
  stdout:
    error: unknown command: load accounts /tmp/tmptbbwd8xg/accounts.csv
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-accounts-valid.py", line 19, in <module>
        assert code == 0
    AssertionError
- RED: load-accounts-atomic-invalid-row (FEATURE-LoadAccounts.md)
  intent: A file with an invalid last row exits 3, prints nothing to stdout, and stores none of the preceding valid rows.
  return code: 1
  stdout:
    error: unknown command: load accounts /tmp/tmp9h0kgt92/accounts.csv
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-accounts-atomic-invalid-row.py", line 19, in <module>
        assert code == 3
    AssertionError
- RED: load-accounts-field-rules (FEATURE-LoadAccounts.md)
  intent: Over-long codes, empty names, and over-long names each reject the whole file with exit 3 and store nothing.
  return code: 1
  stdout:
    error: unknown command: load accounts /tmp/tmpe4l50u_p/accounts0.csv
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-accounts-field-rules.py", line 24, in <module>
        assert code == 3
    AssertionError
- RED: load-accounts-duplicates (FEATURE-LoadAccounts.md)
  intent: A code repeated inside the file, or already stored, rejects the whole file with exit 3 and stores nothing new.
  return code: 1
  stdout:
    error: unknown command: load accounts /tmp/tmpz0hq7ovh/store.csv
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-accounts-duplicates.py", line 22, in <module>
        assert code == 3
    AssertionError
- RED: load-accounts-header-and-usage (FEATURE-LoadAccounts.md)
  intent: A mismatched header exits 3, a missing file exits 1, and a wrong argument count or unknown table exits 2.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
      out = ''
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-accounts-header-and-usage.py", line 16, in <module>
        assert code == 3 and out == ""
    AssertionError

## Post-build programmatic acceptance
- PASS: balancerules-summary (FEATURE-BalanceRules.md)
  intent: account_summary returns the stored transaction count and the integer-cent sum of its amounts.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: balancerules-summary-empty (FEATURE-BalanceRules.md)
  intent: An account with no transactions has a zero count and zero balance.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: balancerules-balances (FEATURE-BalanceRules.md)
  intent: balances returns the per-account sums computed from stored rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: balancerules-check-boundary (FEATURE-BalanceRules.md)
  intent: check_balances accepts a change that lands exactly on zero and rejects one cent below.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: balancerules-check-any-account (FEATURE-BalanceRules.md)
  intent: check_balances rejects when any one of several accounts would go negative.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: balancerules-check-writes-nothing (FEATURE-BalanceRules.md)
  intent: A rejected balance check leaves the stored transactions unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: balancerules-next-id (FEATURE-BalanceRules.md)
  intent: next_txn_id is one more than the largest stored id, or 1 when the table is empty.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: init-empties-ledger (FEATURE-Init.md)
  intent: Init removes every account, category, and transaction and exits 0 with no standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: init-rerun (FEATURE-Init.md)
  intent: Rerunning init on an already empty ledger still exits 0 and leaves it empty.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: init-argument-usage (FEATURE-Init.md)
  intent: Init with an extra argument is a usage error that changes nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: init takes 0 to 0 arguments
- PASS: count-reports-stored-rows (FEATURE-Count.md)
  intent: Count prints the table header and the stored row count of each table in the declared order.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    table,rows
    accounts,1
    categories,1
    transactions,1
- PASS: count-tracks-changes (FEATURE-Count.md)
  intent: Count reflects rows added after a previous count.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: count-after-init (FEATURE-Count.md)
  intent: After init every table reports zero rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: count-argument-usage (FEATURE-Count.md)
  intent: Count with an extra argument is a usage error with no standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: count takes 0 to 0 arguments
- PASS: load-categories-valid (FEATURE-LoadCategories.md)
  intent: A valid categories file loads, reports the loaded count, and every row reads back from the store.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    table,loaded
    categories,2
- PASS: load-categories-atomic-invalid-row (FEATURE-LoadCategories.md)
  intent: A file with an invalid last row exits 3, prints nothing to stdout, and stores none of the preceding valid rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: code must be 1 to 12 characters from A-Z and 0-9: 'UTK-B3'
- PASS: load-categories-field-rules (FEATURE-LoadCategories.md)
  intent: Over-long codes, empty descriptions, and over-long descriptions each reject the whole file with exit 3.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: code must be 1 to 12 characters from A-Z and 0-9: 'KKKKKKKKKKKKK'
    
    error: description must be 1 to 40 characters
    
    error: description must be 1 to 40 characters
- PASS: load-categories-duplicates (FEATURE-LoadCategories.md)
  intent: A code repeated inside the file, or already stored, rejects the whole file with exit 3 and stores nothing new.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: category UTKD1 already exists
    
    error: category UTKD3 appears more than once in the file
- PASS: load-categories-header-and-usage (FEATURE-LoadCategories.md)
  intent: A mismatched header exits 3, a missing file exits 1, and a missing file argument exits 2.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: load-accounts-valid (FEATURE-LoadAccounts.md)
  intent: A valid accounts file loads, reports the loaded count, and every row reads back from the store.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    table,loaded
    accounts,3
- PASS: load-accounts-atomic-invalid-row (FEATURE-LoadAccounts.md)
  intent: A file with an invalid last row exits 3, prints nothing to stdout, and stores none of the preceding valid rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: code must be 1 to 12 characters from A-Z and 0-9: 'utlb3'
- PASS: load-accounts-field-rules (FEATURE-LoadAccounts.md)
  intent: Over-long codes, empty names, and over-long names each reject the whole file with exit 3 and store nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: code must be 1 to 12 characters from A-Z and 0-9: 'AAAAAAAAAAAAA'
    
    error: name must be 1 to 40 characters
    
    error: name must be 1 to 40 characters
- PASS: load-accounts-duplicates (FEATURE-LoadAccounts.md)
  intent: A code repeated inside the file, or already stored, rejects the whole file with exit 3 and stores nothing new.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account UTLD1 already exists
    
    error: account UTLD3 appears more than once in the file
- PASS: load-accounts-header-and-usage (FEATURE-LoadAccounts.md)
  intent: A mismatched header exits 3, a missing file exits 1, and a wrong argument count or unknown table exits 2.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
Baseline is green: 73 tests pass. Now I'll write the service modules, starting with the balance rules and a shared loader.Now the four command modules, each self-registering the way the existing registry expects.Next, a scratch-store fixture so command tests never touch the configured store, then the test files.All 124 pass (73 existing plus 51 new). I'll smoke-test the real `ledger` launcher against a throwaway store so the configured `data/app.db` stays untouched.<br>

RESULT: SUCCESS

FILES CHANGED:
- cli/balance.py
- cli/loader.py
- cli/validate.py
- cli/commands/init.py
- cli/commands/count.py
- cli/commands/load_categories.py
- cli/commands/load_accounts.py
- tests/conftest.py
- tests/test_balance_rules.py
- tests/test_init.py
- tests/test_count.py
- tests/test_load_categories.py
- tests/test_load_accounts.py

SUMMARY:
- **balance-rules:** `cli/balance.py` provides `account_summary`, `balances`, `check_balances` (raises `Rejected`, exit 3, when any stored balance plus its delta goes below zero; writes nothing), and `next_txn_id`. Everything is computed from listed rows in integer cents.
- **init-command:** `ledger init` deletes transactions, then categories, then accounts, through the declared delete operations. It takes no arguments and prints nothing. No DDL.
- **count-command:** `ledger count` prints `table,rows` and then the accounts, categories, and transactions counts, all from queries.
- **load-categories / load-accounts:** each validates the header, every row (code, description or name, field count), duplicates within the file, and duplicates against the store before its first write. Any failure exits 3 and writes nothing. A missing file exits 1. Shared CSV reading is in `cli/loader.py`.
- **Tests:** `sh bin/test.sh` runs 124 tests, all passing (73 pre-existing and 51 new). The new tests read every result back through the store or the CLI runner and check exit codes and stdout. Balance tests use the shipped `db_session` rollback fixture. Command tests use a new `scratch_db` fixture, a throwaway SQLite file under `tmp_path` selected via `DATABASE_PATH`, so the configured `data/app.db` is never modified.
- **Smoke test:** I ran the real `./ledger` launcher against a temporary store. count, both loads, a duplicate rejection (exit 3), and init all behaved as specified.
- **Not run:** the staged `AC` blocks from the specs are executed by the Drydock harness and were not run by me directly. I mirrored their assertions in the tests above. `sources/run.sh` is not part of this block and was not run.

Choices I made:
- Command modules live in `cli/commands/` as one file per command, self-registering through `cli/registry.py`. Helpers sit outside that package so the auto-importer does not load them as commands.
- I added `validate_description` (1 to 40 chars, no comma or line break) to `cli/validate.py` for category descriptions.
- Transactions cannot be deleted as a set, so init deletes them one id at a time.

BLOCKERS:
- None for this block.

<blueprint-decisions>
[{"spec":"FEATURE-LoadCategories.md","severity":"Material","subject":"Write-phase atomicity","decision":"All rows are validated before the first write, so every validation failure stores nothing. The persistence API exposes no transaction wrapper, so a store error raised partway through the write loop (exit 1) would leave earlier rows stored. Should a multi-row transaction be added to the DATABASE contract to close this gap?"},{"spec":"FEATURE-LoadAccounts.md","severity":"Material","subject":"Write-phase atomicity","decision":"Same as categories: validation is all-or-nothing, but a mid-write store failure is not rolled back because the persistence contract offers no transaction boundary. Should that be added to DATABASE.md?"}]
</blueprint-decisions>

FAILURE_SUMMARY: not applicable (step succeeded)
