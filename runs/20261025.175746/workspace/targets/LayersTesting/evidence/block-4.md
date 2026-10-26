# Evidence: Block 4 · Service (block-4)

- block type: block
- date: 2026-10-25
- resulting state: closed/verified
- story points (combined assembled cost): 47146
- execution id: 20261025.182446.803Z-c29f05bf

## Stories built
- Implement ledger load transactions keeping file txn_ids, with balance checking. (load-transactions) [story]
- Implement ledger account get. (account-get) [story]
- Implement ledger txn get. (txn-get) [story]
- Implement ledger account rename. (account-rename) [story]
- Implement ledger account delete. (account-delete) [story]
- Implement ledger account add. (account-add) [story]
- Implement ledger txn delete. (txn-delete) [story]
- Implement ledger report monthly. (report-monthly) [story]
- Implement ledger txn amend. (txn-amend) [story]
- Implement ledger report balances. (report-balances) [story]
- Implement ledger report categories. (report-categories) [story]
- Implement ledger txn post. (txn-post) [story]
- Implement ledger transfer between two accounts atomically. (transfer-command) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1156)
- implements: FEATURE-LoadTransactions.md (SP 4602)
- context: ARCHITECTURE_compact.md (SP 475)
- context: DATABASE.md (SP 7219)
- stack: common_compact.md (SP 1653)
- stack: cli.md (SP 2689)
- implements: FEATURE-AccountGet.md (SP 1497)
- implements: FEATURE-TxnGet.md (SP 1668)
- implements: FEATURE-AccountRename.md (SP 1680)
- implements: FEATURE-AccountDelete.md (SP 1737)
- implements: FEATURE-AccountAdd.md (SP 1906)
- implements: FEATURE-TxnDelete.md (SP 1971)
- implements: FEATURE-ReportMonthly.md (SP 2325)
- implements: FEATURE-TxnAmend.md (SP 2514)
- implements: FEATURE-ReportBalances.md (SP 2571)
- implements: FEATURE-ReportCategories.md (SP 2793)
- implements: FEATURE-TxnPost.md (SP 3129)
- implements: FEATURE-Transfer.md (SP 3822)

## Build directory changes
- cli/balance.py
- cli/commands/account_add.py
- cli/commands/account_delete.py
- cli/commands/account_get.py
- cli/commands/account_rename.py
- cli/commands/load_transactions.py
- cli/commands/report_balances.py
- cli/commands/report_categories.py
- cli/commands/report_monthly.py
- cli/commands/transfer.py
- cli/commands/txn_amend.py
- cli/commands/txn_delete.py
- cli/commands/txn_get.py
- cli/commands/txn_post.py
- cli/output.py
- cli/validate.py
- cli/writes.py
- data/logs/test_2026-10-25_142539.log
- data/logs/test_2026-10-25_142703.log
- data/logs/test_2026-10-25_142818.log
- data/logs/test_2026-10-25_143005.log
- tests/test_account_commands.py
- tests/test_load_transactions.py
- tests/test_reports.py
- tests/test_transfer.py
- tests/test_txn_commands.py

## Pre-build acceptance observation
- RED: load-transactions-valid (FEATURE-LoadTransactions.md)
  intent: A valid transactions file keeps its txn_ids, stores integer cents, and reports the loaded count.
  return code: 1
  stdout:
    error: unknown command: load transactions /tmp/tmp86h3ypz4/txns.csv
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-valid.py", line 31, in <module>
        assert code == 0
    AssertionError
- RED: load-transactions-unknown-references (FEATURE-LoadTransactions.md)
  intent: An unknown account or unknown category in the last row exits 3 and stores none of the preceding valid rows.
  return code: 1
  stdout:
    error: unknown command: load transactions /tmp/tmp_xzvx099/refs0.csv
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-unknown-references.py", line 27, in <module>
        assert code == 3
    AssertionError
- RED: load-transactions-field-rules (FEATURE-LoadTransactions.md)
  intent: An impossible date, a third decimal place, a zero amount, and a non-integer id each reject the whole file with exit 3.
  return code: 1
  stdout:
    error: unknown command: load transactions /tmp/tmpxao_e024/fields0.csv
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-field-rules.py", line 29, in <module>
        assert code == 3
    AssertionError
- RED: load-transactions-duplicate-ids (FEATURE-LoadTransactions.md)
  intent: A txn_id repeated in the file or already stored rejects the whole file with exit 3 and changes nothing.
  return code: 1
  stdout:
    error: unknown command: load transactions /tmp/tmpsph7dfrm/store.csv
  stderr:
    --- drydock: values at failure ---
      code = 2
      out = ''
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-duplicate-ids.py", line 29, in <module>
        assert code == 3 and out == ""
    AssertionError
- RED: load-transactions-negative-balance (FEATURE-LoadTransactions.md)
  intent: A file that would leave an account balance below zero exits 3 and stores none of its rows.
  return code: 1
  stdout:
    error: unknown command: load transactions /tmp/tmpq4hq72m3/overdraw.csv
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-negative-balance.py", line 25, in <module>
        assert code == 3
    AssertionError
