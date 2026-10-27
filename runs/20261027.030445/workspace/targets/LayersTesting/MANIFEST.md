# MANIFEST: LayersTesting
updated: 2026-10-27T03:27:26+00:00
state: draft
blocks:      18

## story 1: Stand up the Python project tree, environment, pytest runner, and module layout for the ledger.
id:           foundation
summary:      Stand up the Python project tree, environment, pytest runner, and module layout for the ledger.
type:         foundational
kind:         capability
phase:        1
block:        1
implements:   ARCHITECTURE.md
instructions: |
  Create the Python 3.11+ project root: pyproject.toml, committed uv.lock, `.venv` created by `uv venv`,
  pytest configuration, a conftest.py exposing the `db_session` and `cli_runner` fixtures, and the
  `bin/` launcher directory. Define the module ownership of the architecture: persistence is reached
  only through the shipped `persistence` package, configuration lives in one config module, command
  handlers are plain functions that validate every input and rule before their first write, and
  money is handled only as integer cents (never float) at every layer.
  Write ARCHITECTURE.md with a Technology Stack section derived from TECHNOLOGY_STACK.md and a module
  ownership table. Do not read sources/run.sh or any seed file from application code.
stack:        common.md, python.md
stack_mode:   builder
size:         7388
provides:     python-foundation
acceptance:   yes
state:        pending

## story 2: Declare the accounts, categories, and transactions tables and every repository operation the ledger needs.
id:           database
summary:      Declare the accounts, categories, and transactions tables and every repository operation the ledger needs.
type:         foundational
kind:         capability
phase:        1
block:        2
implements:   DATABASE.md
instructions: |
  Author DATABASE.md with three tables: accounts (account TEXT PK, name TEXT), categories (category
  TEXT PK, description TEXT), transactions (txn_id INTEGER PK, date TEXT, account TEXT REFERENCES
  accounts, category TEXT REFERENCES categories, amount INTEGER cents, memo TEXT). Declare one access
  pattern per operation any story needs: create/get/update/delete by key, list (ordered by code or
  txn_id, filterable by account), delete-all per table (used by `init`, since no DDL runs at runtime),
  max txn_id, per-account transaction count and balance sum, and any aggregate the reports need.
  The generated persistence package is written by Drydock; this story writes no persistence code.
stack:        common.md, python.md, persistence.md, sqlite.md
stack_mode:   builder
size:         22682
provides:     accounts, categories, transactions
depends:      foundation
acceptance:   yes
state:        pending

## story 3: Resolve the database location from DATABASE_URL, DATABASE_PATH, or data/app.db and open the store.
id: config
summary: Resolve the database location from DATABASE_URL, DATABASE_PATH, or data/app.db and open the store.
type: service
kind: capability
phase: 1
block: 3
implements: FEATURE-DatabaseSelection.md
covers: CFG-001
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, sqlite.md
stack_mode: consumer
size: 19211
provides: config.database_path, config.open_store
consumes: accounts, categories, transactions
instructions: |
  Implement a config module: `database_path()` returns DATABASE_URL (stripping an optional
  `sqlite://` prefix) when set, else DATABASE_PATH, else `data/app.db`. `open_store()` opens it via
  `persistence.open_database` and raises a dedicated StoreUnavailable error when the database cannot
  be opened, which the CLI maps to exit 1 with nothing on standard output. Create the parent directory
  of the default path only if absent. Never import a database driver.
acceptance: yes
depends: foundation, database
state: pending

## story 4: Provide the `ledger` executable, the cli package entry point, command dispatch, and exit-code mapping.
id: cli-foundation
summary: Provide the `ledger` executable, the cli package entry point, command dispatch, and exit-code mapping.
type: foundational
kind: capability
phase: 1
block: 4
implements: FEATURE-LedgerCli.md
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md
stack_mode: builder
size: 20886
provides: ledger, cli.main
consumes: config.open_store
instructions: |
  Create the `cli` package per the CLI Foundation Contract: `main(argv) -> int` and `cli/testing.py`
  with `cli_runner`. Create the executable `ledger` at the application root (POSIX sh launcher that
  uses the `.venv` interpreter when present, else python3) which calls `main` and exits with its
  return value. Build a command registry that later stories register into, a shared CSV writer
  (`\n` endings, no quoting), a money formatter/parser on integer cents, and an exit-code mapping:
  success 0, StoreUnavailable or unreadable file 1, UsageError 2, Rejected 3, NotFound 4. A failing
  command writes nothing to stdout and one diagnostic line to stderr. Unknown commands exit 2.
