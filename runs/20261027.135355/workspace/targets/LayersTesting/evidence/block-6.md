# Evidence: Block 6 · Service (block-6)

- block type: block
- date: 2026-10-27
- resulting state: closed/verified
- story points (combined assembled cost): 28316
- execution id: 20261027.144606.714Z-909a9d30

## Stories built
- Implement `ledger load accounts <csv>` as an all-or-nothing load. (feature-load-accounts) [story]
- Implement `ledger account delete <code>`. (feature-account-delete) [story]
- Implement `ledger txn get <id>`. (feature-txn-get) [story]
- Implement `ledger account rename <code> <name>`. (feature-account-rename) [story]
- Implement `ledger account get <code>`. (feature-account-get) [story]
- Implement `ledger txn delete <id>`. (feature-txn-delete) [story]
- Implement `ledger txn amend <id> <amount>`. (feature-txn-amend) [story]
- Implement `ledger load categories <csv>` as an all-or-nothing load. (feature-load-categories) [story]
- Implement `ledger transfer <from> <to> <amount> <date>` as an atomic two-row write. (feature-transfer) [story]

## Acceptance tooling authorization
- FEATURE-LoadAccounts.md#load-accounts-success: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-LoadAccounts.md#load-accounts-rejected-row-stores-nothing: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-LoadAccounts.md#load-accounts-invalid-fields: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-LoadAccounts.md#load-accounts-duplicates-rejected: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-LoadAccounts.md#load-accounts-header-and-usage: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-AccountDelete.md#account-delete-success: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-AccountDelete.md#account-delete-in-use: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-AccountDelete.md#account-delete-absent: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-AccountDelete.md#account-delete-usage: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-TxnGet.md#txn-get-existing: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-TxnGet.md#txn-get-negative-amount: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-TxnGet.md#txn-get-absent: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-TxnGet.md#txn-get-bad-id: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-AccountRename.md#account-rename-success: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-AccountRename.md#account-rename-absent: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-AccountRename.md#account-rename-invalid-name: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-AccountRename.md#account-rename-usage: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-AccountGet.md#account-get-existing: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-AccountGet.md#account-get-empty-account: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-AccountGet.md#account-get-absent: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-AccountGet.md#account-get-usage: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-LoadCategories.md#load-categories-success: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-LoadCategories.md#load-categories-rejected-row-stores-nothing: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-LoadCategories.md#load-categories-invalid-fields: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-LoadCategories.md#load-categories-duplicates-rejected: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-LoadCategories.md#load-categories-header-and-usage: executable=python3; scope=test; authorization=existing Target environment

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1134)
- implements: FEATURE-LoadAccounts.md (SP 3010)
- context: ARCHITECTURE_compact.md (SP 332)
- context: DATABASE_compact.md (SP 884)
- stack: common_compact.md (SP 1653)
- stack: cli.md (SP 2689)
- implements: FEATURE-AccountDelete.md (SP 1404)
- implements: FEATURE-TxnGet.md (SP 1504)
- implements: FEATURE-AccountRename.md (SP 1536)
- implements: FEATURE-AccountGet.md (SP 1654)
- implements: FEATURE-TxnDelete.md (SP 1904)
- implements: FEATURE-TxnAmend.md (SP 2853)
- implements: FEATURE-LoadCategories.md (SP 2971)
- implements: FEATURE-Transfer.md (SP 3201)

## Build directory changes
- cli/commands/accounts.py
- cli/commands/load.py
- cli/commands/transactions.py
- cli/commands/transfers.py
- data/app.db-shm
- data/app.db-wal
- data/logs/test_2026-10-27_105015.log
- ledger_core/atomic.py
- ledger_core/transactions.py
- tests/test_account_manage.py
- tests/test_atomic.py
- tests/test_load.py
- tests/test_transfer.py
- tests/test_txn_manage.py

## Pre-build acceptance observation
- RED: load-accounts-success (FEATURE-LoadAccounts.md)
  intent: a valid accounts file loads every row, prints the declared two CSV rows with the loaded count, and the rows are readable afterward.
  return code: 1
  stdout:
    error: loading accounts is not implemented yet
  stderr:
    --- drydock: values at failure ---
      code = 1
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-accounts-success.py", line 18, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: load-accounts-rejected-row-stores-nothing (FEATURE-LoadAccounts.md)
  intent: when the last row is invalid, exit 3 is returned, stdout is empty, and none of the earlier valid rows is stored.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 1
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-accounts-rejected-row-stores-nothing.py", line 19, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: load-accounts-invalid-fields (FEATURE-LoadAccounts.md)
  intent: each invalid code or name (too long, empty, bad characters, comma in name) rejects the whole file with exit 3 and stores neither it nor the valid row before it.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      bad = ['ABCDEFGHIJKLM', 'Code Too Long']
      code = 1
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-accounts-invalid-fields.py", line 26, in <module>
        assert code == 3, bad
               ^^^^^^^^^
    AssertionError: ['ABCDEFGHIJKLM', 'Code Too Long']