- RED: load-transactions-header-and-usage (FEATURE-LoadTransactions.md)
  intent: A mismatched header exits 3, a missing file exits 1, and a missing file argument exits 2.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
      out = ''
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-header-and-usage.py", line 16, in <module>
        assert code == 3 and out == ""
    AssertionError
- RED: account-get-row (FEATURE-AccountGet.md)
  intent: Getting an existing account prints its name, transaction count, and a balance computed from its stored transactions.
  return code: 1
  stdout:
    error: unknown command: account get UTGET1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-get-row.py", line 25, in <module>
        assert code == 0
    AssertionError
- RED: account-get-empty (FEATURE-AccountGet.md)
  intent: An account with no transactions reports zero transactions and a zero balance.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-get-empty.py", line 12, in <module>
        assert code == 0
    AssertionError
- RED: account-get-absent (FEATURE-AccountGet.md)
  intent: An absent account exits 4 with nothing on standard output.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-get-absent.py", line 8, in <module>
        assert code == 4
    AssertionError
- GREEN (prepassed): account-get-usage (FEATURE-AccountGet.md)
  intent: A wrong argument count exits 2.
  return code: 0
- RED: txn-get-present (FEATURE-TxnGet.md)
  intent: Getting a stored transaction prints its header and a row carrying the stored values with a two-decimal amount.
  return code: 1
  stdout:
    error: unknown command: txn get 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-get-present.py", line 23, in <module>
        assert code == 0
    AssertionError
- RED: txn-get-negative-amount (FEATURE-TxnGet.md)
  intent: A negative stored amount prints with a leading minus sign and two decimals.
  return code: 1
  stdout:
    error: unknown command: txn get 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-get-negative-amount.py", line 21, in <module>
        assert code == 0
    AssertionError
- RED: txn-get-absent (FEATURE-TxnGet.md)
  intent: Getting an id that is not stored exits 4 with nothing on standard output.
  return code: 1
  stdout:
    error: unknown command: txn get 1000
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-get-absent.py", line 8, in <module>
        assert code == 4
    AssertionError
- RED: txn-get-bad-arguments (FEATURE-TxnGet.md)
  intent: A non-integer id exits 3 and a wrong argument count exits 2.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-get-bad-arguments.py", line 4, in <module>
        assert code == 3
    AssertionError
- RED: account-rename-updates (FEATURE-AccountRename.md)
  intent: Renaming prints the row with the new name and persists it, leaving the transaction count unchanged.
  return code: 1
  stdout:
    error: unknown command: account rename UTREN1 Event Cash Box
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-rename-updates.py", line 20, in <module>
        assert code == 0
    AssertionError
- RED: account-rename-absent (FEATURE-AccountRename.md)
  intent: Renaming an absent account exits 4, prints nothing, and creates no account.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-rename-absent.py", line 7, in <module>
        assert code == 4
    AssertionError
- RED: account-rename-invalid-name (FEATURE-AccountRename.md)
  intent: An empty, over-long, or comma-containing name exits 3 and leaves the stored name unchanged.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      bad = ''
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-rename-invalid-name.py", line 10, in <module>
        assert code == 3, bad
    AssertionError
- GREEN (prepassed): account-rename-usage (FEATURE-AccountRename.md)
  intent: A wrong argument count exits 2 and changes nothing.
  return code: 0
- RED: account-delete-unused (FEATURE-AccountDelete.md)
  intent: Deleting an account with no transactions exits 0, prints deleted and the code, and removes it.
  return code: 1
  stdout:
    error: unknown command: account delete UTDEL1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-delete-unused.py", line 13, in <module>
        assert code == 0
    AssertionError
- RED: account-delete-in-use (FEATURE-AccountDelete.md)
  intent: Deleting an account that has transactions exits 3, prints nothing, and keeps the account and its transaction.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-delete-in-use.py", line 14, in <module>
        assert code == 3
    AssertionError
- RED: account-delete-absent (FEATURE-AccountDelete.md)
  intent: Deleting an absent account exits 4 with nothing on standard output.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-delete-absent.py", line 8, in <module>
        assert code == 4
    AssertionError
- RED: account-delete-then-get (FEATURE-AccountDelete.md)
  intent: After a successful delete, account get for the same code exits 4.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-delete-then-get.py", line 8, in <module>
        assert code == 0
    AssertionError
- GREEN (prepassed): account-delete-usage (FEATURE-AccountDelete.md)
  intent: A wrong argument count exits 2 and removes nothing.
  return code: 0
- RED: account-add-stores (FEATURE-AccountAdd.md)
  intent: Adding an account exits 0, prints the account row with zero transactions, and persists the account.
  return code: 1
  stdout:
    error: unknown command: account add UTADD1 Event Float
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-add-stores.py", line 15, in <module>
        assert code == 0
    AssertionError
- RED: account-add-duplicate (FEATURE-AccountAdd.md)
  intent: Adding an existing code exits 3, prints nothing on standard output, and leaves the stored name unchanged.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-add-duplicate.py", line 9, in <module>
        assert code == 3
    AssertionError
