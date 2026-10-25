# Evidence: Block 4 · Service (block-4)

- block type: block
- date: 2026-10-25
- resulting state: closed/verified
- story points (combined assembled cost): 61134
- execution id: 20261025.163357.169Z-f8b625e4

## Stories built
- Implement `ledger init` to drop and recreate the three tables. (init) [story]
- Implement `ledger count` reporting row counts per table. (count) [story]
- Implement `ledger account add`. (account-add) [story]
- Reject a duplicate account code. (account-duplicate) [story]
- Implement `ledger account get`. (account-get) [story]
- Implement `ledger account rename`. (account-rename) [story]
- Implement `ledger load categories <csv>`. (load-categories) [story]
- Implement `ledger load accounts <csv>`. (load-accounts) [story]
- Implement `ledger txn post`. (txn-post) [story]
- Implement `ledger txn get`. (txn-get) [story]
- Validate transaction post inputs. (txn-validate) [story]
- Implement `ledger txn delete`. (txn-delete) [story]
- Implement `ledger txn amend`. (txn-amend) [story]
- Implement `ledger transfer`. (transfer) [story]
- Implement `ledger load transactions <csv>` keeping file txn_ids. (load-transactions) [story]
- Implement `ledger account delete`. (account-delete) [story]
- Reject a transfer that would overdraw the source. (transfer-overdraw) [story]
- Implement `ledger report balances`. (report-balances) [story]
- Implement `ledger report monthly`. (report-monthly) [story]
- Implement `ledger report categories`. (report-categories) [story]
- Prove an invalid load is rejected atomically with exit 3. (load-rejection) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1156)
- implements: FEATURE-Init.md (SP 1348)
- context: ARCHITECTURE_compact.md (SP 327)
- context: DATABASE_compact.md (SP 453)
- stack: cli.md (SP 2689)
- stack: persistence_compact.md (SP 2693)
- implements: FEATURE-Count.md (SP 1375)
- implements: FEATURE-AccountAdd.md (SP 2047)
- implements: FEATURE-AccountDuplicate.md (SP 1267)
- implements: FEATURE-AccountGet.md (SP 2079)
- implements: FEATURE-AccountRename.md (SP 1916)
- implements: FEATURE-LoadCategories.md (SP 2628)
- implements: FEATURE-LoadAccounts.md (SP 2656)
- implements: FEATURE-TxnPost.md (SP 4112)
- implements: FEATURE-TxnGet.md (SP 2173)
- implements: FEATURE-TxnValidate.md (SP 2187)
- implements: FEATURE-TxnDelete.md (SP 2466)
- implements: FEATURE-TxnAmend.md (SP 3138)
- implements: FEATURE-Transfer.md (SP 3947)
- implements: FEATURE-LoadTransactions.md (SP 4744)
- implements: FEATURE-AccountDelete.md (SP 1836)
- implements: FEATURE-TransferOverdraw.md (SP 1984)
- implements: FEATURE-ReportBalances.md (SP 2284)
- implements: FEATURE-ReportMonthly.md (SP 2407)
- implements: FEATURE-ReportCategories.md (SP 2500)
- implements: FEATURE-LoadRejection.md (SP 2791)

## Build directory changes
- cli/commands/__init__.py
- cli/commands/account.py
- cli/commands/count.py
- cli/commands/init.py
- cli/commands/load.py
- cli/commands/report.py
- cli/commands/transfer.py
- cli/commands/txn.py
- cli/views.py
- data/logs/test_2026-10-25_123930.log
- tests/test_commands.py

## Pre-build acceptance observation
- RED: init-empties-tables (FEATURE-Init.md)
  intent: ledger init exits 0, prints nothing, and leaves all three tables empty even when transactions reference accounts and categories.
  return code: 1
  stdout:
    error: unknown command: init
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "init-empties-tables.py", line 15, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: init-repeatable (FEATURE-Init.md)
  intent: Running ledger init twice in a row succeeds both times.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      first = (2, '', 'error: unknown command: init\n')
    --- drydock: end values ---
    Traceback (most recent call last):
      File "init-repeatable.py", line 5, in <module>
        assert first[0] == 0
               ^^^^^^^^^^^^^
    AssertionError
- GREEN (prepassed): init-usage-error (FEATURE-Init.md)
  intent: ledger init with an extra argument is exit 2 and removes nothing.
  return code: 0
- RED: count-reports-tables (FEATURE-Count.md)
  intent: ledger count lists the three tables in order with counts that grow by the rows the criterion adds.
  return code: 1
  stdout:
    error: unknown command: count
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "count-reports-tables.py", line 27, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: count-after-init (FEATURE-Count.md)
  intent: ledger count reports zero rows in every table after ledger init.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "count-after-init.py", line 7, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- GREEN (prepassed): count-usage-error (FEATURE-Count.md)
  intent: ledger count with an extra argument is exit 2 with nothing on standard output.
  return code: 0
- RED: account-add-valid (FEATURE-AccountAdd.md)
  intent: Adding a valid account prints its zero-balance row and the account reads back with the supplied name.
  return code: 1
  stdout:
    error: unknown command: account add ADDOK1 Added Account
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-add-valid.py", line 11, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: account-add-boundaries (FEATURE-AccountAdd.md)
  intent: A 12-character code and a 40-character name are accepted.
  return code: 1
  stdout:
    error: unknown command: account add ADDMAXCODE12 NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-add-boundaries.py", line 12, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: account-add-invalid-code (FEATURE-AccountAdd.md)
  intent: A code that is too long, lowercase, or contains a forbidden character is rejected with exit 3 and not stored.
  return code: 1
  stdout:
    ADDBADCODE123X  error: unknown command: account add ADDBADCODE123X Some Name
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-add-invalid-code.py", line 8, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- RED: account-add-invalid-name (FEATURE-AccountAdd.md)
  intent: A name that is empty, longer than 40 characters, or holds a comma or newline is rejected with exit 3 and not stored.
  return code: 1
  stdout:
    ADDBN1  error: unknown command: account add ADDBN1
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-add-invalid-name.py", line 9, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- GREEN (prepassed): account-add-usage (FEATURE-AccountAdd.md)
  intent: Missing or extra arguments to account add are a usage error (exit 2) and store nothing.
  return code: 0
  stdout:
    error: unknown command: account add ADDUSE1
    
     error: unknown command: account add ADDUSE1 Name extra
    
     error: unknown command: account add
- RED: account-duplicate-rejected (FEATURE-AccountDuplicate.md)
  intent: Adding an existing account code exits 3, prints nothing, and keeps the original name.
  return code: 1
  stdout:
    error: unknown command: account add ADUPR1 Different Name
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-duplicate-rejected.py", line 11, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- RED: account-duplicate-same-name (FEATURE-AccountDuplicate.md)
  intent: Re-adding an existing account with the identical name is still rejected with exit 3.
  return code: 1
  stdout:
    error: unknown command: account add ADUPS1 Same Name
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-duplicate-same-name.py", line 9, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: account-duplicate-then-recover (FEATURE-AccountDuplicate.md)
  intent: After a duplicate rejection, adding a different code succeeds and adds exactly one row.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-duplicate-then-recover.py", line 9, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- RED: account-get-empty (FEATURE-AccountGet.md)
  intent: Getting an account with no transactions prints its row with a zero count and a zero balance.
  return code: 1
  stdout:
    error: unknown command: account get AGETE1
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-get-empty.py", line 13, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: account-get-balance (FEATURE-AccountGet.md)
  intent: Getting an account computes its transaction count and balance from stored integer cents.
  return code: 1
  stdout:
    error: unknown command: account get AGETB1
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-get-balance.py", line 22, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: account-get-negative-format (FEATURE-AccountGet.md)
  intent: A balance is never printed negative because the ledger forbids it, and a positive one has no thousands separator.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-get-negative-format.py", line 19, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: account-get-absent (FEATURE-AccountGet.md)
  intent: Getting an absent account exits 4 and writes nothing to stdout.
  return code: 1
  stdout:
    error: unknown command: account get AGETNO1
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-get-absent.py", line 9, in <module>
        assert rc == 4
               ^^^^^^^
    AssertionError