- RED: load-accounts-duplicates-rejected (FEATURE-LoadAccounts.md)
  intent: a code repeated inside the file, and a code already stored, each reject the whole file with exit 3 and leave the other rows unstored.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 1
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-accounts-duplicates-rejected.py", line 18, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- GREEN (prepassed): load-accounts-header-and-usage (FEATURE-LoadAccounts.md)
  intent: a wrong header exits 3 with nothing stored, and a missing file argument is a usage error with exit 2.
  return code: 0
- RED: account-delete-success (FEATURE-AccountDelete.md)
  intent: Deleting an account without transactions prints the confirmation and a later read finds nothing.
  return code: 1
  stdout:
    usage: unknown command 'account delete ZZAD1'
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-delete-success.py", line 12, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: account-delete-in-use (FEATURE-AccountDelete.md)
  intent: An account with a transaction is refused with exit 3 and both the account and the transaction remain.
  return code: 1
  stdout:
    usage: unknown command 'account delete ZZAD2'
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-delete-in-use.py", line 11, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- RED: account-delete-absent (FEATURE-AccountDelete.md)
  intent: Deleting an absent account exits 4 with no standard output.
  return code: 1
  stdout:
    usage: unknown command 'account delete ZZADNONE'
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-delete-absent.py", line 9, in <module>
        assert rc == 4
               ^^^^^^^
    AssertionError
- GREEN (prepassed): account-delete-usage (FEATURE-AccountDelete.md)
  intent: A missing argument is a usage error with exit 2 and no standard output.
  return code: 0
- RED: txn-get-existing (FEATURE-TxnGet.md)
  intent: A stored transaction prints with every column and the cents shown as a two-decimal amount.
  return code: 1
  stdout:
    usage: unknown command 'txn get 900001601'
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-get-existing.py", line 15, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: txn-get-negative-amount (FEATURE-TxnGet.md)
  intent: A negative stored amount prints with a leading minus and two decimals.
  return code: 1
  stdout:
    usage: unknown command 'txn get 900001603'
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-get-negative-amount.py", line 15, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: txn-get-absent (FEATURE-TxnGet.md)
  intent: An absent transaction id exits 4 with no standard output.
  return code: 1
  stdout:
    usage: unknown command 'txn get 999999999'
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-get-absent.py", line 9, in <module>
        assert rc == 4
               ^^^^^^^
    AssertionError
- RED: txn-get-bad-id (FEATURE-TxnGet.md)
  intent: A non-integer id is rejected with exit 3 and a wrong argument count is a usage error with exit 2.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-get-bad-id.py", line 6, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- RED: account-rename-success (FEATURE-AccountRename.md)
  intent: Renaming prints the updated row and a separate read shows the new name persisted.
  return code: 1
  stdout:
    usage: unknown command 'account rename ZZAR1 New Name'
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-rename-success.py", line 12, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: account-rename-absent (FEATURE-AccountRename.md)
  intent: Renaming an absent account exits 4 with no standard output and creates nothing.
  return code: 1
  stdout:
    usage: unknown command 'account rename ZZARNONE Any Name'
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-rename-absent.py", line 8, in <module>
        assert rc == 4
               ^^^^^^^
    AssertionError
- RED: account-rename-invalid-name (FEATURE-AccountRename.md)
  intent: A name containing a comma, an empty name, and an over-length name each exit 3 and leave the stored name unchanged.
  return code: 1
  stdout:
    usage: unknown command 'account rename ZZAR2 has,comma'
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-rename-invalid-name.py", line 11, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- GREEN (prepassed): account-rename-usage (FEATURE-AccountRename.md)
  intent: A wrong argument count is a usage error with exit 2 and no standard output.
  return code: 0