- RED: account-add-invalid-code (FEATURE-AccountAdd.md)
  intent: Codes that are lowercase, too long, or empty are rejected with exit 3 and nothing is stored.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      bad = 'lower1'
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-add-invalid-code.py", line 9, in <module>
        assert code == 3, bad
    AssertionError: lower1
- RED: account-add-invalid-name (FEATURE-AccountAdd.md)
  intent: Names that are empty, over 40 characters, or contain a comma are rejected with exit 3 and nothing is stored.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      bad = ''
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-add-invalid-name.py", line 9, in <module>
        assert code == 3, bad
    AssertionError
- GREEN (prepassed): account-add-usage (FEATURE-AccountAdd.md)
  intent: A wrong argument count exits 2 and stores nothing.
  return code: 0
- RED: txn-delete-roundtrip (FEATURE-TxnDelete.md)
  intent: Deleting a stored transaction prints deleted and the id, and a later read finds nothing.
  return code: 1
  stdout:
    error: unknown command: txn delete 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-delete-roundtrip.py", line 19, in <module>
        assert code == 0
    AssertionError
- RED: txn-delete-absent (FEATURE-TxnDelete.md)
  intent: Deleting an id that is not stored exits 4 and removes nothing.
  return code: 1
  stdout:
    error: unknown command: txn delete 1000
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-delete-absent.py", line 9, in <module>
        assert code == 4
    AssertionError
- RED: txn-delete-negative-balance (FEATURE-TxnDelete.md)
  intent: Deleting a deposit that later payments depend on exits 3 and keeps the row.
  return code: 1
  stdout:
    error: unknown command: txn delete 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-delete-negative-balance.py", line 22, in <module>
        assert code == 3
    AssertionError
- RED: txn-delete-bad-arguments (FEATURE-TxnDelete.md)
  intent: A non-integer id exits 3 and a wrong argument count exits 2.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-delete-bad-arguments.py", line 4, in <module>
        assert code == 3
    AssertionError
- RED: report-monthly-rows (FEATURE-ReportMonthly.md)
  intent: The monthly report computes count, inflow, outflow, and net for a month from stored rows and places the month row in ascending order before TOTAL.
  return code: 1
  stdout:
    error: unknown command: report monthly
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-monthly-rows.py", line 28, in <module>
        assert code == 0
    AssertionError
- RED: report-monthly-total (FEATURE-ReportMonthly.md)
  intent: The TOTAL row equals the sum of the month rows for count, inflow, outflow, and net.
  return code: 1
  stdout:
    error: unknown command: report monthly
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-monthly-total.py", line 22, in <module>
        assert code == 0
    AssertionError
- RED: report-monthly-total-count (FEATURE-ReportMonthly.md)
  intent: The TOTAL transaction count equals the number of stored transactions read back from the database.
  return code: 1
  stdout:
    error: unknown command: report monthly
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-monthly-total-count.py", line 11, in <module>
        assert code == 0
    AssertionError
- GREEN (prepassed): report-monthly-usage (FEATURE-ReportMonthly.md)
  intent: Extra arguments and an unknown report name exit 2 with nothing on standard output.
  return code: 0
- RED: txn-amend-roundtrip (FEATURE-TxnAmend.md)
  intent: Amending a deposit prints the updated row and persists only the new amount in integer cents.
  return code: 1
  stdout:
    error: unknown command: txn amend 1 60.00
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-amend-roundtrip.py", line 23, in <module>
        assert code == 0
    AssertionError
- RED: txn-amend-absent (FEATURE-TxnAmend.md)
  intent: Amending an id that is not stored exits 4 and stores nothing.
  return code: 1
  stdout:
    error: unknown command: txn amend 1000 1.00
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-amend-absent.py", line 9, in <module>
        assert code == 4
    AssertionError
- RED: txn-amend-negative-balance (FEATURE-TxnAmend.md)
  intent: An amendment that would leave the account balance below zero exits 3 and leaves the amount unchanged.
  return code: 1
  stdout:
    error: unknown command: txn amend 1 0.10
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-amend-negative-balance.py", line 23, in <module>
        assert code == 3
    AssertionError
- RED: txn-amend-invalid-amount (FEATURE-TxnAmend.md)
  intent: A zero or over-precise amount exits 3 and leaves the stored amount unchanged.
  return code: 1
  stdout:
    0 2 error: unknown command: txn amend 1 0
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-amend-invalid-amount.py", line 18, in <module>
        assert code == 3
    AssertionError
- GREEN (prepassed): txn-amend-usage (FEATURE-TxnAmend.md)
  intent: A wrong argument count exits 2.
  return code: 0
- RED: report-balances-rows (FEATURE-ReportBalances.md)
  intent: The report shows each created account's transaction count and balance in two-decimal form, with zero for an account without transactions.
  return code: 1
  stdout:
    error: unknown command: report balances
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-balances-rows.py", line 29, in <module>
        assert code == 0
    AssertionError