- GREEN (prepassed): account-get-usage (FEATURE-AccountGet.md)
  intent: Getting an account with a wrong argument count exits 2 and writes nothing to stdout.
  return code: 0
- RED: account-rename-success (FEATURE-AccountRename.md)
  intent: Renaming an account prints the updated row and the new name reads back from storage.
  return code: 1
  stdout:
    error: unknown command: account rename ARENA1 New Name
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-rename-success.py", line 14, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: account-rename-keeps-transactions (FEATURE-AccountRename.md)
  intent: Renaming leaves the account's transactions and balance untouched.
  return code: 1
  stdout:
    error: unknown command: account rename ARENT1 After
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-rename-keeps-transactions.py", line 19, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: account-rename-absent (FEATURE-AccountRename.md)
  intent: Renaming an absent account exits 4 and creates nothing.
  return code: 1
  stdout:
    error: unknown command: account rename ARENN1 Whatever
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-rename-absent.py", line 9, in <module>
        assert rc == 4
               ^^^^^^^
    AssertionError
- RED: account-rename-invalid-name (FEATURE-AccountRename.md)
  intent: A name that is too long, empty, or contains a comma is rejected with exit 3 and the stored name is unchanged.
  return code: 1
  stdout:
    error: unknown command: account rename ARENI1 NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-rename-invalid-name.py", line 12, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- GREEN (prepassed): account-rename-usage (FEATURE-AccountRename.md)
  intent: Renaming with a wrong argument count exits 2 and writes nothing to stdout.
  return code: 0
- RED: load-categories-valid (FEATURE-LoadCategories.md)
  intent: A valid categories file loads, reports the loaded count, and every row reads back.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-categories-valid.py", line 20, in <module>
        before = counts()
                 ^^^^^^^^
      File "load-categories-valid.py", line 10, in counts
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: load-categories-header (FEATURE-LoadCategories.md)
  intent: A file whose header does not match the table columns is rejected with exit 3 and stores nothing.
  return code: 1
  stdout:
    error: unknown command: load categories /tmp/tmpu5md4j8_/categories.csv
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-categories-header.py", line 17, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- RED: load-categories-atomic (FEATURE-LoadCategories.md)
  intent: An invalid row rejects the whole file so no earlier row is stored.
  return code: 1
  stdout:
    error: unknown command: load categories /tmp/tmpskuw9u2j/categories.csv
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-categories-atomic.py", line 19, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- RED: load-categories-duplicates (FEATURE-LoadCategories.md)
  intent: A code repeated inside the file, or already stored, is rejected with exit 3 and nothing is added.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-categories-duplicates.py", line 21, in <module>
        before = counts()
                 ^^^^^^^^
      File "load-categories-duplicates.py", line 9, in counts
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: load-categories-usage-and-io (FEATURE-LoadCategories.md)
  intent: A missing argument is a usage error (exit 2) and an unreadable file is an operational failure (exit 1).
  return code: 1
  stdout:
    error: unknown command: load categories
    
     error: unknown command: load categories /tmp/tmpyy93_2u1/absent.csv
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-categories-usage-and-io.py", line 14, in <module>
        assert rc == 1
               ^^^^^^^
    AssertionError
- RED: load-accounts-valid (FEATURE-LoadAccounts.md)
  intent: A valid accounts file loads, reports the loaded count, and every row reads back.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-accounts-valid.py", line 20, in <module>
        before = counts()
                 ^^^^^^^^
      File "load-accounts-valid.py", line 10, in counts
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: load-accounts-header (FEATURE-LoadAccounts.md)
  intent: A file whose header does not match the table columns is rejected with exit 3 and stores nothing.
  return code: 1
  stdout:
    error: unknown command: load accounts /tmp/tmpyziexbiv/accounts.csv
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-accounts-header.py", line 18, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- RED: load-accounts-atomic (FEATURE-LoadAccounts.md)
  intent: An invalid row rejects the whole file so no earlier row is stored.
  return code: 1
  stdout:
    error: unknown command: load accounts /tmp/tmpvz9gzf6m/accounts.csv
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-accounts-atomic.py", line 19, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- RED: load-accounts-duplicates (FEATURE-LoadAccounts.md)
  intent: A code repeated inside the file, or already stored, is rejected with exit 3 and nothing is added.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-accounts-duplicates.py", line 21, in <module>
        before = counts()
                 ^^^^^^^^
      File "load-accounts-duplicates.py", line 9, in counts
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: load-accounts-usage-and-io (FEATURE-LoadAccounts.md)
  intent: A missing argument is a usage error (exit 2) and an unreadable file is an operational failure (exit 1).
  return code: 1
  stdout:
    error: unknown command: load accounts
    
     error: unknown command: load accounts /tmp/tmprls_in7k/absent.csv
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-accounts-usage-and-io.py", line 14, in <module>
        assert rc == 1
               ^^^^^^^
    AssertionError
- RED: txn-post-success (FEATURE-TxnPost.md)
  intent: Posting a transaction prints its row with the next id and stores integer cents that read back.
  return code: 1
  stdout:
    error: unknown command: txn post TPOSS1 TPOSSC1 45.50 2026-04-01 walk in sale
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-post-success.py", line 18, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: txn-post-id-increments (FEATURE-TxnPost.md)
  intent: Two successive posts receive consecutive transaction ids.
  return code: 1
  stdout:
    error: unknown command: txn post TPOSI1 TPOSIC1 10.00 2026-04-01 one
    
    error: unknown command: txn post TPOSI1 TPOSIC1 20.00 2026-04-01 two
  stderr:
    --- drydock: values at failure ---
      rc1 = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-post-id-increments.py", line 16, in <module>
        assert rc1 == 0
               ^^^^^^^^
    AssertionError
- RED: txn-post-no-memo (FEATURE-TxnPost.md)
  intent: A post without a memo stores and prints an empty memo.
  return code: 1
  stdout:
    error: unknown command: txn post TPOSN1 TPOSNC1 3.00 2026-04-02
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-post-no-memo.py", line 14, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: txn-post-negative-with-funds (FEATURE-TxnPost.md)
  intent: A negative post is accepted when the account balance stays at or above zero and is stored as negative cents.
  return code: 1
  stdout:
    error: unknown command: txn post TPOSG1 TPOSGC1 -12.34 2026-04-02 tape
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-post-negative-with-funds.py", line 20, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: txn-post-reject-overdraw (FEATURE-TxnPost.md)
  intent: A post that would leave the account balance below zero exits 3 and stores nothing.
  return code: 1
  stdout:
    error: unknown command: txn post TPOSO1 TPOSOC1 -10.01 2026-04-02
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-post-reject-overdraw.py", line 17, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- RED: txn-post-reject-unknown-account (FEATURE-TxnPost.md)
  intent: A post to an unknown account exits 3 and stores nothing.
  return code: 1
  stdout:
    error: unknown command: txn post TPOSU1 TPOSU1C 1.00 2026-04-01
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-post-reject-unknown-account.py", line 12, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- RED: txn-post-reject-unknown-category (FEATURE-TxnPost.md)
  intent: A post to an unknown category exits 3 and stores nothing.
  return code: 1
  stdout:
    error: unknown command: txn post TPOSK1 TPOSKC1 1.00 2026-04-01
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-post-reject-unknown-category.py", line 12, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- RED: txn-post-reject-zero-amount (FEATURE-TxnPost.md)
  intent: A zero amount in any spelling exits 3 and stores nothing.
  return code: 1
  stdout:
    error: unknown command: txn post TPOSZ1 TPOSZC1 0 2026-04-01
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-post-reject-zero-amount.py", line 13, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- RED: txn-post-reject-bad-memo (FEATURE-TxnPost.md)
  intent: A memo longer than 60 characters or containing a comma exits 3 and stores nothing.
  return code: 1
  stdout:
    error: unknown command: txn post TPOSM1 TPOSMC1 1.00 2026-04-01 mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txn-post-reject-bad-memo.py", line 14, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- GREEN (prepassed): txn-post-usage (FEATURE-TxnPost.md)
  intent: A post with too few or too many arguments exits 2 and writes nothing to stdout.
  return code: 0