- RED: account-get-existing (FEATURE-AccountGet.md)
  intent: An account with two stored transactions is printed with its live count and its balance, both derived from the fixture amounts.
  return code: 1
  stdout:
    usage: unknown command 'account get ZZAG1'
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-get-existing.py", line 22, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: account-get-empty-account (FEATURE-AccountGet.md)
  intent: An account with no transactions prints a zero count and a zero balance.
  return code: 1
  stdout:
    usage: unknown command 'account get ZZAG2'
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-get-empty-account.py", line 12, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: account-get-absent (FEATURE-AccountGet.md)
  intent: An absent account code exits 4 and writes nothing to standard output.
  return code: 1
  stdout:
    usage: unknown command 'account get ZZAGNONE'
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-get-absent.py", line 10, in <module>
        assert rc == 4
               ^^^^^^^
    AssertionError
- GREEN (prepassed): account-get-usage (FEATURE-AccountGet.md)
  intent: A missing or surplus argument is a usage error with exit 2 and no standard output.
  return code: 0
- RED: txn-delete-success (FEATURE-TxnDelete.md)
  intent: Deleting an existing transaction exits 0, prints `deleted` then the id, and a separate read finds no row.
  return code: 1
  stdout:
    usage: unknown command 'txn delete 900200001'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-delete-success.py", line 15, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: txn-delete-absent (FEATURE-TxnDelete.md)
  intent: Deleting an id that does not exist exits 4 with nothing on stdout.
  return code: 1
  stdout:
    usage: unknown command 'txn delete 900299999'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-delete-absent.py", line 10, in <module>
        assert code == 4
               ^^^^^^^^^
    AssertionError
- RED: txn-delete-negative-balance (FEATURE-TxnDelete.md)
  intent: Deleting a +10000 deposit while a -4000 payment remains would leave -4000, so exit 3 and the row stays; deleting the payment instead leaves a positive balance and succeeds.
  return code: 1
  stdout:
    usage: unknown command 'txn delete 900200002'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-delete-negative-balance.py", line 18, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: txn-delete-bad-id (FEATURE-TxnDelete.md)
  intent: A non-integer id is rejected with exit 3 and nothing on stdout.
  return code: 1
  stdout:
    usage: unknown command 'txn delete abc'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-delete-bad-id.py", line 6, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- GREEN (prepassed): txn-delete-usage (FEATURE-TxnDelete.md)
  intent: A wrong argument count for txn delete exits 2 with nothing on stdout.
  return code: 0
  stdout:
    usage: unknown command 'txn delete'
    
    
    usage: unknown command 'txn delete 1 2'
- RED: txn-amend-success (FEATURE-TxnAmend.md)
  intent: Amending an existing transaction exits 0, prints the updated row with the supplied amount text, and a separate read shows the new integer cents.
  return code: 1
  stdout:
    usage: unknown command 'txn amend 900100001 50.00'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-amend-success.py", line 19, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: txn-amend-only-amount (FEATURE-TxnAmend.md)
  intent: Amend changes only the amount; date, account, category, and memo read back exactly as they were created.
  return code: 1
  stdout:
    usage: unknown command 'txn amend 900100002 35.50'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-amend-only-amount.py", line 17, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: txn-amend-absent (FEATURE-TxnAmend.md)
  intent: Amending an id that does not exist exits 4, prints nothing to stdout, and creates no row.
  return code: 1
  stdout:
    usage: unknown command 'txn amend 900199999 5.00'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-amend-absent.py", line 10, in <module>
        assert code == 4
               ^^^^^^^^^
    AssertionError
- RED: txn-amend-negative-balance (FEATURE-TxnAmend.md)
  intent: An amend that would leave the account balance below zero exits 3 and keeps the original amount, while an amend landing exactly on zero succeeds. The account holds +10000 and -4000 cents, so lowering the first to 3000 gives -1000 and lowering it to 4000 gives 0.
  return code: 1
  stdout:
    usage: unknown command 'txn amend 900100003 30.00'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-amend-negative-balance.py", line 18, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: txn-amend-invalid-amount (FEATURE-TxnAmend.md)
  intent: Amounts with three decimals, a zero amount, and a non-numeric amount are rejected with exit 3 and the stored amount is unchanged.
  return code: 1
  stdout:
    usage: unknown command 'txn amend 900100005 1.234'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-amend-invalid-amount.py", line 17, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- GREEN (prepassed): txn-amend-usage (FEATURE-TxnAmend.md)
  intent: A wrong argument count for txn amend exits 2 with nothing on stdout.
  return code: 0
  stdout:
    usage: unknown command 'txn amend'
    
    
    usage: unknown command 'txn amend 1'
    
    
    usage: unknown command 'txn amend 1 2.00 extra'