acceptance: yes
depends: foundation, config
state: pending

## story 5: Implement `ledger init` to reset the ledger to empty.
id: ledger-init
summary: Implement `ledger init` to reset the ledger to empty.
type: service
kind: capability
phase: 2
block: 5
implements: FEATURE-LedgerInit.md
covers: LEDGER-001
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: consumer
size: 21361
provides: ledger init
consumes: ledger, accounts, categories, transactions
instructions: |
  `ledger init` removes every transaction, then every category and account, in one atomic unit, writes
  nothing to stdout, and exits 0. Rerunning it removes all records again. It applies no DDL.
acceptance: yes
depends: cli-foundation, database
state: pending

## story 6: Implement `ledger count` reporting rows per table.
id: ledger-count
summary: Implement `ledger count` reporting rows per table.
type: service
kind: capability
phase: 2
block: 5
implements: FEATURE-LedgerCount.md
covers: LEDGER-002
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: consumer
size: 21696
provides: ledger count
consumes: ledger, accounts, categories, transactions
instructions: |
  Write `table,rows` then `accounts`, `categories`, `transactions` rows in that order, counted from
  the database. When the database cannot be opened the command exits 1 with empty stdout and changes
  nothing.
acceptance: yes
depends: cli-foundation, database
state: pending

## story 7: Implement `ledger load accounts` and the shared load dispatcher and code/name validators.
id: load-accounts
summary: Implement `ledger load accounts` and the shared load dispatcher and code/name validators.
type: service
kind: capability
phase: 2
block: 5
implements: FEATURE-LoadAccounts.md
covers: LOAD-001
accepts: st-004, st-007
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: consumer
size: 23486
provides: ledger load, ledger load accounts
consumes: ledger, accounts
instructions: |
  Create the shared `load` command: argument count is exactly two (table, csv path), else usage exit 2;
  an unknown table exits 2; an unreadable file exits 1; a header that does not equal the table's
  columns in order exits 3. Provide shared validators for codes (1 to 12 of A-Z0-9) and names (1 to 40
  chars, no comma or newline). Load accounts: validate every row and duplicate keys (within the file
  and against stored rows) before the first write, then store all rows atomically or none. Success
  writes `table,loaded` and `accounts,<rows>`. A header-only file loads zero rows, writes
  `accounts,0`, and exits 0.
acceptance: yes
depends: cli-foundation, database
state: pending

## story 8: Implement `ledger load categories`.
id: load-categories
summary: Implement `ledger load categories`.
type: service
kind: capability
phase: 2
block: 6
implements: FEATURE-LoadCategories.md
covers: LOAD-002
accepts: st-004, st-007
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: consumer
size: 22471
provides: ledger load categories
consumes: ledger load, categories
instructions: |
  Register the categories handler with the shared load dispatcher. Same contract as accounts with
  category code and description (1 to 40 chars, no comma or newline) validation, duplicate-key
  rejection, all-or-nothing storage, and output `table,loaded` / `categories,<rows>`.
acceptance: yes
depends: load-accounts
state: pending

