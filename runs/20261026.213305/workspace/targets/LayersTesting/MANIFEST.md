# MANIFEST: LayersTesting
updated: 2026-10-26T21:58:08+00:00
state: draft
blocks:      14

## story 1: Stand up the Python project tree, environment, test runner and application module layout.
id:           foundation
summary:      Stand up the Python project tree, environment, test runner and application module layout.
type:         foundational
kind:         capability
phase:        1
block:        1
implements:   ARCHITECTURE.md
instructions: |
  Create the Python 3.11+ project: pyproject.toml, committed uv.lock, .venv via uv, pytest as the
  runner, and the package layout described in ARCHITECTURE.md. Money is integer cents at every layer;
  no floating point. Application code never opens a database driver; all access goes through the
  generated persistence package. Record the module ownership table for persistence, configuration
  and CLI boundaries.
stack:        common.md, python.md
stack_mode:   builder
size:         7542
provides:     python project tree
acceptance:   yes
state:        pending

## story 2: Declare the accounts, categories and transactions store and every repository operation the ledger needs.
id:           database
summary:      Declare the accounts, categories and transactions store and every repository operation the ledger needs.
type:         foundational
kind:         capability
phase:        1
block:        2
implements:   DATABASE.md
instructions: |
  Declare tables accounts, categories and transactions exactly as in the source (amount INTEGER cents,
  account and category foreign keys). Declare one access pattern per repository operation the stories
  need: create/get/update/delete/list for each table, list transactions by account, count rows per
  table, delete-all per table for init, max txn_id, per-account balance and transaction count
  aggregation inputs, and monthly and category grouping inputs as lists. Report aggregation is computed
  by callers from listed rows in integer cents. The builder writes no persistence code; Drydock
  generates the package.
stack:        common.md, python.md, persistence.md, sqlite.md
stack_mode:   builder
size:         23165
provides:     persistence.open_database
depends:      foundation
acceptance:   yes
state:        pending

## story 3: Provide the executable `ledger`, the command dispatcher and database location resolution.
id: cli-foundation
summary: Provide the executable `ledger`, the command dispatcher and database location resolution.
type: foundational
kind: capability
phase: 1
block: 3
implements: FEATURE-CliFoundation.md
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: builder
size: 18118
provides: ledger, ledger.register_command, ledger_config.database_dsn
consumes: persistence.open_database
instructions: |
  Create the executable `ledger` at the application root (executable bit set) delegating to
  cli.main(argv) -> int, plus cli/testing.py with cli_runner. Provide a command registry that
  later stories register into with ledger.register_command. Resolve the database as DATABASE_URL
  (empty treated as unset), then DATABASE_PATH, then data/app.db, and open it only through
  persistence.open_database. Never print the DSN or any credential.
acceptance: yes
depends: database
state: pending

## story 4: Format integer cents and write CSV rows to standard output.
id: csv-output
summary: Format integer cents and write CSV rows to standard output.
type: service
kind: capability
phase: 1
block: 4
implements: FEATURE-CsvOutput.md
covers: CLI-002
accepts: st-011
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 17399
provides: csv_output.format_cents, csv_output.write_rows
consumes: ledger.register_command
instructions: |
  Implement integer-only cents formatting: exactly two decimals, leading `-` when negative, no
  thousands separator, zero always `0.00`, never `-0.00`. write_rows emits comma-separated rows with
  no quoting, no trailing spaces and `\n` endings.
acceptance: yes
depends: cli-foundation
state: pending

## story 5: Map rejection, not-found, operational and usage failures to exit codes and one stderr line.
id: error-contract
summary: Map rejection, not-found, operational and usage failures to exit codes and one stderr line.
type: service
kind: capability
phase: 1
block: 4
implements: FEATURE-ErrorContract.md
covers: CLI-003
accepts: st-011
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 17741
provides: ledger_errors.Rejected, ledger_errors.NotFound, ledger_errors.OperationalFailure, ledger_errors.UsageError
consumes: ledger.register_command
instructions: |
  Define the error types and the top-level handler: usage 2, rejected 3, not found 4, operational
  failure (database unreachable, tables missing, file unreadable) 1. A failure writes nothing to
  stdout and exactly one diagnostic line to stderr that never contains a DSN, path credential or
  password. Unexpected database errors map to exit 1.
acceptance: yes
depends: cli-foundation
state: pending