- RED: load-categories-success (FEATURE-LoadCategories.md)
  intent: a valid categories file loads every row, prints the declared two CSV rows with the loaded count, and the rows are readable afterward.
  return code: 1
  stdout:
    error: loading categories is not implemented yet
  stderr:
    --- drydock: values at failure ---
      code = 1
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-categories-success.py", line 18, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: load-categories-rejected-row-stores-nothing (FEATURE-LoadCategories.md)
  intent: when a later row is invalid, exit 3 is returned, stdout is empty, and none of the earlier valid rows is stored.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 1
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-categories-rejected-row-stores-nothing.py", line 19, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: load-categories-invalid-fields (FEATURE-LoadCategories.md)
  intent: each invalid code or description (bad characters, empty, over length, comma) rejects the whole file with exit 3 and stores no row.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      bad = ['zzkc1', 'Lowercase']
      code = 1
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-categories-invalid-fields.py", line 25, in <module>
        assert code == 3, bad
               ^^^^^^^^^
    AssertionError: ['zzkc1', 'Lowercase']
- RED: load-categories-duplicates-rejected (FEATURE-LoadCategories.md)
  intent: a code repeated inside the file, and a code already stored, each reject the whole file with exit 3 and leave the stored row unchanged.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 1
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-categories-duplicates-rejected.py", line 18, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- GREEN (prepassed): load-categories-header-and-usage (FEATURE-LoadCategories.md)
  intent: a wrong header exits 3 with nothing stored, and a missing file argument is a usage error with exit 2.
  return code: 0
- RED: transfer-success (FEATURE-Transfer.md)
  intent: A valid transfer exits 0 and prints two rows with consecutive ids starting at the previous maximum plus one, category TRANSFER, the signed amounts, and the specified memos; a separate read shows both stored.
  return code: 1
  stdout:
    usage: unknown command 'transfer ZZTF1 ZZTF2 250.00 2026-05-10'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfer-success.py", line 23, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: transfer-conserves-cash (FEATURE-Transfer.md)
  intent: A valid transfer moves cash without changing the total held by the two accounts, computed from stored rows before and after.
  return code: 1
  stdout:
    usage: unknown command 'transfer ZZTF3 ZZTF4 123.45 2026-05-11'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfer-conserves-cash.py", line 22, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: transfer-insufficient-funds (FEATURE-Transfer.md)
  intent: A transfer exceeding the source balance by one cent exits 3 and stores neither row; a transfer of exactly the balance then succeeds and leaves the source at zero.
  return code: 1
  stdout:
    usage: unknown command 'transfer ZZTF5 ZZTF6 100.01 2026-05-12'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfer-insufficient-funds.py", line 18, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: transfer-rejections (FEATURE-Transfer.md)
  intent: Same source and destination, zero or negative amounts, three decimals, an impossible date, and an unknown account are each rejected with exit 3, with empty stdout and no new rows.
  return code: 1
  stdout:
    ('ZZTF7', 'ZZTF7', '5.00', '2026-05-13') 2  usage: unknown command 'transfer ZZTF7 ZZTF7 5.00 2026-05-13'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfer-rejections.py", line 26, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- GREEN (prepassed): transfer-usage (FEATURE-Transfer.md)
  intent: A wrong argument count for transfer exits 2 with nothing on stdout.
  return code: 0
  stdout:
    usage: unknown command 'transfer'
    
    
    usage: unknown command 'transfer A B 1.00'
    
    
    usage: unknown command 'transfer A B 1.00 2026-05-01 extra'

## Post-build programmatic acceptance
- PASS: load-accounts-success (FEATURE-LoadAccounts.md)
  intent: a valid accounts file loads every row, prints the declared two CSV rows with the loaded count, and the rows are readable afterward.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    table,loaded
    accounts,3
- PASS: load-accounts-rejected-row-stores-nothing (FEATURE-LoadAccounts.md)
  intent: when the last row is invalid, exit 3 is returned, stdout is empty, and none of the earlier valid rows is stored.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: load-accounts-invalid-fields (FEATURE-LoadAccounts.md)
  intent: each invalid code or name (too long, empty, bad characters, comma in name) rejects the whole file with exit 3 and stores neither it nor the valid row before it.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: load-accounts-duplicates-rejected (FEATURE-LoadAccounts.md)
  intent: a code repeated inside the file, and a code already stored, each reject the whole file with exit 3 and leave the other rows unstored.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: load-accounts-header-and-usage (FEATURE-LoadAccounts.md)
  intent: a wrong header exits 3 with nothing stored, and a missing file argument is a usage error with exit 2.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-delete-success (FEATURE-AccountDelete.md)
  intent: Deleting an account without transactions prints the confirmation and a later read finds nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    deleted
    ZZAD1