- RED: txnget-present (FEATURE-TxnGet.md)
  intent: txn get prints the header and the stored row with a two-decimal amount.
  return code: 1
  stdout:
    error: unknown command: txn get 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txnget-present.py", line 18, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: txnget-negative-empty-memo (FEATURE-TxnGet.md)
  intent: A negative amount prints with a leading minus and an empty memo prints as an empty field.
  return code: 1
  stdout:
    error: unknown command: txn get 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txnget-negative-empty-memo.py", line 18, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: txnget-absent (FEATURE-TxnGet.md)
  intent: txn get of an absent id exits 4 with nothing on standard output.
  return code: 1
  stdout:
    error: unknown command: txn get 1000
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txnget-absent.py", line 9, in <module>
        assert code == 4
               ^^^^^^^^^
    AssertionError
- GREEN (prepassed): txnget-usage (FEATURE-TxnGet.md)
  intent: Wrong argument counts and a non-integer id are usage errors with exit 2 and no output.
  return code: 0
  stdout:
    ('txn', 'get') 2  error: unknown command: txn get
    
    ('txn', 'get', '1', '2') 2  error: unknown command: txn get 1 2
    
    ('txn', 'get', 'abc') 2  error: unknown command: txn get abc
- RED: txnget-read-only (FEATURE-TxnGet.md)
  intent: txn get leaves the stored row and the table size unchanged.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txnget-read-only.py", line 14, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: txnvalidate-unknown-category (FEATURE-TxnValidate.md)
  intent: An unknown category exits 3 and writes no row.
  return code: 1
  stdout:
    error: unknown command: txn post TVACCT1 NOSUCHCAT 1.00 2026-04-01
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txnvalidate-unknown-category.py", line 11, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: txnvalidate-bad-amounts (FEATURE-TxnValidate.md)
  intent: Over-precise, malformed, and zero amounts exit 3 and write no row.
  return code: 1
  stdout:
    '1.234' 2  error: unknown command: txn post TVACCT2 TVCAT2 1.234 2026-04-01
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txnvalidate-bad-amounts.py", line 13, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: txnvalidate-bad-dates (FEATURE-TxnValidate.md)
  intent: Impossible and malformed dates exit 3 and write no row.
  return code: 1
  stdout:
    '2026-02-30' 2  error: unknown command: txn post TVACCT3 TVCAT3 1.00 2026-02-30
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txnvalidate-bad-dates.py", line 13, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: txnvalidate-valid-boundaries (FEATURE-TxnValidate.md)
  intent: A one-decimal amount and a leap-day date are accepted and stored as integer cents.
  return code: 1
  stdout:
    error: unknown command: txn post TVACCT4 TVCAT4 12.5 2028-02-29
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txnvalidate-valid-boundaries.py", line 14, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: txnvalidate-no-id-gap (FEATURE-TxnValidate.md)
  intent: A rejected post consumes no id, so the next successful post receives the next id.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txnvalidate-no-id-gap.py", line 11, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: txndelete-success (FEATURE-TxnDelete.md)
  intent: txn delete prints deleted and the id, and the row is gone on read back.
  return code: 1
  stdout:
    error: unknown command: txn delete 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txndelete-success.py", line 17, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: txndelete-absent (FEATURE-TxnDelete.md)
  intent: txn delete of an absent id exits 4 and removes nothing.
  return code: 1
  stdout:
    error: unknown command: txn delete 1000
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txndelete-absent.py", line 10, in <module>
        assert code == 4
               ^^^^^^^^^
    AssertionError
- RED: txndelete-negative-balance (FEATURE-TxnDelete.md)
  intent: Deleting a credit that funds a later debit exits 3 and keeps both rows.
  return code: 1
  stdout:
    error: unknown command: txn delete 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txndelete-negative-balance.py", line 18, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: txndelete-debit-allowed (FEATURE-TxnDelete.md)
  intent: Deleting a debit raises the balance and is accepted.
  return code: 1
  stdout:
    error: unknown command: txn delete 2
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txndelete-debit-allowed.py", line 17, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- GREEN (prepassed): txndelete-usage (FEATURE-TxnDelete.md)
  intent: Wrong argument counts and a non-integer id are usage errors with exit 2.
  return code: 0
  stdout:
    ('txn', 'delete') 2  error: unknown command: txn delete
    
    ('txn', 'delete', '1', '2') 2  error: unknown command: txn delete 1 2
    
    ('txn', 'delete', 'abc') 2  error: unknown command: txn delete abc
- RED: txnamend-success (FEATURE-TxnAmend.md)
  intent: txn amend prints the updated row, changes only the amount, and persists it.
  return code: 1
  stdout:
    error: unknown command: txn amend 1 54.50
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txnamend-success.py", line 18, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: txnamend-absent (FEATURE-TxnAmend.md)
  intent: txn amend of an absent id exits 4 with nothing on standard output.
  return code: 1
  stdout:
    error: unknown command: txn amend 1000 5.00
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txnamend-absent.py", line 10, in <module>
        assert code == 4
               ^^^^^^^^^
    AssertionError
- RED: txnamend-negative-balance (FEATURE-TxnAmend.md)
  intent: An amendment that would leave the account balance below zero exits 3 and changes nothing.
  return code: 1
  stdout:
    error: unknown command: txn amend 2 -200.00
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txnamend-negative-balance.py", line 17, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: txnamend-boundary-zero-balance (FEATURE-TxnAmend.md)
  intent: An amendment that leaves the balance exactly zero is accepted.
  return code: 1
  stdout:
    error: unknown command: txn amend 2 -100.00
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txnamend-boundary-zero-balance.py", line 17, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: txnamend-invalid-amount (FEATURE-TxnAmend.md)
  intent: Malformed, over-precise, and zero amounts exit 3 and leave the row unchanged.
  return code: 1
  stdout:
    1.234 2  error: unknown command: txn amend 1 1.234
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "txnamend-invalid-amount.py", line 14, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- GREEN (prepassed): txnamend-usage (FEATURE-TxnAmend.md)
  intent: Wrong argument counts and a non-integer id are usage errors with exit 2.
  return code: 0
  stdout:
    ('txn', 'amend') 2  error: unknown command: txn amend
    
    ('txn', 'amend', '1') 2  error: unknown command: txn amend 1
    
    ('txn', 'amend', '1', '2.00', '3.00') 2  error: unknown command: txn amend 1 2.00 3.00
    
    ('txn', 'amend', 'abc', '2.00') 2  error: unknown command: txn amend abc 2.00
- RED: transfer-success (FEATURE-Transfer.md)
  intent: A valid transfer prints two TRANSFER rows with consecutive ids and stores both.
  return code: 1
  stdout:
    error: unknown command: transfer XFSRC1 XFDST1 25.00 2026-04-03
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfer-success.py", line 20, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: transfer-balances (FEATURE-Transfer.md)
  intent: A transfer moves exactly the amount between the two account balances.
  return code: 1
  stdout:
    error: unknown command: transfer XFSRC2 XFDST2 40.00 2026-04-03
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfer-balances.py", line 23, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: transfer-entire-balance (FEATURE-Transfer.md)
  intent: Transferring the entire source balance leaves it at zero and is accepted.
  return code: 1
  stdout:
    error: unknown command: transfer XFSRC3 XFDST3 100.00 2026-04-03
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfer-entire-balance.py", line 18, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: transfer-rejected-writes-nothing (FEATURE-Transfer.md)
  intent: Non-positive amounts, identical accounts, unknown accounts, bad dates, and malformed amounts exit 3 and write no row.
  return code: 1
  stdout:
    ('XFSRC4', 'XFDST4', '0', '2026-04-03') 2  error: unknown command: transfer XFSRC4 XFDST4 0 2026-04-03
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfer-rejected-writes-nothing.py", line 30, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: transfer-overdraw (FEATURE-Transfer.md)
  intent: A transfer larger than the source balance exits 3 and writes neither row.
  return code: 1
  stdout:
    error: unknown command: transfer XFSRC5 XFDST5 100.01 2026-04-03
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfer-overdraw.py", line 19, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- GREEN (prepassed): transfer-usage (FEATURE-Transfer.md)
  intent: Wrong argument counts are usage errors with exit 2 and no output.
  return code: 0
  stdout:
    ('transfer',) 2  error: unknown command: transfer
    
    ('transfer', 'A', 'B', '1.00') 2  error: unknown command: transfer A B 1.00
    
    ('transfer', 'A', 'B', '1.00', '2026-04-03', 'extra') 2  error: unknown command: transfer A B 1.00 2026-04-03 extra