- RED: report-balances-order-and-total (FEATURE-ReportBalances.md)
  intent: Account rows are ordered by code and the TOTAL row equals the sum of the account rows' counts and balances.
  return code: 1
  stdout:
    error: unknown command: report balances
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-balances-order-and-total.py", line 28, in <module>
        assert code == 0
    AssertionError
- RED: report-balances-reflects-changes (FEATURE-ReportBalances.md)
  intent: The report is recomputed from stored rows, so a later transaction changes the balance by exactly its amount.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-balances-reflects-changes.py", line 27, in <module>
        assert code == 0
    AssertionError
- GREEN (prepassed): report-balances-usage (FEATURE-ReportBalances.md)
  intent: An extra argument after balances and an unknown report each exit 2 with nothing on stdout.
  return code: 0
- RED: report-categories-row-values (FEATURE-ReportCategories.md)
  intent: A category's count, inflow, outflow, and net match the cents of the transactions created for it, and an empty category reports zeros.
  return code: 1
  stdout:
    error: unknown command: report categories
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-categories-row-values.py", line 30, in <module>
        assert code == 0
    AssertionError
- RED: report-categories-order-and-total (FEATURE-ReportCategories.md)
  intent: Category rows are ordered by code and the TOTAL row equals the sums of the category rows and the stored transaction count.
  return code: 1
  stdout:
    error: unknown command: report categories
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-categories-order-and-total.py", line 28, in <module>
        assert code == 0
    AssertionError
- RED: report-categories-reflects-changes (FEATURE-ReportCategories.md)
  intent: The report is recomputed from stored rows, so a later outflow raises the category's outflow and lowers its net by exactly its amount.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-categories-reflects-changes.py", line 27, in <module>
        assert code == 0
    AssertionError
- GREEN (prepassed): report-categories-usage (FEATURE-ReportCategories.md)
  intent: An extra argument after categories exits 2 with nothing on stdout.
  return code: 0
- RED: txn-post-roundtrip (FEATURE-TxnPost.md)
  intent: A valid post prints the stored row, assigns the largest id plus one, and persists the amount as integer cents.
  return code: 1
  stdout:
    error: unknown command: txn post TPOST1 TPCAT1 45.50 2026-04-01 walk in sale
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-post-roundtrip.py", line 20, in <module>
        assert code == 0
    AssertionError
- RED: txn-post-memo-optional (FEATURE-TxnPost.md)
  intent: A post without a memo succeeds and stores an empty memo.
  return code: 1
  stdout:
    error: unknown command: txn post TPOST2 TPCAT2 10.00 2026-04-02
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-post-memo-optional.py", line 15, in <module>
        assert code == 0
    AssertionError
- RED: txn-post-rejects-invalid (FEATURE-TxnPost.md)
  intent: An unknown account, unknown category, over-precise amount, zero amount, or impossible date exits 3 and stores nothing.
  return code: 1
  stdout:
    ('TPNOACCT', 'TPCAT3', '1.00', '2026-04-01') 2 error: unknown command: txn post TPNOACCT TPCAT3 1.00 2026-04-01
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-post-rejects-invalid.py", line 22, in <module>
        assert code == 3
    AssertionError
- RED: txn-post-negative-balance (FEATURE-TxnPost.md)
  intent: A payment larger than the account balance exits 3 and stores nothing, while a payment within the balance succeeds.
  return code: 1
  stdout:
    error: unknown command: txn post TPOST4 TPCAT4 -10.01 2026-04-02
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-post-negative-balance.py", line 18, in <module>
        assert code == 3
    AssertionError
- GREEN (prepassed): txn-post-usage (FEATURE-TxnPost.md)
  intent: Too few or too many arguments exit 2 and store nothing.
  return code: 0
- RED: transfer-valid (FEATURE-Transfer.md)
  intent: A valid transfer prints two consecutive-id TRANSFER rows with opposite amounts and stores both.
  return code: 1
  stdout:
    error: unknown command: transfer TRFSRC1 TRFDST1 250.00 2026-04-03
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfer-valid.py", line 26, in <module>
        assert code == 0
    AssertionError
- RED: transfer-conserves-cash (FEATURE-Transfer.md)
  intent: A valid transfer changes the two balances by opposite amounts and leaves their combined total unchanged.
  return code: 1
  stdout:
    error: unknown command: transfer TRFSRC2 TRFDST2 100.00 2026-04-03
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfer-conserves-cash.py", line 28, in <module>
        assert code == 0
    AssertionError
- RED: transfer-rejects-invalid (FEATURE-Transfer.md)
  intent: Equal accounts, a zero or negative amount, an unknown account, or an impossible date exit 3 and store no rows.
  return code: 1
  stdout:
    ('TRFSRC3', 'TRFSRC3', '10.00', '2026-04-03') 2 error: unknown command: transfer TRFSRC3 TRFSRC3 10.00 2026-04-03
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfer-rejects-invalid.py", line 31, in <module>
        assert code == 3
    AssertionError