## story 9: Implement `ledger load transactions` with amount, date, reference, and balance validation.
id: load-transactions
summary: Implement `ledger load transactions` with amount, date, reference, and balance validation.
type: service
kind: capability
phase: 2
block: 7
implements: FEATURE-LoadTransactions.md
covers: LOAD-003
accepts: st-004, st-007, st-008
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: consumer
size: 25662
provides: ledger load transactions
consumes: ledger load, accounts, categories, transactions
instructions: |
  Register the transactions handler. Keep each file `txn_id`. Provide shared validators reused by later
  stories: amount parsing (`-?DIGITS[.D[D]]`, at most two decimals, never zero, to integer cents with
  no floating point), real Gregorian calendar dates (Feb 29 only in leap years), memo (0 to 60 chars,
  no comma or newline), and a balance check. Reject with exit 3, before any write, on any invalid row,
  duplicate txn_id (in file or stored), unknown account or category, or when the final balance of any
  account (stored rows plus the whole batch) would be below zero. Store all rows or none. Output
  `table,loaded` / `transactions,<rows>`. Loading the staged accounts, categories, and transactions
  seed files in order yields 4, 7, and 120 rows.
acceptance: yes
depends: load-accounts, load-categories
state: pending

## story 10: Implement `ledger account add`.
id: acct-add
summary: Implement `ledger account add`.
type: service
kind: capability
phase: 3
block: 8
implements: FEATURE-AccountAdd.md
covers: ACCT-001
accepts: st-006, st-007
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: consumer
size: 21381
provides: ledger account add
consumes: ledger, accounts, transactions
instructions: |
  Register the `account` command group with `add <code> <name>`. Validate code and name, reject a
  duplicate code with exit 3, store the row, and write the header `account,name,transactions,balance`
  and the new row with 0 transactions and balance `0.00`.
acceptance: yes
depends: load-accounts
state: pending

## story 11: Implement `ledger account get`.
id: acct-get
summary: Implement `ledger account get`.
type: service
kind: capability
phase: 3
block: 9
implements: FEATURE-AccountGet.md
covers: ACCT-002
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: consumer
size: 21583
provides: ledger account get
consumes: ledger, accounts, transactions
instructions: |
  `account get <code>` writes the account header and row with the transaction count and balance
  computed from stored transactions (two-decimal output). An absent code exits 4.
acceptance: yes
depends: acct-add
state: pending

## story 12: Implement `ledger account rename`.
id: acct-rename
summary: Implement `ledger account rename`.
type: service
kind: capability
phase: 3
block: 10
implements: FEATURE-AccountRename.md
covers: ACCT-003
accepts: st-006
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: consumer
size: 21985
provides: ledger account rename
consumes: ledger, accounts
instructions: |
  `account rename <code> <name>` changes only the name and writes the updated account row. An absent
  code exits 4 (checked first); an invalid name exits 3 and changes nothing.
acceptance: yes
depends: acct-get
state: pending

## story 13: Implement `ledger account delete`.
id: acct-delete
summary: Implement `ledger account delete`.
type: service
kind: capability
phase: 3
block: 10
implements: FEATURE-AccountDelete.md
covers: ACCT-004
accepts: st-006
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: consumer
size: 21360
provides: ledger account delete
consumes: ledger, accounts, transactions
instructions: |
  `account delete <code>` writes `deleted` and the code. An absent code exits 4; an account that has
  any transaction exits 3 and nothing is removed.
acceptance: yes
depends: acct-get
state: pending

## story 14: Implement `ledger txn post` with id assignment and the full rule set.
id: txn-post
summary: Implement `ledger txn post` with id assignment and the full rule set.
type: service
kind: capability
phase: 4
block: 11
implements: FEATURE-TxnPost.md
covers: TXN-001
accepts: st-006, st-007, st-008
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: consumer
size: 23883
provides: ledger txn post
consumes: ledger, accounts, categories, transactions
instructions: |
  Register the `txn` group with `post <account> <category> <amount> <date> [<memo>]` (memo optional,
  stored empty when omitted). Reuse the shared validators. Assign txn_id = max(txn_id)+1, or 1 when
  empty. Validate every field, account and category existence, and that the account balance stays
  non-negative, all before the write; any failure exits 3 and writes nothing. Output the transaction
  header and the new row; amounts print with exactly two decimals.
acceptance: yes
depends: load-transactions, acct-get
state: pending