- PASS: account-delete-in-use (FEATURE-AccountDelete.md)
  intent: An account with a transaction is refused with exit 3 and both the account and the transaction remain.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account ZZAD2 has transactions and cannot be deleted
- PASS: account-delete-absent (FEATURE-AccountDelete.md)
  intent: Deleting an absent account exits 4 with no standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account ZZADNONE does not exist
- PASS: account-delete-usage (FEATURE-AccountDelete.md)
  intent: A missing argument is a usage error with exit 2 and no standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: txn-get-existing (FEATURE-TxnGet.md)
  intent: A stored transaction prints with every column and the cents shown as a two-decimal amount.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    900001601,2026-04-05,ZZTG1,ZZTGC1,12.34,get probe
- PASS: txn-get-negative-amount (FEATURE-TxnGet.md)
  intent: A negative stored amount prints with a leading minus and two decimals.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    900001603,2026-04-06,ZZTG2,ZZTGC2,-12.50,
- PASS: txn-get-absent (FEATURE-TxnGet.md)
  intent: An absent transaction id exits 4 with no standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: transaction 999999999 does not exist
- PASS: txn-get-bad-id (FEATURE-TxnGet.md)
  intent: A non-integer id is rejected with exit 3 and a wrong argument count is a usage error with exit 2.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-rename-success (FEATURE-AccountRename.md)
  intent: Renaming prints the updated row and a separate read shows the new name persisted.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    ZZAR1,New Name,0,0.00
- PASS: account-rename-absent (FEATURE-AccountRename.md)
  intent: Renaming an absent account exits 4 with no standard output and creates nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account ZZARNONE does not exist
- PASS: account-rename-invalid-name (FEATURE-AccountRename.md)
  intent: A name containing a comma, an empty name, and an over-length name each exit 3 and leave the stored name unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: name must not contain a comma or newline
    
    error: name must be 1 to 40 characters
    
    error: name must be 1 to 40 characters
- PASS: account-rename-usage (FEATURE-AccountRename.md)
  intent: A wrong argument count is a usage error with exit 2 and no standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-get-existing (FEATURE-AccountGet.md)
  intent: An account with two stored transactions is printed with its live count and its balance, both derived from the fixture amounts.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    ZZAG1,Get Probe,2,7.50
- PASS: account-get-empty-account (FEATURE-AccountGet.md)
  intent: An account with no transactions prints a zero count and a zero balance.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    ZZAG2,Empty Probe,0,0.00
- PASS: account-get-absent (FEATURE-AccountGet.md)
  intent: An absent account code exits 4 and writes nothing to standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account ZZAGNONE does not exist
- PASS: account-get-usage (FEATURE-AccountGet.md)
  intent: A missing or surplus argument is a usage error with exit 2 and no standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: txn-delete-success (FEATURE-TxnDelete.md)
  intent: Deleting an existing transaction exits 0, prints `deleted` then the id, and a separate read finds no row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    deleted
    900200001
- PASS: txn-delete-absent (FEATURE-TxnDelete.md)
  intent: Deleting an id that does not exist exits 4 with nothing on stdout.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: transaction 900299999 does not exist
- PASS: txn-delete-negative-balance (FEATURE-TxnDelete.md)
  intent: Deleting a +10000 deposit while a -4000 payment remains would leave -4000, so exit 3 and the row stays; deleting the payment instead leaves a positive balance and succeeds.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account ZZDL2 would be overdrawn by 4000 cents
    
    deleted
    900200003
- PASS: txn-delete-bad-id (FEATURE-TxnDelete.md)
  intent: A non-integer id is rejected with exit 3 and nothing on stdout.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: transaction id must be an integer: 'abc'
- PASS: txn-delete-usage (FEATURE-TxnDelete.md)
  intent: A wrong argument count for txn delete exits 2 with nothing on stdout.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    usage: wrong number of arguments for 'txn delete'
    
    
    usage: wrong number of arguments for 'txn delete'