- RED: transfer-insufficient-funds (FEATURE-Transfer.md)
  intent: A transfer larger than the source balance exits 3 and stores neither row.
  return code: 1
  stdout:
    error: unknown command: transfer TRFSRC4 TRFDST4 100.01 2026-04-03
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfer-insufficient-funds.py", line 23, in <module>
        assert code == 3
    AssertionError
- GREEN (prepassed): transfer-usage (FEATURE-Transfer.md)
  intent: A wrong argument count exits 2 and stores nothing.
  return code: 0

## Post-build programmatic acceptance
- PASS: load-transactions-valid (FEATURE-LoadTransactions.md)
  intent: A valid transactions file keeps its txn_ids, stores integer cents, and reports the loaded count.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    table,loaded
    transactions,3
- PASS: load-transactions-unknown-references (FEATURE-LoadTransactions.md)
  intent: An unknown account or unknown category in the last row exits 3 and stores none of the preceding valid rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: row 2: no account UTMBNONE
    
    error: row 2: no category UTMDNONE
- PASS: load-transactions-field-rules (FEATURE-LoadTransactions.md)
  intent: An impossible date, a third decimal place, a zero amount, and a non-integer id each reject the whole file with exit 3.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: date must be a real calendar date as YYYY-MM-DD: '2026-02-30'
    
    error: amount must look like 12.50 or -3.1, with at most two decimals: '1.234'
    
    error: amount must not be zero
    
    error: txn_id must be an integer: 'abc'
- PASS: load-transactions-duplicate-ids (FEATURE-LoadTransactions.md)
  intent: A txn_id repeated in the file or already stored rejects the whole file with exit 3 and changes nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: row 2: txn_id 910301 is repeated or already stored
    
    error: row 2: txn_id 910303 is repeated or already stored
- PASS: load-transactions-negative-balance (FEATURE-LoadTransactions.md)
  intent: A file that would leave an account balance below zero exits 3 and stores none of its rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: balance of UTMG1 would be -0.01, below zero
- PASS: load-transactions-header-and-usage (FEATURE-LoadTransactions.md)
  intent: A mismatched header exits 3, a missing file exits 1, and a missing file argument exits 2.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-get-row (FEATURE-AccountGet.md)
  intent: Getting an existing account prints its name, transaction count, and a balance computed from its stored transactions.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    UTGET1,Get Probe,2,74.50
- PASS: account-get-empty (FEATURE-AccountGet.md)
  intent: An account with no transactions reports zero transactions and a zero balance.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-get-absent (FEATURE-AccountGet.md)
  intent: An absent account exits 4 with nothing on standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-get-usage (FEATURE-AccountGet.md)
  intent: A wrong argument count exits 2.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: txn-get-present (FEATURE-TxnGet.md)
  intent: Getting a stored transaction prints its header and a row carrying the stored values with a two-decimal amount.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    1,2026-04-01,TGET1,TGCAT1,12.34,get probe
- PASS: txn-get-negative-amount (FEATURE-TxnGet.md)
  intent: A negative stored amount prints with a leading minus sign and two decimals.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    1,2026-04-02,TGET2,TGCAT2,-12.50,
- PASS: txn-get-absent (FEATURE-TxnGet.md)
  intent: Getting an id that is not stored exits 4 with nothing on standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: no transaction 1000
- PASS: txn-get-bad-arguments (FEATURE-TxnGet.md)
  intent: A non-integer id exits 3 and a wrong argument count exits 2.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-rename-updates (FEATURE-AccountRename.md)
  intent: Renaming prints the row with the new name and persists it, leaving the transaction count unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    UTREN1,Event Cash Box,1,5.00
- PASS: account-rename-absent (FEATURE-AccountRename.md)
  intent: Renaming an absent account exits 4, prints nothing, and creates no account.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-rename-invalid-name (FEATURE-AccountRename.md)
  intent: An empty, over-long, or comma-containing name exits 3 and leaves the stored name unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-rename-usage (FEATURE-AccountRename.md)
  intent: A wrong argument count exits 2 and changes nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-delete-unused (FEATURE-AccountDelete.md)
  intent: Deleting an account with no transactions exits 0, prints deleted and the code, and removes it.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    deleted
    UTDEL1
- PASS: account-delete-in-use (FEATURE-AccountDelete.md)
  intent: Deleting an account that has transactions exits 3, prints nothing, and keeps the account and its transaction.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-delete-absent (FEATURE-AccountDelete.md)
  intent: Deleting an absent account exits 4 with nothing on standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-delete-then-get (FEATURE-AccountDelete.md)
  intent: After a successful delete, account get for the same code exits 4.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-delete-usage (FEATURE-AccountDelete.md)
  intent: A wrong argument count exits 2 and removes nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-add-stores (FEATURE-AccountAdd.md)
  intent: Adding an account exits 0, prints the account row with zero transactions, and persists the account.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    UTADD1,Event Float,0,0.00