## story 15: Implement `ledger txn get`.
id: txn-get
summary: Implement `ledger txn get`.
type: service
kind: capability
phase: 4
block: 12
implements: FEATURE-TxnGet.md
covers: TXN-002
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: consumer
size: 21739
provides: ledger txn get
consumes: ledger, transactions
instructions: |
  `txn get <id>` writes the header `txn_id,date,account,category,amount,memo` and the stored row. An
  absent id exits 4; a non-integer id exits 3.
acceptance: yes
depends: txn-post
state: pending

## story 16: Implement `ledger txn delete` with the balance rule.
id: txn-delete
summary: Implement `ledger txn delete` with the balance rule.
type: service
kind: capability
phase: 4
block: 12
implements: FEATURE-TxnDelete.md
covers: TXN-004
accepts: st-006, st-008
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: consumer
size: 21649
provides: ledger txn delete
consumes: ledger, transactions
instructions: |
  `txn delete <id>` writes `deleted` and the id. An absent id exits 4; a deletion that would leave the
  account balance below zero exits 3 and removes nothing.
acceptance: yes
depends: txn-post
state: pending

## story 17: Implement `ledger txn amend` with the balance rule.
id: txn-amend
summary: Implement `ledger txn amend` with the balance rule.
type: service
kind: capability
phase: 4
block: 12
implements: FEATURE-TxnAmend.md
covers: TXN-003
accepts: st-006, st-008
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: consumer
size: 22651
provides: ledger txn amend
consumes: ledger, transactions
instructions: |
  `txn amend <id> <amount>` changes only the amount and writes the updated row. An absent id exits 4
  (checked first); an invalid amount, or a result that leaves the account balance below zero, exits 3
  and changes nothing.
acceptance: yes
depends: txn-post
state: pending

## story 18: Implement `ledger transfer` as an atomic pair of transactions.
id: transfer
summary: Implement `ledger transfer` as an atomic pair of transactions.
type: service
kind: capability
phase: 5
block: 13
implements: FEATURE-Transfer.md
covers: XFER-001
accepts: st-007, st-008, st-010
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: consumer
size: 23048
provides: ledger transfer
consumes: ledger, accounts, categories, transactions
instructions: |
  `transfer <from> <to> <amount> <date>`: accounts must exist and differ, amount must be positive,
  date valid, category TRANSFER must exist, and the source balance must stay non-negative, all
  before any write; failure exits 3 and stores neither row. Store `-amount` on <from> with memo
  `transfer to <to>` using the next id, then `+amount` on <to> with memo `transfer from <from>` using
  the following id, in one atomic unit. Write the header and both rows.
acceptance: yes
depends: txn-post
state: pending

## story 19: Implement `ledger report balances`.
id: rpt-balances
summary: Implement `ledger report balances`.
type: service
kind: capability
phase: 6
block: 14
implements: FEATURE-ReportBalances.md
covers: RPT-001
accepts: st-005, st-011
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: consumer
size: 22033
provides: ledger report balances
consumes: ledger, accounts, transactions
instructions: |
  Register the `report` group with `balances`. Write `account,name,transactions,balance` per account
  ordered by code, then `TOTAL,,<count>,<sum>`, computed from stored rows in integer cents. An empty
  ledger writes the header and `TOTAL,,0,0.00`. Every value comes from a query.
acceptance: yes
depends: load-transactions
state: pending

## story 20: Implement `ledger report categories`.
id: rpt-categories
summary: Implement `ledger report categories`.
type: service
kind: capability
phase: 6
block: 15
implements: FEATURE-ReportCategories.md
covers: RPT-002
accepts: st-005, st-011
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: consumer
size: 22365
provides: ledger report categories
consumes: ledger, categories, transactions
instructions: |
  Write `category,description,transactions,inflow,outflow,net` per category ordered by code, including
  categories with no transactions, then `TOTAL,,<count>,<inflow>,<outflow>,<net>`. Inflow sums positive
  amounts, outflow sums absolute values of negatives, net = inflow - outflow. With no categories the
  output is the header and `TOTAL,,0,0.00,0.00,0.00`.