- RED: load-transactions-valid (FEATURE-LoadTransactions.md)
  intent: A valid transactions file keeps its file ids, reports the loaded count, and every row reads back.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      tmp = '/tmp/tmpo69qomla'
      acct = 'LDTXA1'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-valid.py", line 31, in <module>
        assert load("accounts", ["account", "name"], [[acct, "Load Txn Account"]], tmp)[0] == 0
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: load-transactions-unknown-references (FEATURE-LoadTransactions.md)
  intent: An unknown account or unknown category rejects the file with exit 3 and stores nothing.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      tmp = '/tmp/tmp_0viyvny'
      acct = 'LDURA1'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-unknown-references.py", line 20, in <module>
        assert load("accounts", ["account", "name"], [[acct, "Ref Account"]], tmp)[0] == 0
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: load-transactions-invalid-fields (FEATURE-LoadTransactions.md)
  intent: A bad amount, zero amount, bad calendar date, or bad memo each reject the file with exit 3 and store nothing.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      tmp = '/tmp/tmp0dksr2ls'
      acct = 'LDIFA1'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-invalid-fields.py", line 26, in <module>
        assert load("accounts", ["account", "name"], [[acct, "Field Account"]], tmp)[0] == 0
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: load-transactions-duplicate-ids (FEATURE-LoadTransactions.md)
  intent: A txn_id repeated in the file, or already stored, rejects the file with exit 3 and adds nothing.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      tmp = '/tmp/tmp8rn5mk7z'
      acct = 'LDDIA1'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-duplicate-ids.py", line 26, in <module>
        assert load("accounts", ["account", "name"], [[acct, "Dup Account"]], tmp)[0] == 0
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: load-transactions-negative-balance (FEATURE-LoadTransactions.md)
  intent: A file that would leave an account balance below zero is rejected with exit 3 and stores nothing.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      tmp = '/tmp/tmpd34rc9qb'
      acct = 'LDNBA1'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-negative-balance.py", line 24, in <module>
        assert load("accounts", ["account", "name"], [[acct, "Balance Account"]], tmp)[0] == 0
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: load-transactions-usage-and-io (FEATURE-LoadTransactions.md)
  intent: A missing argument is a usage error (exit 2) and an unreadable file is an operational failure (exit 1).
  return code: 1
  stdout:
    error: unknown command: load transactions
    
     error: unknown command: load transactions /tmp/tmpji08n60r/absent.csv
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-transactions-usage-and-io.py", line 14, in <module>
        assert rc == 1
               ^^^^^^^
    AssertionError
- RED: account-delete-success (FEATURE-AccountDelete.md)
  intent: Deleting an account with no transactions prints deleted and the code, and the account no longer reads back.
  return code: 1
  stdout:
    error: unknown command: account delete ADELS1
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
  intent: Deleting an account that has transactions is refused with exit 3 and changes nothing.
  return code: 1
  stdout:
    error: unknown command: account delete ADELU1
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-delete-in-use.py", line 18, in <module>
        assert rc == 3
               ^^^^^^^
    AssertionError
- RED: account-delete-absent (FEATURE-AccountDelete.md)
  intent: Deleting an absent account exits 4 and writes nothing to stdout.
  return code: 1
  stdout:
    error: unknown command: account delete ADELN1
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-delete-absent.py", line 10, in <module>
        assert rc == 4
               ^^^^^^^
    AssertionError
- RED: account-delete-leaves-others (FEATURE-AccountDelete.md)
  intent: Deleting one account leaves every other account in place.
  return code: 1
  stdout:
    error: unknown command: account delete ADELO1
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "account-delete-leaves-others.py", line 12, in <module>
        assert rc == 0
               ^^^^^^^
    AssertionError
- GREEN (prepassed): account-delete-usage (FEATURE-AccountDelete.md)
  intent: Deleting with a wrong argument count exits 2 and writes nothing to stdout.
  return code: 0
- RED: transfer-overdraw-rejected (FEATURE-TransferOverdraw.md)
  intent: A transfer exceeding the source balance exits 3, prints nothing, and writes no rows.
  return code: 1
  stdout:
    error: unknown command: transfer ACPTOD1 ACPTOD2 100.01 2026-06-02
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfer-overdraw-rejected.py", line 19, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: transfer-overdraw-exact-balance (FEATURE-TransferOverdraw.md)
  intent: A transfer equal to the whole source balance succeeds and leaves the source at zero.
  return code: 1
  stdout:
    error: unknown command: transfer ACPTOE1 ACPTOE2 100.00 2026-06-02
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfer-overdraw-exact-balance.py", line 19, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: transfer-overdraw-empty-source (FEATURE-TransferOverdraw.md)
  intent: A source account with no transactions cannot be the source of any positive transfer.
  return code: 1
  stdout:
    error: unknown command: transfer ACPTOM1 ACPTOM2 0.01 2026-06-02
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfer-overdraw-empty-source.py", line 15, in <module>
        assert code == 3
               ^^^^^^^^^
    AssertionError
- RED: report-balances-rows (FEATURE-ReportBalances.md)
  intent: The report has one row per stored account in code order with counts and balances computed from stored transactions, then a consistent TOTAL row.
  return code: 1
  stdout:
    error: unknown command: report balances
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-balances-rows.py", line 24, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: report-balances-empty-account (FEATURE-ReportBalances.md)
  intent: An account with no transactions appears with a zero count and a zero balance.
  return code: 1
  stdout:
    error: unknown command: report balances
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-balances-empty-account.py", line 14, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: report-balances-reflects-changes (FEATURE-ReportBalances.md)
  intent: The report is computed from the database, so a new transaction changes the reported balance by its amount.
  return code: 1
  stdout:
    error: unknown command: report balances
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-balances-reflects-changes.py", line 23, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: report-monthly-rows (FEATURE-ReportMonthly.md)
  intent: Each month row's count, inflow, outflow, and net match the stored transactions grouped by date, ascending, followed by a consistent TOTAL row.
  return code: 1
  stdout:
    error: unknown command: report monthly
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-monthly-rows.py", line 24, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: report-monthly-skips-empty-months (FEATURE-ReportMonthly.md)
  intent: A month between two months with transactions but with none of its own does not appear.
  return code: 1
  stdout:
    error: unknown command: report monthly
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-monthly-skips-empty-months.py", line 17, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: report-monthly-reflects-changes (FEATURE-ReportMonthly.md)
  intent: The report is computed from the database, so a new transaction in a month raises that month's count by one.
  return code: 1
  stdout:
    error: unknown command: report monthly
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-monthly-reflects-changes.py", line 20, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: report-categories-rows (FEATURE-ReportCategories.md)
  intent: Each category row's count, inflow, outflow, and net match the stored transactions, in code order, followed by a consistent TOTAL row.
  return code: 1
  stdout:
    error: unknown command: report categories
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-categories-rows.py", line 24, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: report-categories-unused-category (FEATURE-ReportCategories.md)
  intent: A category with no transactions is listed with a zero count and zero amounts.
  return code: 1
  stdout:
    error: unknown command: report categories
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-categories-unused-category.py", line 14, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: report-categories-outflow-positive (FEATURE-ReportCategories.md)
  intent: A category with only withdrawals reports outflow as a positive number and a negative net with a leading minus.
  return code: 1
  stdout:
    error: unknown command: report categories
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "report-categories-outflow-positive.py", line 21, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: load-rejection-eleventh-row (FEATURE-LoadRejection.md)
  intent: Ten valid rows followed by an unknown-account row are rejected with exit 3 and none of the eleven is stored.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      tmp = '/tmp/tmpo6ev3o9o'
      acct = 'LDRJA1'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-rejection-eleventh-row.py", line 28, in <module>
        assert load("accounts", ["account", "name"], [[acct, "Reject Account"]], tmp)[0] == 0
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: load-rejection-staged-bad-file (FEATURE-LoadRejection.md)
  intent: The supplied bad transactions file is rejected with exit 3 and no table row count changes.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      rc = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-rejection-staged-bad-file.py", line 13, in <module>
        before = counts()
                 ^^^^^^^^
      File "load-rejection-staged-bad-file.py", line 8, in counts
        assert rc == 0
               ^^^^^^^
    AssertionError