- PASS: account-add-duplicate (FEATURE-AccountAdd.md)
  intent: Adding an existing code exits 3, prints nothing on standard output, and leaves the stored name unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-add-invalid-code (FEATURE-AccountAdd.md)
  intent: Codes that are lowercase, too long, or empty are rejected with exit 3 and nothing is stored.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-add-invalid-name (FEATURE-AccountAdd.md)
  intent: Names that are empty, over 40 characters, or contain a comma are rejected with exit 3 and nothing is stored.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-add-usage (FEATURE-AccountAdd.md)
  intent: A wrong argument count exits 2 and stores nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: txn-delete-roundtrip (FEATURE-TxnDelete.md)
  intent: Deleting a stored transaction prints deleted and the id, and a later read finds nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    deleted
    1
- PASS: txn-delete-absent (FEATURE-TxnDelete.md)
  intent: Deleting an id that is not stored exits 4 and removes nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: no transaction 1000
- PASS: txn-delete-negative-balance (FEATURE-TxnDelete.md)
  intent: Deleting a deposit that later payments depend on exits 3 and keeps the row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: balance of TDEL2 would be -5.00, below zero
- PASS: txn-delete-bad-arguments (FEATURE-TxnDelete.md)
  intent: A non-integer id exits 3 and a wrong argument count exits 2.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: report-monthly-rows (FEATURE-ReportMonthly.md)
  intent: The monthly report computes count, inflow, outflow, and net for a month from stored rows and places the month row in ascending order before TOTAL.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    month,transactions,inflow,outflow,net
    2098-05,2,100.00,25.50,74.50
    2098-06,1,40.01,0.00,40.01
    TOTAL,3,140.01,25.50,114.51
- PASS: report-monthly-total (FEATURE-ReportMonthly.md)
  intent: The TOTAL row equals the sum of the month rows for count, inflow, outflow, and net.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    month,transactions,inflow,outflow,net
    2098-07,1,123.45,0.00,123.45
    2098-08,1,0.00,3.45,-3.45
    TOTAL,2,123.45,3.45,120.00
- PASS: report-monthly-total-count (FEATURE-ReportMonthly.md)
  intent: The TOTAL transaction count equals the number of stored transactions read back from the database.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    month,transactions,inflow,outflow,net
    TOTAL,0,0.00,0.00,0.00
- PASS: report-monthly-usage (FEATURE-ReportMonthly.md)
  intent: Extra arguments and an unknown report name exit 2 with nothing on standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: txn-amend-roundtrip (FEATURE-TxnAmend.md)
  intent: Amending a deposit prints the updated row and persists only the new amount in integer cents.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    1,2026-04-01,TAMD1,TACAT1,60.00,amend probe
- PASS: txn-amend-absent (FEATURE-TxnAmend.md)
  intent: Amending an id that is not stored exits 4 and stores nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: no transaction 1000
- PASS: txn-amend-negative-balance (FEATURE-TxnAmend.md)
  intent: An amendment that would leave the account balance below zero exits 3 and leaves the amount unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: balance of TAMD2 would be -4.90, below zero
- PASS: txn-amend-invalid-amount (FEATURE-TxnAmend.md)
  intent: A zero or over-precise amount exits 3 and leaves the stored amount unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    0 3 error: amount must not be zero
    
    1.234 3 error: amount must look like 12.50 or -3.1, with at most two decimals: '1.234'
    
    abc 3 error: amount must look like 12.50 or -3.1, with at most two decimals: 'abc'
- PASS: txn-amend-usage (FEATURE-TxnAmend.md)
  intent: A wrong argument count exits 2.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: report-balances-rows (FEATURE-ReportBalances.md)
  intent: The report shows each created account's transaction count and balance in two-decimal form, with zero for an account without transactions.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    UTRB1,Funded,3,719.49
    UTRB2,Empty,0,0.00
    TOTAL,,3,719.49
- PASS: report-balances-order-and-total (FEATURE-ReportBalances.md)
  intent: Account rows are ordered by code and the TOTAL row equals the sum of the account rows' counts and balances.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    UTRC1,Early,1,7.00
    UTRC9,Late,1,25.00
    TOTAL,,2,32.00
- PASS: report-balances-reflects-changes (FEATURE-ReportBalances.md)
  intent: The report is recomputed from stored rows, so a later transaction changes the balance by exactly its amount.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: report-balances-usage (FEATURE-ReportBalances.md)
  intent: An extra argument after balances and an unknown report each exit 2 with nothing on stdout.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: report-categories-row-values (FEATURE-ReportCategories.md)
  intent: A category's count, inflow, outflow, and net match the cents of the transactions created for it, and an empty category reports zeros.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    category,description,transactions,inflow,outflow,net
    UTSC1,Used,4,519.99,13.25,506.74
    UTSC2,Unused,0,0.00,0.00,0.00
    TOTAL,,4,519.99,13.25,506.74
- PASS: report-categories-order-and-total (FEATURE-ReportCategories.md)
  intent: Category rows are ordered by code and the TOTAL row equals the sums of the category rows and the stored transaction count.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    category,description,transactions,inflow,outflow,net
    UTSD1,Early,1,0.00,3.00,-3.00
    UTSD9,Late,1,9.00,0.00,9.00
    TOTAL,,2,9.00,3.00,6.00