acceptance: yes
depends: rpt-balances
state: pending

## story 21: Implement `ledger report monthly`.
id: rpt-monthly
summary: Implement `ledger report monthly`.
type: service
kind: capability
phase: 6
block: 15
implements: FEATURE-ReportMonthly.md
covers: RPT-003
accepts: st-005, st-011
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: consumer
size: 21987
provides: ledger report monthly
consumes: ledger, transactions
instructions: |
  Write `month,transactions,inflow,outflow,net` per `YYYY-MM` that has transactions, ascending, then
  `TOTAL,<count>,<inflow>,<outflow>,<net>`. With no transactions the output is the header and
  `TOTAL,0,0.00,0.00,0.00`.
acceptance: yes
depends: rpt-balances
state: pending

## story 22: Reject unknown commands, tables, reports, and wrong argument counts with exit 2.
id: cli-usage
summary: Reject unknown commands, tables, reports, and wrong argument counts with exit 2.
type: service
kind: capability
phase: 7
block: 16
implements: FEATURE-UsageErrors.md
covers: CLI-001
accepts: st-011
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md
stack_mode: consumer
size: 19256
provides: cli.usage-errors
consumes: ledger, ledger init, ledger count, ledger load, ledger account add, ledger account get, ledger account rename, ledger account delete, ledger txn post, ledger txn get, ledger txn amend, ledger txn delete, ledger transfer, ledger report balances, ledger report categories, ledger report monthly
instructions: |
  Ensure every command, group, table, and report enforces its argument form through the shared
  UsageError path: unknown command, unknown account/txn subcommand, unknown table, unknown report, and
  any wrong argument count exit 2 with empty stdout and one stderr line naming the expected form.
  Fix any command handler that does not route through that path; a usage error never writes.
acceptance: yes
depends: ledger-init, ledger-count, load-categories, load-transactions, acct-rename, acct-delete, txn-get, txn-amend, txn-delete, transfer, rpt-categories, rpt-monthly
state: pending

## story 23: Provide `bin/test.sh` and the application pytest suite.
id: test-suite
summary: Provide `bin/test.sh` and the application pytest suite.
type: service
kind: test harness
phase: 7
block: 17
implements: FEATURE-TestSuite.md
covers: TEST-001
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md
stack_mode: consumer
size: 15393
provides: bin/test.sh
consumes: ledger
instructions: |
  Write a POSIX sh `bin/test.sh` that activates `.venv` when present, runs `pytest -q` from the
  application root, and exits zero only when every test passes. Build the pytest suite against a real
  temporary SQLite database (pointed at via DATABASE_URL): cover each command, each exit code (0 to 4),
  and rules 1 to 7, including atomic rejection of loads and transfers, the negative-balance rule, leap
  dates, amount formats, txn_id assignment, and report totals. The suite never reads sources/run.sh.
acceptance: yes
depends: cli-usage
state: pending

## story 24: Terminal gate: the supplied grader passes with every check.
id:           verification
summary:      Terminal gate: the supplied grader passes with every check.
type:         feature
kind:         integration
phase:        8
block:        18
implements:   VERIFICATION.md
covers:       VER-001
accepts:      st-001
instructions: |
  Assembly story. Confirm the finished ledger is runnable at the application root and that
  `sh bin/test.sh` and `sh sources/run.sh` both exit zero. The Programmatic Acceptance declares
  `Suite: full` and runs `sh sources/run.sh` unfiltered, requiring exit code zero. Do not modify any
  file under sources/.
stack:        common.md, python.md
stack_mode:   consumer
size:         4685
consumes:     ledger, bin/test.sh
depends:      foundation, database, config, cli-foundation, ledger-init, ledger-count, load-accounts, load-categories, load-transactions, acct-add, acct-get, acct-rename, acct-delete, txn-post, txn-get, txn-amend, txn-delete, transfer, rpt-balances, rpt-categories, rpt-monthly, cli-usage, test-suite
acceptance:   yes
state:        pending