## story 6: Validate codes, names, memos, amounts and dates and convert amounts to integer cents.
id: validation
summary: Validate codes, names, memos, amounts and dates and convert amounts to integer cents.
type: service
kind: capability
phase: 1
block: 5
implements: FEATURE-Validation.md
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md
stack_mode: consumer
size: 15300
provides: validation.parse_amount, validation.parse_date, validation.check_code, validation.check_text
consumes: ledger_errors.Rejected
instructions: |
  Codes: 1-12 of A-Z0-9. Names and descriptions 1-40 chars, memos 0-60, none with comma or newline.
  Amounts match -?DIGITS[.D[D]] only (no leading dot, plus sign, spaces or separators), at most two
  decimals, never zero in any form (0, 0.00, -0), parsed with integer arithmetic into cents. Dates
  are real calendar dates YYYY-MM-DD with leap-year rules. Violations raise Rejected.
acceptance: yes
depends: error-contract
state: pending

## story 7: Reject unknown commands, tables, reports and wrong argument counts with exit 2 and usage on stderr.
id: cli-usage
summary: Reject unknown commands, tables, reports and wrong argument counts with exit 2 and usage on stderr.
type: service
kind: capability
phase: 1
block: 5
implements: FEATURE-CliUsage.md
covers: CLI-001
accepts: st-011
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 17435
provides: ledger usage
consumes: ledger.register_command, ledger_errors.UsageError
instructions: |
  With no arguments, or an unknown command, report or table, or the wrong argument count, write
  usage text to stderr only and exit 2. Usage names every command and sub-verb in the command table.
  Nothing is written to stdout and nothing to the database.
acceptance: yes
depends: cli-foundation, error-contract
state: pending

## story 8: Judge account balances on the final state of a command and reject any negative balance.
id: balance-rules
summary: Judge account balances on the final state of a command and reject any negative balance.
type: service
kind: capability
phase: 1
block: 5
implements: FEATURE-BalanceRules.md
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, persistence.md
stack_mode: consumer
size: 18204
provides: balance_rules.check_final_balances
consumes: persistence.open_database, ledger_errors.Rejected
instructions: |
  Given pending inserts, amount changes and deletions, compute each affected account's resulting
  balance from stored transactions plus the pending changes and raise Rejected if any is below zero,
  before any write. Judge only the final state: an intermediate dip restored later in the same
  command is allowed. Integer cents only.
acceptance: yes
depends: database, error-contract
state: pending

## story 9: Implement `ledger init` to prepare an empty ledger and remove all rows on rerun.
id: ledger-init
summary: Implement `ledger init` to prepare an empty ledger and remove all rows on rerun.
type: service
kind: capability
phase: 2
block: 6
implements: FEATURE-LedgerInit.md
covers: LEDGER-001
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md, persistence.md
stack_mode: consumer
size: 19977
provides: ledger init
consumes: ledger.register_command, ledger_config.database_dsn, persistence.open_database, ledger_errors.OperationalFailure
instructions: |
  Delete all transactions, then categories, then accounts in one database transaction. Write nothing
  to stdout. Unreachable database exits 1 without leaking the DSN. Cover the DATABASE_URL/DATABASE_PATH/
  default resolution order including an empty DATABASE_URL.
acceptance: yes
depends: cli-foundation, error-contract, database
state: pending

## story 10: Implement `ledger count` reporting stored row counts.
id: ledger-count
summary: Implement `ledger count` reporting stored row counts.
type: service
kind: capability
phase: 2
block: 7
implements: FEATURE-LedgerCount.md
covers: LEDGER-002
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md, persistence.md
stack_mode: consumer
size: 20003
provides: ledger count
consumes: ledger.register_command, persistence.open_database, csv_output.write_rows
instructions: |
  Write `table,rows` then accounts, categories, transactions rows in that order, counted from the
  database.
acceptance: yes
depends: ledger-init, csv-output
state: pending

## story 11: Implement `ledger load categories <csv>` all-or-nothing.
id: load-categories
summary: Implement `ledger load categories <csv>` all-or-nothing.
type: service
kind: capability
phase: 2
block: 7
implements: FEATURE-LoadCategories.md
covers: LOAD-002
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md, persistence.md
stack_mode: consumer
size: 21288
provides: ledger load categories
consumes: ledger.register_command, persistence.open_database, validation.check_code, validation.check_text, csv_output.write_rows, ledger_errors.Rejected, ledger_errors.OperationalFailure
instructions: |
  Same contract as accounts with header `category,description`. Write `table,loaded` and
  `categories,<rows>`.