- PASS: report-categories-reflects-changes (FEATURE-ReportCategories.md)
  intent: The report is recomputed from stored rows, so a later outflow raises the category's outflow and lowers its net by exactly its amount.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: report-categories-usage (FEATURE-ReportCategories.md)
  intent: An extra argument after categories exits 2 with nothing on stdout.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: txn-post-roundtrip (FEATURE-TxnPost.md)
  intent: A valid post prints the stored row, assigns the largest id plus one, and persists the amount as integer cents.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    1,2026-04-01,TPOST1,TPCAT1,45.50,walk in sale
- PASS: txn-post-memo-optional (FEATURE-TxnPost.md)
  intent: A post without a memo succeeds and stores an empty memo.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    1,2026-04-02,TPOST2,TPCAT2,10.00,
- PASS: txn-post-rejects-invalid (FEATURE-TxnPost.md)
  intent: An unknown account, unknown category, over-precise amount, zero amount, or impossible date exits 3 and stores nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ('TPNOACCT', 'TPCAT3', '1.00', '2026-04-01') 3 error: no account TPNOACCT
    
    ('TPOST3', 'TPNOCAT', '1.00', '2026-04-01') 3 error: no category TPNOCAT
    
    ('TPOST3', 'TPCAT3', '1.234', '2026-04-01') 3 error: amount must look like 12.50 or -3.1, with at most two decimals: '1.234'
    
    ('TPOST3', 'TPCAT3', '0', '2026-04-01') 3 error: amount must not be zero
    
    ('TPOST3', 'TPCAT3', '1.00', '2026-02-30') 3 error: date must be a real calendar date as YYYY-MM-DD: '2026-02-30'
    
    ('TPOST3', 'TPCAT3', '1.00', 'not-a-date') 3 error: date must be a real calendar date as YYYY-MM-DD: 'not-a-date'
- PASS: txn-post-negative-balance (FEATURE-TxnPost.md)
  intent: A payment larger than the account balance exits 3 and stores nothing, while a payment within the balance succeeds.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: balance of TPOST4 would be -0.01, below zero
    
    txn_id,date,account,category,amount,memo
    2,2026-04-02,TPOST4,TPCAT4,-5.00,
- PASS: txn-post-usage (FEATURE-TxnPost.md)
  intent: Too few or too many arguments exit 2 and store nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transfer-valid (FEATURE-Transfer.md)
  intent: A valid transfer prints two consecutive-id TRANSFER rows with opposite amounts and stores both.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    2,2026-04-03,TRFSRC1,TRANSFER,-250.00,transfer to TRFDST1
    3,2026-04-03,TRFDST1,TRANSFER,250.00,transfer from TRFSRC1
- PASS: transfer-conserves-cash (FEATURE-Transfer.md)
  intent: A valid transfer changes the two balances by opposite amounts and leaves their combined total unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    3,2026-04-03,TRFSRC2,TRANSFER,-100.00,transfer to TRFDST2
    4,2026-04-03,TRFDST2,TRANSFER,100.00,transfer from TRFSRC2
- PASS: transfer-rejects-invalid (FEATURE-Transfer.md)
  intent: Equal accounts, a zero or negative amount, an unknown account, or an impossible date exit 3 and store no rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ('TRFSRC3', 'TRFSRC3', '10.00', '2026-04-03') 3 error: transfer needs two different accounts
    
    ('TRFSRC3', 'TRFDST3', '0', '2026-04-03') 3 error: amount must not be zero
    
    ('TRFSRC3', 'TRFDST3', '0.00', '2026-04-03') 3 error: amount must not be zero
    
    ('TRFSRC3', 'TRFDST3', '-5.00', '2026-04-03') 3 error: transfer amount must be positive
    
    ('TRFSRC3', 'TRFNONE', '10.00', '2026-04-03') 3 error: no account TRFNONE
    
    ('TRFNONE', 'TRFDST3', '10.00', '2026-04-03') 3 error: no account TRFNONE
    
    ('TRFSRC3', 'TRFDST3', '1.234', '2026-04-03') 3 error: amount must look like 12.50 or -3.1, with at most two decimals: '1.234'
    
    ('TRFSRC3', 'TRFDST3', '10.00', '2026-02-30') 3 error: date must be a real calendar date as YYYY-MM-DD: '2026-02-30'
- PASS: transfer-insufficient-funds (FEATURE-Transfer.md)
  intent: A transfer larger than the source balance exits 3 and stores neither row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: balance of TRFSRC4 would be -0.01, below zero
- PASS: transfer-usage (FEATURE-Transfer.md)
  intent: A wrong argument count exits 2 and stores nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