- PASS: txn-amend-success (FEATURE-TxnAmend.md)
  intent: Amending an existing transaction exits 0, prints the updated row with the supplied amount text, and a separate read shows the new integer cents.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    900100001,2026-05-01,ZZAM1,ZZAMC1,50.00,amend probe
- PASS: txn-amend-only-amount (FEATURE-TxnAmend.md)
  intent: Amend changes only the amount; date, account, category, and memo read back exactly as they were created.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    900100002,2026-05-02,ZZAM2,ZZAMC2,35.50,keep this memo
- PASS: txn-amend-absent (FEATURE-TxnAmend.md)
  intent: Amending an id that does not exist exits 4, prints nothing to stdout, and creates no row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: transaction 900199999 does not exist
- PASS: txn-amend-negative-balance (FEATURE-TxnAmend.md)
  intent: An amend that would leave the account balance below zero exits 3 and keeps the original amount, while an amend landing exactly on zero succeeds. The account holds +10000 and -4000 cents, so lowering the first to 3000 gives -1000 and lowering it to 4000 gives 0.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account ZZAM3 would be overdrawn by 1000 cents
    
    txn_id,date,account,category,amount,memo
    900100003,2026-05-03,ZZAM3,ZZAMC3,40.00,
- PASS: txn-amend-invalid-amount (FEATURE-TxnAmend.md)
  intent: Amounts with three decimals, a zero amount, and a non-numeric amount are rejected with exit 3 and the stored amount is unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: amount must look like -12.50 with at most two decimals: '1.234'
    
    
    error: amount must not be zero
    
    
    error: amount must not be zero
    
    
    error: amount must look like -12.50 with at most two decimals: 'abc'
- PASS: txn-amend-usage (FEATURE-TxnAmend.md)
  intent: A wrong argument count for txn amend exits 2 with nothing on stdout.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    usage: wrong number of arguments for 'txn amend'
    
    
    usage: wrong number of arguments for 'txn amend'
    
    
    usage: wrong number of arguments for 'txn amend'
- PASS: load-categories-success (FEATURE-LoadCategories.md)
  intent: a valid categories file loads every row, prints the declared two CSV rows with the loaded count, and the rows are readable afterward.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    table,loaded
    categories,3
- PASS: load-categories-rejected-row-stores-nothing (FEATURE-LoadCategories.md)
  intent: when a later row is invalid, exit 3 is returned, stdout is empty, and none of the earlier valid rows is stored.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: load-categories-invalid-fields (FEATURE-LoadCategories.md)
  intent: each invalid code or description (bad characters, empty, over length, comma) rejects the whole file with exit 3 and stores no row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: load-categories-duplicates-rejected (FEATURE-LoadCategories.md)
  intent: a code repeated inside the file, and a code already stored, each reject the whole file with exit 3 and leave the stored row unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: load-categories-header-and-usage (FEATURE-LoadCategories.md)
  intent: a wrong header exits 3 with nothing stored, and a missing file argument is a usage error with exit 2.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transfer-success (FEATURE-Transfer.md)
  intent: A valid transfer exits 0 and prints two rows with consecutive ids starting at the previous maximum plus one, category TRANSFER, the signed amounts, and the specified memos; a separate read shows both stored.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    900300002,2026-05-10,ZZTF1,TRANSFER,-250.00,transfer to ZZTF2
    900300003,2026-05-10,ZZTF2,TRANSFER,250.00,transfer from ZZTF1
- PASS: transfer-conserves-cash (FEATURE-Transfer.md)
  intent: A valid transfer moves cash without changing the total held by the two accounts, computed from stored rows before and after.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    900300011,2026-05-11,ZZTF3,TRANSFER,-123.45,transfer to ZZTF4
    900300012,2026-05-11,ZZTF4,TRANSFER,123.45,transfer from ZZTF3
- PASS: transfer-insufficient-funds (FEATURE-Transfer.md)
  intent: A transfer exceeding the source balance by one cent exits 3 and stores neither row; a transfer of exactly the balance then succeeds and leaves the source at zero.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account ZZTF5 would be overdrawn by 1 cents
    
    txn_id,date,account,category,amount,memo
    900300021,2026-05-12,ZZTF5,TRANSFER,-100.00,transfer to ZZTF6
    900300022,2026-05-12,ZZTF6,TRANSFER,100.00,transfer from ZZTF5