acceptance: yes
depends: ledger-init, validation, csv-output, error-contract
state: pending

## story 12: Implement `ledger load accounts <csv>` all-or-nothing.
id: load-accounts
summary: Implement `ledger load accounts <csv>` all-or-nothing.
type: service
kind: capability
phase: 2
block: 7
implements: FEATURE-LoadAccounts.md
covers: LOAD-001
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md, persistence.md
stack_mode: consumer
size: 21850
provides: ledger load accounts
consumes: ledger.register_command, persistence.open_database, validation.check_code, validation.check_text, csv_output.write_rows, ledger_errors.Rejected, ledger_errors.OperationalFailure
instructions: |
  Parse the whole file first. A header differing from `account,name` in names or order exits 3
  before any write. Validate every row and duplicate keys (within the file and against stored rows);
  any failure rejects the file with exit 3 and stores nothing. Unreadable file exits 1. Write
  `table,loaded` and `accounts,<rows>`.
acceptance: yes
depends: ledger-init, validation, csv-output, error-contract
state: pending

## story 13: Implement `ledger load transactions <csv>` with validation and the final-balance rule, all-or-nothing.
id: load-transactions
summary: Implement `ledger load transactions <csv>` with validation and the final-balance rule, all-or-nothing.
type: service
kind: capability
phase: 2
block: 8
implements: FEATURE-LoadTransactions.md
covers: LOAD-003
accepts: st-004, st-007, st-008
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md, persistence.md
stack_mode: consumer
size: 23932
provides: ledger load transactions
consumes: ledger.register_command, persistence.open_database, validation.parse_amount, validation.parse_date, validation.check_code, validation.check_text, balance_rules.check_final_balances, csv_output.write_rows, ledger_errors.Rejected
instructions: |
  Header `txn_id,date,account,category,amount,memo`. Keep each file txn_id. Reject with exit 3 and no
  writes any bad row, duplicate txn_id, unknown account or category, or negative final account balance
  (judged after the whole file). A header-only file loads zero rows and writes `transactions,0`. Write
  `table,loaded` and `transactions,<rows>`. Validation, balance check and insert occur in one
  database transaction.
acceptance: yes
depends: load-accounts, load-categories, validation, balance-rules, csv-output
state: pending

## story 14: Implement `ledger account add <code> <name>`.
id: account-add
summary: Implement `ledger account add <code> <name>`.
type: service
kind: capability
phase: 3
block: 9
implements: FEATURE-AccountAdd.md
covers: ACCT-001
accepts: st-006
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md, persistence.md
stack_mode: consumer
size: 20484
provides: ledger account add
consumes: ledger.register_command, persistence.open_database, validation.check_code, validation.check_text, csv_output.write_rows, ledger_errors.Rejected
instructions: |
  Store a new account and print `account,name,transactions,balance` with the new row (0, 0.00).
  Duplicate code exits 3; names may repeat across accounts.
acceptance: yes
depends: ledger-init, validation, csv-output, error-contract
state: pending

## story 15: Implement `ledger account get <code>`.
id: account-get
summary: Implement `ledger account get <code>`.
type: service
kind: capability
phase: 3
block: 10
implements: FEATURE-AccountGet.md
covers: ACCT-002
accepts: st-006
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md, persistence.md
stack_mode: consumer
size: 20475
provides: ledger account get
consumes: ledger.register_command, persistence.open_database, csv_output.write_rows, ledger_errors.NotFound
instructions: |
  Print the account row with transaction count and balance computed from stored transactions. Absent
  code exits 4.
acceptance: yes
depends: account-add
state: pending

## story 16: Implement `ledger account rename <code> <name>`.
id: account-rename
summary: Implement `ledger account rename <code> <name>`.
type: service
kind: capability
phase: 3
block: 10
implements: FEATURE-AccountRename.md
covers: ACCT-003
accepts: st-006
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md, persistence.md
stack_mode: consumer
size: 20504
provides: ledger account rename
consumes: ledger.register_command, persistence.open_database, validation.check_text, csv_output.write_rows, ledger_errors.NotFound, ledger_errors.Rejected
instructions: |
  Change only the name and print the updated row. Renaming to the current name succeeds. Absent code
  exits 4; invalid name exits 3.
acceptance: yes
depends: account-add
state: pending