Baseline is green (124 tests). The existing code has the balance rule, validators, money and loader helpers I need, and the persistence layer is autocommit with no application-level transaction API. I'll build the 13 commands on those helpers, and make the two multi-row writes all-or-nothing by compensating delete on failure.Now the account commands.Now the transaction commands.Now the three reports.Before writing tests, a quick import and smoke check to catch errors early.All 17 commands register and the existing 124 tests still pass. Now the test suite, covering the declared acceptance assertions plus boundaries, starting with the account commands.I left a stray import and a convoluted line in two of those tests. Cleaning them up before running.Now the full suite.The failure is in my test, not the code. `cli_runner` opens its own `Database`, so patching the fixture's instance never reaches the command. I'll test the compensation through `store_transactions` with a wrapper that fails on the second create.Next I'll run the staged acceptance assertions verbatim, not just my restatements of them. I'll extract each `=== AC ===` block from the Feature specs and run it against a throwaway SQLite store in `/tmp`, so `data/app.db` is never touched.All 59 criteria across the 13 Feature specs are extracted. Each criterion writes through the CLI, which opens its own connection, so I'll run each one inside the shipped acceptance transaction (`begin/end_acceptance_transaction`) on a fresh copy of the schema-only store, the way the harness does.My extractor kept the `Intent:` prose line inside each block, so every criterion failed at parse time before running. I'll strip that line and rerun, printing only failures.All 59 declared acceptance criteria pass verbatim. Now the project suite with my new tests.Suite is green at 247 tests. Last, a guardrail check: no floats for money, no driver imports outside `persistence/`, and nothing under `sources/` touched.I implemented all 13 stories in block 4. The project suite passes (247 tests, up from 124), and all 59 declared acceptance criteria from the 13 Feature specs pass when run verbatim.

Verification:
- **Acceptance criteria:** I extracted each `=== AC ===` block and ran it in the shipped acceptance transaction against a fresh schema-only SQLite copy in `/tmp`, so `data/app.db` was not touched. That temp directory is removed.
- **Project suite:** `sh bin/test.sh` exits 0. The 123 new tests read state back from the store after each command, and cover the error exit codes and the boundaries.
- **Guardrails:** no floats in `cli/`, no driver imports outside `persistence/`, and nothing under `sources/` changed.

Choices I made:
- **Atomic writes:** the shipped persistence layer has no multi-statement transaction for the application. `transfer` and `load transactions` therefore write their rows through `cli/writes.py`, which deletes any rows already created if a later create fails. A failure in that cleanup would itself surface as exit 1.
- **Transfer and missing `TRANSFER` category:** the spec does not cover this case. I reject it with exit 3 instead of letting a foreign-key error surface as exit 1.
- **Balance check on load:** the Feature spec (Decision Q-004) checks final balances after the whole file is applied. The build instruction says "in file order." I followed the spec, so a payment that precedes its funding deposit in the file is accepted.
- **Transaction ids:** `txn_id` accepts an optionally signed run of digits. The spec only says "integer."

<blueprint-decisions>
[{"spec":"FEATURE-LoadTransactions.md","severity":"Material","subject":"Balance check scope on load","decision":"The Feature spec checks final per-account balances after the whole file is applied (Q-004). The build instruction asked for a check in file order. I followed the spec, so a row may precede the deposit that funds it. Is final-balance the intended rule, or should a file-order check replace it?"},{"spec":"FEATURE-Transfer.md","severity":"Low","subject":"Atomicity of the two transfer rows","decision":"The persistence layer offers no application-level transaction. Both rows are written through store_transactions, which deletes the first row if the second create fails, then re-raises (exit 1). This gives both-or-neither under a store fault, but is compensation, not a true database transaction."},{"spec":"FEATURE-Transfer.md","severity":"Low","subject":"Missing TRANSFER category","decision":"The spec does not cover a store with no TRANSFER category. I reject it with exit 3, matching the unknown-category rule in txn post, rather than letting a foreign-key failure surface as exit 1."}]
</blueprint-decisions>

RESULT: SUCCESS

FILES CHANGED:
- cli/balance.py
- cli/output.py
- cli/validate.py
- cli/writes.py
- cli/commands/account_add.py
- cli/commands/account_delete.py
- cli/commands/account_get.py
- cli/commands/account_rename.py
- cli/commands/load_transactions.py
- cli/commands/report_balances.py
- cli/commands/report_categories.py
- cli/commands/report_monthly.py
- cli/commands/transfer.py
- cli/commands/txn_amend.py
- cli/commands/txn_delete.py
- cli/commands/txn_get.py
- cli/commands/txn_post.py
- tests/test_account_commands.py
- tests/test_load_transactions.py
- tests/test_reports.py
- tests/test_transfer.py
- tests/test_txn_commands.py

SUMMARY:
Implemented the 13 block-4 stories: load transactions, account get/add/rename/delete, txn get/post/amend/delete, transfer, and report monthly/balances/categories. Each is a self-registering module under `cli/commands/`, using the existing balance rule, validators, money helpers, and loader. `cli/writes.py` makes the multi-row writes all-or-nothing by compensation. Results: `sh bin/test.sh` exit 0, 247 passed (124 existing, 123 new). Staged acceptance criteria: 59 of 59 pass verbatim, run in the acceptance transaction against a temp store. Nothing committed.

BLOCKERS:
- None.