- RED: load-rejection-late-invalid-fields (FEATURE-LoadRejection.md)
  intent: An invalid amount, invalid date, or duplicate id on a late row stores none of the earlier valid rows.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      tmp = '/tmp/tmpbddq8b79'
      acct = 'LDRLA1'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-rejection-late-invalid-fields.py", line 35, in <module>
        assert load("accounts", ["account", "name"], [[acct, "Late Account"]], tmp)[0] == 0
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: load-rejection-reload-existing (FEATURE-LoadRejection.md)
  intent: Reloading accounts or categories that already exist is rejected with exit 3 and changes no table.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      accounts = '/tmp/tmpscknqj7c/accounts.csv'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "load-rejection-reload-existing.py", line 23, in <module>
        assert cli_runner("load", "accounts", accounts)[0] == 0
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError

## Post-build programmatic acceptance
- PASS: init-empties-tables (FEATURE-Init.md)
  intent: ledger init exits 0, prints nothing, and leaves all three tables empty even when transactions reference accounts and categories.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: init-repeatable (FEATURE-Init.md)
  intent: Running ledger init twice in a row succeeds both times.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: init-usage-error (FEATURE-Init.md)
  intent: ledger init with an extra argument is exit 2 and removes nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: count-reports-tables (FEATURE-Count.md)
  intent: ledger count lists the three tables in order with counts that grow by the rows the criterion adds.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    table,rows
    accounts,2
    categories,1
    transactions,3
- PASS: count-after-init (FEATURE-Count.md)
  intent: ledger count reports zero rows in every table after ledger init.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: count-usage-error (FEATURE-Count.md)
  intent: ledger count with an extra argument is exit 2 with nothing on standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-add-valid (FEATURE-AccountAdd.md)
  intent: Adding a valid account prints its zero-balance row and the account reads back with the supplied name.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    ADDOK1,Added Account,0,0.00
- PASS: account-add-boundaries (FEATURE-AccountAdd.md)
  intent: A 12-character code and a 40-character name are accepted.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    ADDMAXCODE12,NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN,0,0.00
- PASS: account-add-invalid-code (FEATURE-AccountAdd.md)
  intent: A code that is too long, lowercase, or contains a forbidden character is rejected with exit 3 and not stored.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ADDBADCODE123X  error: code must be 1 to 12 characters of A-Z or 0-9: 'ADDBADCODE123X'
    
    addlower  error: code must be 1 to 12 characters of A-Z or 0-9: 'addlower'
    
    ADD-DASH  error: code must be 1 to 12 characters of A-Z or 0-9: 'ADD-DASH'
    
    ADD SPACE  error: code must be 1 to 12 characters of A-Z or 0-9: 'ADD SPACE'
- PASS: account-add-invalid-name (FEATURE-AccountAdd.md)
  intent: A name that is empty, longer than 40 characters, or holds a comma or newline is rejected with exit 3 and not stored.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ADDBN1  error: text must be 1 to 40 characters: ''
    
    ADDBN2  error: text must be 1 to 40 characters: 'NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN'
    
    ADDBN3  error: text must not contain a comma or line break
    
    ADDBN4  error: text must not contain a comma or line break
- PASS: account-add-usage (FEATURE-AccountAdd.md)
  intent: Missing or extra arguments to account add are a usage error (exit 2) and store nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account add: expects 2 argument(s)
    
     error: account add: expects 2 argument(s)
    
     error: account add: expects 2 argument(s)
- PASS: account-duplicate-rejected (FEATURE-AccountDuplicate.md)
  intent: Adding an existing account code exits 3, prints nothing, and keeps the original name.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account ADUPR1 already exists
- PASS: account-duplicate-same-name (FEATURE-AccountDuplicate.md)
  intent: Re-adding an existing account with the identical name is still rejected with exit 3.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account ADUPS1 already exists
- PASS: account-duplicate-then-recover (FEATURE-AccountDuplicate.md)
  intent: After a duplicate rejection, adding a different code succeeds and adds exactly one row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-get-empty (FEATURE-AccountGet.md)
  intent: Getting an account with no transactions prints its row with a zero count and a zero balance.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    AGETE1,Get Empty,0,0.00
- PASS: account-get-balance (FEATURE-AccountGet.md)
  intent: Getting an account computes its transaction count and balance from stored integer cents.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    AGETB1,Get Balance,2,37.66
- PASS: account-get-negative-format (FEATURE-AccountGet.md)
  intent: A balance is never printed negative because the ledger forbids it, and a positive one has no thousands separator.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    AGETF1,Get Format,1,1234567.89
- PASS: account-get-absent (FEATURE-AccountGet.md)
  intent: Getting an absent account exits 4 and writes nothing to stdout.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: no account AGETNO1
- PASS: account-get-usage (FEATURE-AccountGet.md)
  intent: Getting an account with a wrong argument count exits 2 and writes nothing to stdout.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-rename-success (FEATURE-AccountRename.md)
  intent: Renaming an account prints the updated row and the new name reads back from storage.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    ARENA1,New Name,0,0.00
- PASS: account-rename-keeps-transactions (FEATURE-AccountRename.md)
  intent: Renaming leaves the account's transactions and balance untouched.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-rename-absent (FEATURE-AccountRename.md)
  intent: Renaming an absent account exits 4 and creates nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: no account ARENN1
- PASS: account-rename-invalid-name (FEATURE-AccountRename.md)
  intent: A name that is too long, empty, or contains a comma is rejected with exit 3 and the stored name is unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: text must be 1 to 40 characters: 'NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN'
    
    error: text must be 1 to 40 characters: ''
    
    error: text must not contain a comma or line break
- PASS: account-rename-usage (FEATURE-AccountRename.md)
  intent: Renaming with a wrong argument count exits 2 and writes nothing to stdout.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: load-categories-valid (FEATURE-LoadCategories.md)
  intent: A valid categories file loads, reports the loaded count, and every row reads back.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    table,loaded
    categories,4
- PASS: load-categories-header (FEATURE-LoadCategories.md)
  intent: A file whose header does not match the table columns is rejected with exit 3 and stores nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: header must be category,description
- PASS: load-categories-atomic (FEATURE-LoadCategories.md)
  intent: An invalid row rejects the whole file so no earlier row is stored.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: code must be 1 to 12 characters of A-Z or 0-9: 'XXXXXXXXXXXXX'
- PASS: load-categories-duplicates (FEATURE-LoadCategories.md)
  intent: A code repeated inside the file, or already stored, is rejected with exit 3 and nothing is added.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: LDCDP1 repeats in the file
    
     error: LDCDP2 is already stored
- PASS: load-categories-usage-and-io (FEATURE-LoadCategories.md)
  intent: A missing argument is a usage error (exit 2) and an unreadable file is an operational failure (exit 1).
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: load categories: expects 1 argument(s)
    
     error: cannot read /tmp/tmpw6rxcvaq/absent.csv: [Errno 2] No such file or directory: '/tmp/tmpw6rxcvaq/absent.csv'
- PASS: load-accounts-valid (FEATURE-LoadAccounts.md)
  intent: A valid accounts file loads, reports the loaded count, and every row reads back.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    table,loaded
    accounts,3
- PASS: load-accounts-header (FEATURE-LoadAccounts.md)
  intent: A file whose header does not match the table columns is rejected with exit 3 and stores nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: header must be account,name
- PASS: load-accounts-atomic (FEATURE-LoadAccounts.md)
  intent: An invalid row rejects the whole file so no earlier row is stored.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: code must be 1 to 12 characters of A-Z or 0-9: 'bad code'
- PASS: load-accounts-duplicates (FEATURE-LoadAccounts.md)
  intent: A code repeated inside the file, or already stored, is rejected with exit 3 and nothing is added.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: LDDUP1 repeats in the file
    
     error: LDDUP2 is already stored
- PASS: load-accounts-usage-and-io (FEATURE-LoadAccounts.md)
  intent: A missing argument is a usage error (exit 2) and an unreadable file is an operational failure (exit 1).
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: load accounts: expects 1 argument(s)
    
     error: cannot read /tmp/tmp39aig4g2/absent.csv: [Errno 2] No such file or directory: '/tmp/tmp39aig4g2/absent.csv'