## story 17: Implement `ledger txn post` with id assignment and the balance rule.
id: txn-post
summary: Implement `ledger txn post` with id assignment and the balance rule.
type: service
kind: capability
phase: 3
block: 10
implements: FEATURE-TxnPost.md
covers: TXN-001
accepts: st-006, st-007, st-008
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md, persistence.md
stack_mode: consumer
size: 22691
provides: ledger txn post
consumes: ledger.register_command, persistence.open_database, validation.parse_amount, validation.parse_date, validation.check_code, validation.check_text, balance_rules.check_final_balances, csv_output.write_rows, ledger_errors.Rejected
instructions: |
  Args: account category amount date [memo]. Validate everything and the balance rule before writing;
  unknown account or category exits 3. Assign txn_id as max+1 (1 when empty), computing the id and
  inserting the row in one database transaction. Missing memo stores empty memo. Print the new row.
acceptance: yes
depends: account-add, load-categories, validation, balance-rules, csv-output
state: pending

## story 18: Implement `ledger account delete <code>` with in-use refusal.
id: account-delete
summary: Implement `ledger account delete <code>` with in-use refusal.
type: service
kind: capability
phase: 3
block: 11
implements: FEATURE-AccountDelete.md
covers: ACCT-004
accepts: st-006, st-007
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md, persistence.md
stack_mode: consumer
size: 20470
provides: ledger account delete
consumes: ledger.register_command, persistence.open_database, csv_output.write_rows, ledger_errors.NotFound, ledger_errors.Rejected, ledger txn post
instructions: |
  Delete an account with no transactions and print `deleted` and the code. An account with
  transactions exits 3 and changes nothing. Absent code exits 4.
acceptance: yes
depends: account-get, txn-post
state: pending

## story 19: Implement `ledger txn get <id>`.
id: txn-get
summary: Implement `ledger txn get <id>`.
type: service
kind: capability
phase: 3
block: 11
implements: FEATURE-TxnGet.md
covers: TXN-002
accepts: st-006
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md, persistence.md
stack_mode: consumer
size: 20307
provides: ledger txn get
consumes: ledger.register_command, persistence.open_database, csv_output.write_rows, ledger_errors.NotFound
instructions: Print the stored transaction row; absent or non-existent id exits 4; a non-integer id exits 3.
acceptance: yes
depends: txn-post
state: pending

## story 20: Implement `ledger txn delete <id>`.
id: txn-delete
summary: Implement `ledger txn delete <id>`.
type: service
kind: capability
phase: 3
block: 11
implements: FEATURE-TxnDelete.md
covers: TXN-004
accepts: st-006, st-007, st-008
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md, persistence.md
stack_mode: consumer
size: 20905
provides: ledger txn delete
consumes: ledger.register_command, persistence.open_database, balance_rules.check_final_balances, csv_output.write_rows, ledger_errors.NotFound, ledger_errors.Rejected
instructions: Remove the row only when no balance would go negative; print `deleted` and the id. Absent id exits 4.
acceptance: yes
depends: txn-post
state: pending

## story 21: Implement `ledger txn amend <id> <amount>`.
id: txn-amend
summary: Implement `ledger txn amend <id> <amount>`.
type: service
kind: capability
phase: 3
block: 11
implements: FEATURE-TxnAmend.md
covers: TXN-003
accepts: st-006, st-007, st-008
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md, persistence.md
stack_mode: consumer
size: 21219
provides: ledger txn amend
consumes: ledger.register_command, persistence.open_database, validation.parse_amount, balance_rules.check_final_balances, csv_output.write_rows, ledger_errors.NotFound, ledger_errors.Rejected
instructions: |
  Change only the amount; reject any resulting negative balance with exit 3 and no change. Print the
  updated row. Absent id exits 4.
acceptance: yes
depends: txn-post
state: pending

## story 22: Implement `ledger transfer` writing paired TRANSFER rows atomically.
id: transfer
summary: Implement `ledger transfer` writing paired TRANSFER rows atomically.
type: service
kind: capability
phase: 3
block: 11
implements: FEATURE-Transfer.md
covers: XFER-001
accepts: st-007, st-008, st-010
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md, persistence.md
stack_mode: consumer
size: 21854
provides: ledger transfer
consumes: ledger.register_command, persistence.open_database, validation.parse_amount, validation.parse_date, balance_rules.check_final_balances, csv_output.write_rows, ledger_errors.Rejected
instructions: |
  Args: from to amount date. Accounts must differ and amount must be positive. Write `-amount` on
  from with memo `transfer to <to>` using the next id, then `+amount` on to with memo
  `transfer from <from>` using the following id, category TRANSFER (must exist or exit 3). Balance
  checks and both inserts run in one database transaction; both rows or neither. Print both rows.