- PASS: transfer-rejections (FEATURE-Transfer.md)
  intent: Same source and destination, zero or negative amounts, three decimals, an impossible date, and an unknown account are each rejected with exit 3, with empty stdout and no new rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ('ZZTF7', 'ZZTF7', '5.00', '2026-05-13') 3  error: transfer needs two different accounts
    
    ('ZZTF7', 'ZZTF8', '0', '2026-05-13') 3  error: amount must not be zero
    
    ('ZZTF7', 'ZZTF8', '-5.00', '2026-05-13') 3  error: transfer amount must be positive
    
    ('ZZTF7', 'ZZTF8', '5.001', '2026-05-13') 3  error: amount must look like -12.50 with at most two decimals: '5.001'
    
    ('ZZTF7', 'ZZTF8', '5.00', '2026-02-30') 3  error: date is not a real calendar date: 2026-02-30
    
    ('ZZTF7', 'ZZTFNONE', '5.00', '2026-05-13') 3  error: account ZZTFNONE does not exist
    
    ('ZZTFNONE', 'ZZTF8', '5.00', '2026-05-13') 3  error: account ZZTFNONE does not exist
- PASS: transfer-usage (FEATURE-Transfer.md)
  intent: A wrong argument count for transfer exits 2 with nothing on stdout.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    usage: wrong number of arguments for 'transfer'
    
    
    usage: wrong number of arguments for 'transfer'
    
    
    usage: wrong number of arguments for 'transfer'

## Build summary
I'll start by inspecting the build directory and the staged sources.The project already has a CLI, ledger_core, and persistence layer. I'll read the existing modules the new commands must plug into.The persistence output was truncated. I'll pull just the schema method signatures, the remaining test files, and the test script.The `ledger` launcher, `cli` dispatch, and ledger_core are in place. Next I need the generated persistence operations for update and delete, plus the existing tests for conventions.Existing account and transaction commands are partial, and `load` is a placeholder. The remaining question is whether the shipped persistence layer offers an atomic multi-row write for the all-or-nothing loads and transfer. I'll check that next.The persistence API autocommits each operation, with no public transaction scope outside the test rollback. Before I settle on the atomicity approach, I'll confirm there is no commit or batch primitive.Baseline is 240 passing tests. The shipped persistence layer autocommits every operation and exposes no transaction scope, so multi-row writes can't be wrapped in one database transaction from the application side. Before editing, I'll check whether existing tests pin the placeholder `load` behaviour I'm about to replace.Existing CSV-reader tests remain valid under the new load. I have enough context to build. My plan:

- **Atomicity:** validate every row or check before the first write, then insert in order. If a later insert fails, delete the rows already inserted. The shipped persistence layer offers no transaction scope, so this is the closest all-or-nothing behaviour available without reaching around the persistence package.
- **Layout:** a small `ledger_core/atomic.py` helper, `parse_txn_id` in `ledger_core/transactions.py`, `load.py` rewritten for accounts and categories, new commands in the existing account and transaction modules, and a new `transfers.py`.

I'll start with the shared helper and the id parser.The Write and Edit tools need each existing file read through the Read tool first, so I'll do that for the three command modules I'm extending.I'll rewrite `load.py` so accounts and categories are real all-or-nothing loads, and keep the transactions placeholder as it is.Now the account commands: `get`, `rename`, and `delete`, each checked in the order the feature specs state.Next, the transaction commands `get`, `delete`, and `amend`, using the balance rule for the two that change amounts.Last command module: `transfer`, a two-row write that reuses the balance rule and the all-or-nothing helper.All nine commands are in place. Before writing new tests, I'll run the existing suite to catch regressions from the refactor.The existing 242 tests pass (240 baseline plus two more already in the suite). Now the new tests, one file per story group, each reading state back through the persistence interface.I'll drop one weak test I wrote at the end of that file, since it asserts nothing the other tests don't already cover.Now the account tests for `get`, `rename`, and `delete`.Next, the transaction tests for `get`, `delete`, and `amend`.One test I just wrote is wrong: amending 303 to -10.00 with 304 at -4000 would overdraw the account. I'll give the account a deposit so the negative amend is actually allowed.Now the transfer tests: the success case, cash conservation, the balance boundary, the rejections, and usage.In `test_transfer_without_transfer_category_is_rejected` I insert a transaction before its category exists, which would violate the foreign key. I'll reorder that setup.I'll add direct unit tests for the two new `ledger_core` helpers, then run everything.That failure is a mistake in my test, not the code. Deleting +4000 from a balance of 0 leaves -4000, so exit 3 is correct. To test the exact-zero boundary I need a remaining balance of exactly zero after the delete, so I'll set up three rows.Now the full suite, plus the staged acceptance runner `sources/run.sh`, which is the terminal check for the whole project.The unit suite passes: 365 tests, exit 0. The `run.sh` tail shows failures, but the `exit=0` there is from `tail`, not the script. I need the start of that output to see whether the seed loads (B1–B3) pass, because the later failures depend on them.The remaining `run.sh` failures are outside this block. B3 and the later checks that rely on seeded transactions fail because `load transactions` is still the placeholder, which is a separate story. The C-series reports (`report balances`, `categories`, `monthly`) are not implemented in any story in this block. Every check that depends only on this block's commands passes (E1–E5, E7–E8, F4–F7, F9, G2–G3, U and Z series). I'll confirm the set of files I changed.All nine stories in this block are implemented and `sh bin/test.sh` passes: 365 tests, exit 0, up from the 240 I found at the start.