- PASS: txn-post-success (FEATURE-TxnPost.md)
  intent: Posting a transaction prints its row with the next id and stores integer cents that read back.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    1,2026-04-01,TPOSS1,TPOSSC1,45.50,walk in sale
- PASS: txn-post-id-increments (FEATURE-TxnPost.md)
  intent: Two successive posts receive consecutive transaction ids.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: txn-post-no-memo (FEATURE-TxnPost.md)
  intent: A post without a memo stores and prints an empty memo.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: txn-post-negative-with-funds (FEATURE-TxnPost.md)
  intent: A negative post is accepted when the account balance stays at or above zero and is stored as negative cents.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: txn-post-reject-overdraw (FEATURE-TxnPost.md)
  intent: A post that would leave the account balance below zero exits 3 and stores nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account TPOSO1 would be -0.01; balance may not go negative
- PASS: txn-post-reject-unknown-account (FEATURE-TxnPost.md)
  intent: A post to an unknown account exits 3 and stores nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: no account TPOSU1
- PASS: txn-post-reject-unknown-category (FEATURE-TxnPost.md)
  intent: A post to an unknown category exits 3 and stores nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: no category TPOSKC1
- PASS: txn-post-reject-zero-amount (FEATURE-TxnPost.md)
  intent: A zero amount in any spelling exits 3 and stores nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: amount must not be zero
    
    error: amount must not be zero
    
    error: amount must not be zero
    
    error: amount must not be zero
- PASS: txn-post-reject-bad-memo (FEATURE-TxnPost.md)
  intent: A memo longer than 60 characters or containing a comma exits 3 and stores nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: text must be 0 to 60 characters: 'mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm'
    
    error: text must not contain a comma or line break
- PASS: txn-post-usage (FEATURE-TxnPost.md)
  intent: A post with too few or too many arguments exits 2 and writes nothing to stdout.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: txnget-present (FEATURE-TxnGet.md)
  intent: txn get prints the header and the stored row with a two-decimal amount.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    1,2026-04-01,TGACCT1,TGCAT1,45.50,walk in sale
- PASS: txnget-negative-empty-memo (FEATURE-TxnGet.md)
  intent: A negative amount prints with a leading minus and an empty memo prints as an empty field.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    1,2026-04-02,TGACCT2,TGCAT2,-12.50,
- PASS: txnget-absent (FEATURE-TxnGet.md)
  intent: txn get of an absent id exits 4 with nothing on standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: no transaction 1000
- PASS: txnget-usage (FEATURE-TxnGet.md)
  intent: Wrong argument counts and a non-integer id are usage errors with exit 2 and no output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ('txn', 'get') 2  error: txn get: expects 1 argument(s)
    
    ('txn', 'get', '1', '2') 2  error: txn get: expects 1 argument(s)
    
    ('txn', 'get', 'abc') 2  error: transaction id must be an integer: 'abc'
- PASS: txnget-read-only (FEATURE-TxnGet.md)
  intent: txn get leaves the stored row and the table size unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: txnvalidate-unknown-category (FEATURE-TxnValidate.md)
  intent: An unknown category exits 3 and writes no row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: no category NOSUCHCAT
- PASS: txnvalidate-bad-amounts (FEATURE-TxnValidate.md)
  intent: Over-precise, malformed, and zero amounts exit 3 and write no row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    '1.234' 3  error: amount must look like 12.50 or -3: '1.234'
    
    'abc' 3  error: amount must look like 12.50 or -3: 'abc'
    
    '12.' 3  error: amount must look like 12.50 or -3: '12.'
    
    '+5.00' 3  error: amount must look like 12.50 or -3: '+5.00'
    
    '--1' 3  error: amount must look like 12.50 or -3: '--1'
    
    '' 3  error: amount must look like 12.50 or -3: ''
    
    '0' 3  error: amount must not be zero
    
    '0.00' 3  error: amount must not be zero
    
    '-0.00' 3  error: amount must not be zero
- PASS: txnvalidate-bad-dates (FEATURE-TxnValidate.md)
  intent: Impossible and malformed dates exit 3 and write no row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    '2026-02-30' 3  error: not a real calendar date: '2026-02-30'
    
    '2026-02-29' 3  error: not a real calendar date: '2026-02-29'
    
    '2026-13-01' 3  error: not a real calendar date: '2026-13-01'
    
    '2026-2-3' 3  error: date must look like 2026-04-01: '2026-2-3'
    
    'notadate' 3  error: date must look like 2026-04-01: 'notadate'
- PASS: txnvalidate-valid-boundaries (FEATURE-TxnValidate.md)
  intent: A one-decimal amount and a leap-day date are accepted and stored as integer cents.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    1,2028-02-29,TVACCT4,TVCAT4,12.50,
- PASS: txnvalidate-no-id-gap (FEATURE-TxnValidate.md)
  intent: A rejected post consumes no id, so the next successful post receives the next id.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    1,2026-04-01,TVACCT5,TVCAT5,1.00,
- PASS: txndelete-success (FEATURE-TxnDelete.md)
  intent: txn delete prints deleted and the id, and the row is gone on read back.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    deleted
    1
- PASS: txndelete-absent (FEATURE-TxnDelete.md)
  intent: txn delete of an absent id exits 4 and removes nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: no transaction 1000
- PASS: txndelete-negative-balance (FEATURE-TxnDelete.md)
  intent: Deleting a credit that funds a later debit exits 3 and keeps both rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account TDACCT2 would be -50.00; balance may not go negative
- PASS: txndelete-debit-allowed (FEATURE-TxnDelete.md)
  intent: Deleting a debit raises the balance and is accepted.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    deleted
    2
- PASS: txndelete-usage (FEATURE-TxnDelete.md)
  intent: Wrong argument counts and a non-integer id are usage errors with exit 2.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ('txn', 'delete') 2  error: txn delete: expects 1 argument(s)
    
    ('txn', 'delete', '1', '2') 2  error: txn delete: expects 1 argument(s)
    
    ('txn', 'delete', 'abc') 2  error: transaction id must be an integer: 'abc'
- PASS: txnamend-success (FEATURE-TxnAmend.md)
  intent: txn amend prints the updated row, changes only the amount, and persists it.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    1,2026-04-01,TAACCT1,TACAT1,54.50,walk in sale
- PASS: txnamend-absent (FEATURE-TxnAmend.md)
  intent: txn amend of an absent id exits 4 with nothing on standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: no transaction 1000
- PASS: txnamend-negative-balance (FEATURE-TxnAmend.md)
  intent: An amendment that would leave the account balance below zero exits 3 and changes nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account TAACCT2 would be -100.00; balance may not go negative
- PASS: txnamend-boundary-zero-balance (FEATURE-TxnAmend.md)
  intent: An amendment that leaves the balance exactly zero is accepted.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    2,2026-04-02,TAACCT3,TACAT3,-100.00,debit
- PASS: txnamend-invalid-amount (FEATURE-TxnAmend.md)
  intent: Malformed, over-precise, and zero amounts exit 3 and leave the row unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    1.234 3  error: amount must look like 12.50 or -3: '1.234'
    
    0 3  error: amount must not be zero
    
    0.00 3  error: amount must not be zero
    
    abc 3  error: amount must look like 12.50 or -3: 'abc'
    
    12. 3  error: amount must look like 12.50 or -3: '12.'
- PASS: txnamend-usage (FEATURE-TxnAmend.md)
  intent: Wrong argument counts and a non-integer id are usage errors with exit 2.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ('txn', 'amend') 2  error: txn amend: expects 2 argument(s)
    
    ('txn', 'amend', '1') 2  error: txn amend: expects 2 argument(s)
    
    ('txn', 'amend', '1', '2.00', '3.00') 2  error: txn amend: expects 2 argument(s)
    
    ('txn', 'amend', 'abc', '2.00') 2  error: transaction id must be an integer: 'abc'
- PASS: transfer-success (FEATURE-Transfer.md)
  intent: A valid transfer prints two TRANSFER rows with consecutive ids and stores both.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    2,2026-04-03,XFSRC1,TRANSFER,-25.00,transfer to XFDST1
    3,2026-04-03,XFDST1,TRANSFER,25.00,transfer from XFSRC1