acceptance: yes
depends: txn-post
state: pending

## story 23: Implement `ledger report balances`.
id: report-balances
summary: Implement `ledger report balances`.
type: service
kind: capability
phase: 4
block: 12
implements: FEATURE-ReportBalances.md
covers: RPT-001
accepts: st-005
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md, persistence.md
stack_mode: consumer
size: 20770
provides: ledger report balances
consumes: ledger.register_command, persistence.open_database, csv_output.write_rows, csv_output.format_cents
instructions: |
  Header `account,name,transactions,balance`, one row per account ordered by code in byte order, then
  `TOTAL,,<count>,<sum>`. Computed from stored data in integer cents. Empty ledger writes header and
  `TOTAL,,0,0.00`.
acceptance: yes
depends: load-transactions, transfer, csv-output
state: pending

## story 24: Implement `ledger report monthly`.
id: report-monthly
summary: Implement `ledger report monthly`.
type: service
kind: capability
phase: 4
block: 12
implements: FEATURE-ReportMonthly.md
covers: RPT-003
accepts: st-005
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md, persistence.md
stack_mode: consumer
size: 20647
provides: ledger report monthly
consumes: ledger.register_command, persistence.open_database, csv_output.write_rows, csv_output.format_cents
instructions: |
  Header `month,transactions,inflow,outflow,net`, one row per YYYY-MM with transactions ascending,
  then `TOTAL,<count>,<inflow>,<outflow>,<net>`. Empty ledger writes header and
  `TOTAL,0,0.00,0.00,0.00`.
acceptance: yes
depends: load-transactions, transfer, csv-output
state: pending

## story 25: Implement `ledger report categories`.
id: report-categories
summary: Implement `ledger report categories`.
type: service
kind: capability
phase: 4
block: 12
implements: FEATURE-ReportCategories.md
covers: RPT-002
accepts: st-005
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md, persistence.md
stack_mode: consumer
size: 20957
provides: ledger report categories
consumes: ledger.register_command, persistence.open_database, csv_output.write_rows, csv_output.format_cents
instructions: |
  Header `category,description,transactions,inflow,outflow,net`, every category ordered by code
  including unused ones, then the TOTAL row `TOTAL,,<count>,<inflow>,<outflow>,<net>`. inflow sums
  positive amounts, outflow sums absolute negatives, net = inflow - outflow.
acceptance: yes
depends: load-transactions, transfer, csv-output
state: pending

## story 26: Provide POSIX bin/test.sh running the application's own pytest suite against temporary databases.
id: test-suite
summary: Provide POSIX bin/test.sh running the application's own pytest suite against temporary databases.
type: service
kind: test harness
phase: 5
block: 13
implements: FEATURE-TestSuite.md
covers: TEST-001
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md
stack_mode: consumer
size: 16010
provides: bin/test.sh
consumes: ledger
instructions: |
  Create bin/test.sh (POSIX sh) that activates .venv and runs pytest from the application root,
  exiting zero only when all tests pass. Tests cover each command, each exit code and each rule
  against a real temporary database that each test creates and removes; none touches data/app.db.
  Tests read seed files only through `ledger load`, never from application code.
acceptance: yes
depends: cli-usage, ledger-init, ledger-count, load-transactions, account-delete, account-rename, txn-get, txn-amend, txn-delete, transfer, report-balances, report-categories, report-monthly
state: pending

## story 27: Run the supplied grader unfiltered as the terminal release gate.
id:           verification
summary:      Run the supplied grader unfiltered as the terminal release gate.
type:         feature
kind:         integration
phase:        5
block:        14
implements:   VERIFICATION.md
covers:       VERIFY-001
accepts:      st-001
instructions: |
  Assembly and intent only. Run `sh sources/run.sh` from the application root with Suite: full and
  require exit 0. Also run `sh bin/test.sh` and require exit 0. Do not modify anything under sources/.
stack:        common.md
stack_mode:   consumer
size:         5321
consumes:     bin/test.sh
depends:      test-suite, cli-usage, ledger-init, ledger-count, load-accounts, load-categories, load-transactions, account-add, account-get, account-rename, account-delete, txn-post, txn-get, txn-amend, txn-delete, transfer, report-balances, report-categories, report-monthly, csv-output, error-contract
acceptance:   yes
state:        pending