Acceptance (`sources/run.sh`, the terminal check) is not green, and that is outside this block. 23 of 43 checks pass. The failures come from two things this block does not cover:

- **`load transactions` is still the placeholder.** Seeded transactions never load, so every check that depends on them fails: B3, B4, D1, D3, E6, F8, G1, G4–G6, and F10.
- **The `report` commands are not in any story here.** C1–C3 and H1–H3 fail with "unknown command".

The checks that depend only on this block's commands pass: E1–E5, E7–E8, F4–F7, F9, G2–G3, and the U and Z series. I could not verify E6, F8, G1, G4 and G5 end to end without seeded transactions. The unit tests cover those paths.

RESULT: SUCCESS

FILES CHANGED:
- ledger_core/atomic.py (new)
- ledger_core/transactions.py
- cli/commands/load.py
- cli/commands/accounts.py
- cli/commands/transactions.py
- cli/commands/transfers.py (new)
- tests/test_load.py (new)
- tests/test_account_manage.py (new)
- tests/test_txn_manage.py (new)
- tests/test_transfer.py (new)
- tests/test_atomic.py (new)

SUMMARY:
- **`load accounts` / `load categories`**: each row is validated, duplicates within the file and against the store are checked, and only then are rows inserted. A failing insert removes the rows already stored and exits 1. Header-only files load zero rows. `load transactions` stays a placeholder.
- **`account get | rename | delete`**: `get` and `rename` return the live row. `rename` validates the name first. `delete` checks existence (4), then whether the account has transactions (3).
- **`txn get | delete | amend`**: `get` is read-only. `delete` and `amend` run the balance rule before writing, so a rejected change stores nothing. An exact zero balance is allowed.
- **`transfer`**: checks everything, including the source balance after the debit, then writes two rows with consecutive ids. Both rows print.
- Test runs: `sh bin/test.sh` → 365 passed, exit 0. `sh sources/run.sh` → 23 of 43 passed, exit 1 (failures explained above).

Choices I made where the spec was silent or the library fell short:
1. **Atomicity by compensation, not a real transaction.** The shipped persistence layer autocommits every operation and exposes no transaction scope. I validate everything first, then insert in order and undo on failure. A failure during the undo itself would still leave partial rows. Real atomicity would need a transaction API in the shipped persistence package.
2. **Transaction ids accept an optional leading minus** (`-?[0-9]+`). A negative id is then absent and exits 4, not 3.
3. **The category description reuses the name validator.** Only the diagnostic wording differs, not the rule.

Not run: the Programmatic Acceptance blocks in the spec are for Drydock's harness to execute. I did not run them. My tests cover the same behaviours in-process, but I have not confirmed the harness verdict.

<blueprint-decisions>
[{"spec":"FEATURE-LoadAccounts.md","severity":"Material","subject":"All-or-nothing insert atomicity","decision":"The shipped persistence layer autocommits each operation and offers no transaction scope to application code. I validate every row before the first write, insert in order, and delete the already-inserted rows if a later insert fails (ledger_core/atomic.py). This is compensating rollback, not a single database transaction; a crash between insert and undo could leave partial rows. Is compensation acceptable, or should the persistence package gain a transaction operation on replan?"},{"spec":"FEATURE-TxnDelete.md","severity":"Low","subject":"Transaction id parsing","decision":"Ids match -?[0-9]+, so a leading minus is accepted and then reported as absent (exit 4) rather than non-integer (exit 3). Tighten to digits only if the spec intends that."}]
</blueprint-decisions>