- PASS: transfer-balances (FEATURE-Transfer.md)
  intent: A transfer moves exactly the amount between the two account balances.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    2,2026-04-03,XFSRC2,TRANSFER,-40.00,transfer to XFDST2
    3,2026-04-03,XFDST2,TRANSFER,40.00,transfer from XFSRC2
- PASS: transfer-entire-balance (FEATURE-Transfer.md)
  intent: Transferring the entire source balance leaves it at zero and is accepted.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    2,2026-04-03,XFSRC3,TRANSFER,-100.00,transfer to XFDST3
    3,2026-04-03,XFDST3,TRANSFER,100.00,transfer from XFSRC3
- PASS: transfer-rejected-writes-nothing (FEATURE-Transfer.md)
  intent: Non-positive amounts, identical accounts, unknown accounts, bad dates, and malformed amounts exit 3 and write no row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ('XFSRC4', 'XFDST4', '0', '2026-04-03') 3  error: amount must not be zero
    
    ('XFSRC4', 'XFDST4', '0.00', '2026-04-03') 3  error: amount must not be zero
    
    ('XFSRC4', 'XFDST4', '-5.00', '2026-04-03') 3  error: transfer amount must be positive
    
    ('XFSRC4', 'XFDST4', '1.234', '2026-04-03') 3  error: amount must look like 12.50 or -3: '1.234'
    
    ('XFSRC4', 'XFDST4', 'abc', '2026-04-03') 3  error: amount must look like 12.50 or -3: 'abc'
    
    ('XFSRC4', 'XFSRC4', '5.00', '2026-04-03') 3  error: transfer needs two different accounts
    
    ('XFSRC4', 'XFNONE', '5.00', '2026-04-03') 3  error: no account XFNONE
    
    ('XFNONE', 'XFDST4', '5.00', '2026-04-03') 3  error: no account XFNONE
    
    ('XFSRC4', 'XFDST4', '5.00', '2026-02-30') 3  error: not a real calendar date: '2026-02-30'
- PASS: transfer-overdraw (FEATURE-Transfer.md)
  intent: A transfer larger than the source balance exits 3 and writes neither row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account XFSRC5 would be -0.01; balance may not go negative
- PASS: transfer-usage (FEATURE-Transfer.md)
  intent: Wrong argument counts are usage errors with exit 2 and no output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ('transfer',) 2  error: transfer: expects 4 argument(s)
    
    ('transfer', 'A', 'B', '1.00') 2  error: transfer: expects 4 argument(s)
    
    ('transfer', 'A', 'B', '1.00', '2026-04-03', 'extra') 2  error: transfer: expects 4 argument(s)
- PASS: load-transactions-valid (FEATURE-LoadTransactions.md)
  intent: A valid transactions file keeps its file ids, reports the loaded count, and every row reads back.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    table,loaded
    transactions,3
- PASS: load-transactions-unknown-references (FEATURE-LoadTransactions.md)
  intent: An unknown account or unknown category rejects the file with exit 3 and stores nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: unknown account LDNOACCT
    
     error: unknown category LDNOCAT
- PASS: load-transactions-invalid-fields (FEATURE-LoadTransactions.md)
  intent: A bad amount, zero amount, bad calendar date, or bad memo each reject the file with exit 3 and store nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    1  error: amount must look like 12.50 or -3: '1.234'
    
    2  error: amount must not be zero
    
    3  error: not a real calendar date: '2026-02-30'
    
    4  error: text must be 0 to 60 characters: 'mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm'
- PASS: load-transactions-duplicate-ids (FEATURE-LoadTransactions.md)
  intent: A txn_id repeated in the file, or already stored, rejects the file with exit 3 and adds nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: 1001 repeats in the file
    
     error: 1002 is already stored
- PASS: load-transactions-negative-balance (FEATURE-LoadTransactions.md)
  intent: A file that would leave an account balance below zero is rejected with exit 3 and stores nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account LDNBA1 would be -0.01; balance may not go negative
- PASS: load-transactions-usage-and-io (FEATURE-LoadTransactions.md)
  intent: A missing argument is a usage error (exit 2) and an unreadable file is an operational failure (exit 1).
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: load transactions: expects 1 argument(s)
    
     error: cannot read /tmp/tmpbjtcqb6o/absent.csv: [Errno 2] No such file or directory: '/tmp/tmpbjtcqb6o/absent.csv'
- PASS: account-delete-success (FEATURE-AccountDelete.md)
  intent: Deleting an account with no transactions prints deleted and the code, and the account no longer reads back.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    deleted
    ADELS1
- PASS: account-delete-in-use (FEATURE-AccountDelete.md)
  intent: Deleting an account that has transactions is refused with exit 3 and changes nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account ADELU1 has transactions and cannot be deleted
- PASS: account-delete-absent (FEATURE-AccountDelete.md)
  intent: Deleting an absent account exits 4 and writes nothing to stdout.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: no account ADELN1
- PASS: account-delete-leaves-others (FEATURE-AccountDelete.md)
  intent: Deleting one account leaves every other account in place.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: account-delete-usage (FEATURE-AccountDelete.md)
  intent: Deleting with a wrong argument count exits 2 and writes nothing to stdout.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transfer-overdraw-rejected (FEATURE-TransferOverdraw.md)
  intent: A transfer exceeding the source balance exits 3, prints nothing, and writes no rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account ACPTOD1 would be -0.01; balance may not go negative
- PASS: transfer-overdraw-exact-balance (FEATURE-TransferOverdraw.md)
  intent: A transfer equal to the whole source balance succeeds and leaves the source at zero.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    txn_id,date,account,category,amount,memo
    2,2026-06-02,ACPTOE1,TRANSFER,-100.00,transfer to ACPTOE2
    3,2026-06-02,ACPTOE2,TRANSFER,100.00,transfer from ACPTOE1
- PASS: transfer-overdraw-empty-source (FEATURE-TransferOverdraw.md)
  intent: A source account with no transactions cannot be the source of any positive transfer.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: account ACPTOM1 would be -0.01; balance may not go negative
- PASS: report-balances-rows (FEATURE-ReportBalances.md)
  intent: The report has one row per stored account in code order with counts and balances computed from stored transactions, then a consistent TOTAL row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    ACPTRB1,Report One,2,87.50
    ACPTRB2,Report Two,1,5000.00
    TOTAL,,3,5087.50
- PASS: report-balances-empty-account (FEATURE-ReportBalances.md)
  intent: An account with no transactions appears with a zero count and a zero balance.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    ACPTRE1,Empty Report,0,0.00
    TOTAL,,0,0.00
- PASS: report-balances-reflects-changes (FEATURE-ReportBalances.md)
  intent: The report is computed from the database, so a new transaction changes the reported balance by its amount.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    account,name,transactions,balance
    ACPTRC1,Changing Report,0,0.00
    TOTAL,,0,0.00
    
    
    account,name,transactions,balance
    ACPTRC1,Changing Report,1,1234.56
    TOTAL,,1,1234.56
- PASS: report-monthly-rows (FEATURE-ReportMonthly.md)
  intent: Each month row's count, inflow, outflow, and net match the stored transactions grouped by date, ascending, followed by a consistent TOTAL row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    month,transactions,inflow,outflow,net
    2031-07,2,500.00,19.99,480.01
    2031-09,1,0.00,20.01,-20.01
    TOTAL,3,500.00,40.00,460.00
- PASS: report-monthly-skips-empty-months (FEATURE-ReportMonthly.md)
  intent: A month between two months with transactions but with none of its own does not appear.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    month,transactions,inflow,outflow,net
    2032-01,1,10.00,0.00,10.00
    2032-03,1,10.00,0.00,10.00
    TOTAL,2,20.00,0.00,20.00
- PASS: report-monthly-reflects-changes (FEATURE-ReportMonthly.md)
  intent: The report is computed from the database, so a new transaction in a month raises that month's count by one.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    month,transactions,inflow,outflow,net
    TOTAL,0,0.00,0.00,0.00
    
    
    month,transactions,inflow,outflow,net
    2033-05,1,7.00,0.00,7.00
    TOTAL,1,7.00,0.00,7.00
- PASS: report-categories-rows (FEATURE-ReportCategories.md)
  intent: Each category row's count, inflow, outflow, and net match the stored transactions, in code order, followed by a consistent TOTAL row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    category,description,transactions,inflow,outflow,net
    ACPTCRA,Category A,1,200.00,0.00,200.00
    ACPTCRB,Category B,2,0.00,20.00,-20.00
    TOTAL,,3,200.00,20.00,180.00
- PASS: report-categories-unused-category (FEATURE-ReportCategories.md)
  intent: A category with no transactions is listed with a zero count and zero amounts.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    category,description,transactions,inflow,outflow,net
    ACPTCRU,Unused Category,0,0.00,0.00,0.00
    TOTAL,,0,0.00,0.00,0.00
- PASS: report-categories-outflow-positive (FEATURE-ReportCategories.md)
  intent: A category with only withdrawals reports outflow as a positive number and a negative net with a leading minus.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    category,description,transactions,inflow,outflow,net
    ACPTCOF,Outflow Funding,1,90.00,0.00,90.00
    ACPTCOS,Outflow Spending,1,0.00,12.34,-12.34
    TOTAL,,2,90.00,12.34,77.66
- PASS: load-rejection-eleventh-row (FEATURE-LoadRejection.md)
  intent: Ten valid rows followed by an unknown-account row are rejected with exit 3 and none of the eleven is stored.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: unknown account LDRJNONE
- PASS: load-rejection-staged-bad-file (FEATURE-LoadRejection.md)
  intent: The supplied bad transactions file is rejected with exit 3 and no table row count changes.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: unknown account DRAWER1
- PASS: load-rejection-late-invalid-fields (FEATURE-LoadRejection.md)
  intent: An invalid amount, invalid date, or duplicate id on a late row stores none of the earlier valid rows.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    1  error: amount must look like 12.50 or -3: '1.234'
    
    2  error: not a real calendar date: '2026-02-30'
    
    3  error: 1001 repeats in the file
- PASS: load-rejection-reload-existing (FEATURE-LoadRejection.md)
  intent: Reloading accounts or categories that already exist is rejected with exit 3 and changes no table.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    accounts  error: LDRRA1 is already stored
    
    categories  error: LDRRC1 is already stored

## Build summary
The baseline is green (110 passing). The block needs 21 stories across seven command modules, plus shared helpers, so I'll write the shared helpers first, then the command modules, then my own tests.I left a meaningless placeholder class in that file. Removing it.Dispatch checks pass. Next I'll write my own test file. Each test runs against a throwaway SQLite store in `tmp_path`, so nothing touches `data/app.db`, and it reads state back through the commands rather than parsing internals.A few things in that file need correcting before I run it: one awkward assertion, an arithmetic error (100.00 − 25.50 + 10.25 is 84.75, not 85.25), and a `txn get` test that posts a debit with no funds, which the guard would correctly reject. Fixing those now.All 141 new tests pass. The `"changed on disk"` notice is from my own Python edit, so there's nothing to reconcile there.

The spec's acceptance criteria are the Definition of Done, so I'll run them too. They assume the Drydock harness, which wraps each criterion in one rolled-back transaction, so I'll emulate that with the library's own begin/end functions. The script lives in `/tmp`, outside the build directory.The runner has a bug: each criterion block starts with an `Intent:` prose line that isn't Python. I'll strip that. I also need to restrict the run to the feature files this block implements. `FEATURE-TestSuite.md` and `FEATURE-UsageErrors.md` aren't part of this block, and the suite one may invoke the staged `run.sh`, which the build instructions forbid here.All 98 blueprint criteria for this block pass. Because the criteria write through the store, I'll confirm the application database was left exactly as it was (the harness emulation should roll everything back).The store is still empty, and the `-wal`/`-shm` files are normal SQLite WAL artifacts under the gitignored `data/` directory. Now the full project suite, which is the declared test command:The full suite passes (251 tests, including the 110 pre-existing ones), and the declared `bin/test.sh` exits 0. One small cleanup: the `cli/commands/__init__.py` docstring still says the package is "intentionally empty of commands", which is no longer true.Last checks: the suite again, plus a real end-to-end run through the `./ledger` launcher against a throwaway database, which exercises the actual process path that the in-process tests don't.The block is implemented. All 98 acceptance criteria for this block pass, and the full project suite is green with 251 tests, 141 of them new.

RESULT: SUCCESS

FILES CHANGED:
- cli/views.py
- cli/commands/init.py
- cli/commands/count.py
- cli/commands/account.py
- cli/commands/load.py
- cli/commands/txn.py
- cli/commands/transfer.py
- cli/commands/report.py
- cli/commands/__init__.py (docstring only; it said the package was intentionally empty)
- tests/test_commands.py

SUMMARY:
- **Commands:** all 21 stories are implemented as `ledger` subcommands. Each module registers its handlers on import, and the shared helpers (id parsing, row shapes, the `Txn` record) live in `cli/views.py`.
- **Checks:** every validation, reference check, duplicate check, and balance-guard check runs before the first write. Rejections exit 3, not-found exits 4, usage errors exit 2, and operational failures exit 1.
- **Data:** no commands hardcode a count, balance, or total. Amounts are integer cents throughout and are formatted by the shipped core helpers.
- **Acceptance criteria:** I ran all 98 criteria from the 21 FEATURE files this block implements, each in its own rolled-back transaction to emulate the Drydock harness. All 98 pass. Drydock's real harness may behave differently, but the application store was left empty afterwards.
- **Tests:** `tests/test_commands.py` covers every story, the error paths, boundaries, and the seed files. Each test runs against its own temporary SQLite store, so nothing touches `data/app.db`.
- **Project suite:** `pytest -q` gives 251 passed, and `bin/test.sh` exits 0.
- **End-to-end:** a smoke run through the `./ledger` launcher loaded the seed files and produced the expected exit codes. The grader `sources/run.sh` was not run: no criterion in this block invokes it.

BLOCKERS:
- None.

<blueprint-decisions>
[{"spec":"FEATURE-LoadTransactions.md","severity":"Material","subject":"All-or-nothing writes","decision":"The spec asks for one transaction, but the persistence package exposes no multi-statement transaction to application code, and the rules forbid driver calls. I validate every row and the balance guard before the first write, so validation failures store nothing. A database error partway through the write phase can still leave earlier rows stored. Is that acceptable, or should the persistence layer add a transaction facility?"},{"spec":"FEATURE-LoadAccounts.md","severity":"Material","subject":"All-or-nothing writes","decision":"Same limitation as load transactions: validation completes before the first write, but a mid-write database failure can leave partial rows, because there is no transaction facility to wrap the writes. Is that acceptable?"},{"spec":"FEATURE-LoadCategories.md","severity":"Material","subject":"All-or-nothing writes","decision":"Same limitation as the other loads. Categories also have no per-row delete declared, so no compensating undo is possible. Is that acceptable?"},{"spec":"FEATURE-Transfer.md","severity":"Material","subject":"Two-row atomicity","decision":"Both TRANSFER rows are checked before the first write, but the two creates are not wrapped in a transaction. A failure on the second create would leave the first stored. Is that acceptable, or should the persistence layer add a transaction facility?"},{"spec":"FEATURE-Init.md","severity":"Material","subject":"Init empties tables rather than dropping them","decision":"The story says drop and recreate, but the FEATURE Behavior says make sure the tables exist, then empty them in foreign-key order. I followed the Behavior. Tables are created from schema.sql only when a probe finds one missing, because execute_script is forbidden inside the acceptance transaction. Should init drop and recreate instead?"},{"spec":"FEATURE-LoadTransactions.md","severity":"Low","subject":"File txn_id range","decision":"The spec says a non-integer txn_id is rejected but does not give a range. I accept only positive integers up to 2147483647, the INTEGER column limit, and reject 0 and negatives. Is that acceptable?"},{"spec":"FEATURE-Transfer.md","severity":"Low","subject":"Missing TRANSFER category","decision":"If the store has no TRANSFER category, transfer exits 1 as an operational failure rather than 3, since it is a store configuration problem rather than bad input. Is that acceptable?"}]
</blueprint-decisions>
