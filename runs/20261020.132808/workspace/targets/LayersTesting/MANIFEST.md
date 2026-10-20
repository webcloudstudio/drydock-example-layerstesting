# MANIFEST: LayersTesting
updated:     2026-10-20T13:43:15+00:00
state:       approved
blocks:      31

applied_specs: |
  ARCHITECTURE.md sha256=49ef8b29edc8ef8fa0d6cd272eec7dbd47a5dcbb584b85a31883482c96cf0e37 commit=3b3d4173ffc62bca0e3fa6ca83e175288d7b5766 applied_by=block-2 applied_at=2026-10-20T13:52:36+00:00 build_sha256=49ef8b29edc8ef8fa0d6cd272eec7dbd47a5dcbb584b85a31883482c96cf0e37
  ARCHITECTURE_compact.md sha256=10ab35885e386f20ca2691e4bea49025dad8dd405b03faf2e3caec9a88146ef3 commit=b1d8587065c14deb8ee5bd3fc1ffb1658053ad6c applied_by=block-3 applied_at=2026-10-20T13:53:59+00:00 build_sha256=10ab35885e386f20ca2691e4bea49025dad8dd405b03faf2e3caec9a88146ef3
  DATABASE.md sha256=650916af259dc734c7ccc409d6e94a7ac33236f48bcbcafce67250823e473913 commit=3b3d4173ffc62bca0e3fa6ca83e175288d7b5766 applied_by=block-2 applied_at=2026-10-20T13:52:36+00:00 build_sha256=650916af259dc734c7ccc409d6e94a7ac33236f48bcbcafce67250823e473913 database_operations=FEATURE-ACCOUNT-001:c6d536dacbfd56a523354d8b39ffc41316798573a60b15f385cab81413be8cab;FEATURE-ACCOUNT-002:5f648d102c0968aecac3f2a5e8b05a27ae234cf6836ea2d2027379e26d3443d7;FEATURE-ACCOUNT-003:ffbdd54b0de70c9d95a3cde29079660cbc79c3110f507aec38acb5b3fbf27498;FEATURE-ACCOUNT-004:2fdf44ae6d577c33ec7f755b8d9ecac445a129b023e0da1f04d116fecaa4d0de;FEATURE-ACCOUNT-005:0d03b4058072bb602f47b50dd653a8f7f5b2ce271215f2816266ad8b5af83635;FEATURE-CATEGORY-001:4c1e9dd2ba8a634ace5b4718d3a1f8e9ccbdf985ed3663ef697326c14e8f3425;FEATURE-CATEGORY-002:53efd3ca49ccefc5db95ce37c82824a07f4af207eeed6c7ada012c556a12e46b;FEATURE-CATEGORY-003:1e5d96daf33f222a03d155130a203a42a851509a8fc3b2ecf4cf92ece16847ce;FEATURE-TXN-001:402433fc8f41fe541a1b18bc21198d7097efdff8cbc178e1c76f7ce459f61db6;FEATURE-TXN-002:7ff535e5ab8cb1ad5824357639e6a4a08b23b06970d571bedc056d12c29675fa;FEATURE-TXN-003:741a0bfe2a6fb70b0b637b72858fbbf1d739bfe7af482d1119b735f81cd45b36;FEATURE-TXN-004:d76997b4461d52929045b9946bff9cbd33f172be82e2cfaba4fcff7dbaa97874;FEATURE-TXN-005:dfae485b962de69ffd3289b066e374dce566e80338d37c8dc6a27480b87d23da
  DATABASE_compact.md sha256=2ca9f00deb2384591af34a53d0dfb9374e040d3e3da294a137600c81b2518d12 commit=b1d8587065c14deb8ee5bd3fc1ffb1658053ad6c applied_by=block-3 applied_at=2026-10-20T13:53:59+00:00 build_sha256=2ca9f00deb2384591af34a53d0dfb9374e040d3e3da294a137600c81b2518d12
  FEATURE-CLI-Platform.md sha256=a7a23d66f8a2e94d86f9f46cdbc87e4437c95f8c40594aeb073f86f2eadc0d82 commit=3b3d4173ffc62bca0e3fa6ca83e175288d7b5766 applied_by=block-2 applied_at=2026-10-20T13:52:36+00:00 build_sha256=29112af1c9c251bdbffa789b4ee69485611a3f1a965145534021f5083eabb994
  FEATURE-Database-Location.md sha256=cd823f2f45e77d6a187a4f587083012c16137adc1aa6fb32d68d9ebb489492bf commit=3b3d4173ffc62bca0e3fa6ca83e175288d7b5766 applied_by=block-3 applied_at=2026-10-20T13:53:59+00:00 build_sha256=c8734830386b259ad30d4686bcb905e1412c7e010502dca68f361709af642747

## story 1: Stand up the Python project root, environment, dependency manifest, and launchers.
id:           python-foundation
finding: ADVISORY: implemented, not verified — no governed acceptance command covers this story. Declare one in ACCEPTANCE.json to gate it.
evidence: evidence/block-1.md
summary:      Stand up the Python project root, environment, dependency manifest, and launchers.
type:         foundational
kind:         capability
phase:        1
block:        1
implements:   ARCHITECTURE.md
instructions: |
  Create the project root with pyproject.toml and a committed uv.lock. Create .venv with uv venv and declare Python 3.11 or newer, pytest, and ruff.
  Provide bin/ launchers that activate .venv. Record the module ownership table and the derived Technology Stack section in ARCHITECTURE.md.
stack:        common.md, python.md
stack_mode:   builder
size:         6868
provides:     project root, .venv, pyproject.toml, uv.lock, pytest -q runner, bin/ launchers
acceptance:   yes
state: closed/implemented

## story 2: Generate the persistence package and schema.sql from DATABASE.md through the shipped Rigging library.
id:           database-step
finding: ADVISORY: implemented, not verified — no governed acceptance command covers this story. Declare one in ACCEPTANCE.json to gate it.
evidence: evidence/block-2.md
summary:      Generate the persistence package and schema.sql from DATABASE.md through the shipped Rigging library.
type:         foundational
kind:         migration
phase:        1
block:        2
implements:   DATABASE.md
accepts:      st-009
instructions: |
  Declare the accounts, categories, and transactions tables with columns, primary keys, and foreign keys, and an access pattern for each table operation the services use.
  The DATABASE step copies the shipped persistence library and generates persistence/schema.py and schema.sql. This story writes no persistence code.
stack:        persistence.md, sqlite.md, python.md
stack_mode:   builder
size:         11775
provides:     open_database(dsn), persistence.testing.db_session, schema.sql
depends:      python-foundation
acceptance:   yes
state: closed/implemented

## story 3: Stand up the cli package, its main entry, the cli_runner fixture, and the ledger launcher.
id: cli-foundation
finding: ADVISORY: implemented, not verified — no governed acceptance command covers this story. Declare one in ACCEPTANCE.json to gate it.
evidence: evidence/block-2.md
summary: Stand up the cli package, its main entry, the cli_runner fixture, and the ledger launcher.
type: foundational
kind: capability
phase: 1
block: 2
implements: FEATURE-CLI-Platform.md
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: cli.md, python.md
stack_mode: builder
size: 10554
provides: cli.main(argv), cli.testing.cli_runner, ./ledger
instructions: |
  Provide cli/__init__.py with main(argv: list[str] | None = None) -> int and cli/testing.py with cli_runner returning (exit_code, stdout, stderr).
  Ship the ledger executable at the application root that delegates to main. Command routing is owned by cli-dispatch.
acceptance: yes
depends: python-foundation
state: closed/implemented

## story 4: Resolve the database location from DATABASE_URL, then DATABASE_PATH, then data/app.db.
id: db-location
finding: ADVISORY: implemented, not verified — no governed acceptance command covers this story. Declare one in ACCEPTANCE.json to gate it.
evidence: evidence/block-3.md
summary: Resolve the database location from DATABASE_URL, then DATABASE_PATH, then data/app.db.
type: service
kind: integration
phase: 1
block: 3
implements: FEATURE-Database-Location.md
covers: DB-001
accepts: st-009
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md
stack_mode: consumer
size: 8843
provides: resolve_database_location()
consumes: open_database
instructions: |
  Select DATABASE_URL first, then DATABASE_PATH, then data/app.db resolved against the working directory. Accept an optional sqlite:// prefix.
  Recognize postgres:// and postgresql:// and exit 1 with a diagnostic stating that this build has no PostgreSQL backend.
  Reach the store only through open_database(dsn).
acceptance: yes
depends: database-step, cli-foundation
state: closed/implemented

## story 5: Run every command in one database transaction that rolls back on any failure.
id: db-transaction
finding: programmatic acceptance failed: command-transaction-commits: AttributeError: 'int' object has no attribute 'account'
evidence: evidence/block-4.md
summary: Run every command in one database transaction that rolls back on any failure.
type: service
kind: capability
phase: 1
block: 4
implements: FEATURE-Command-Transaction.md
covers: DB-003
accepts: st-007
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md
stack_mode: consumer
size: 8361
provides: command transaction wrapper
instructions: |
  Run each command inside one transaction on the store from open_database(dsn). Any failure rolls back every change.
  A write lock held by another connection exits 1 with no change.
acceptance: yes
depends: db-location
state: closed/failed

## story 6: Dispatch ledger commands and reject usage errors with exit 2.
id: cli-dispatch
summary: Dispatch ledger commands and reject usage errors with exit 2.
type: service
kind: capability
phase: 1
block: 5
implements: FEATURE-CLI-Dispatch.md
covers: CLI-001
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: cli.md, python.md
stack_mode: consumer
size: 10643
provides: ledger <command> routing
instructions: |
  Route each command word to its handler. An unknown command, unknown table, unknown report, or wrong argument count exits 2 with one stderr line and nothing on stdout.
  Command handlers are supplied by their own stories.
acceptance: yes
depends: cli-foundation
state: pending

## story 7: Map unreachable databases, missing tables, and unreadable inputs to exit 1 with no change.
id: db-errors
summary: Map unreachable databases, missing tables, and unreadable inputs to exit 1 with no change.
type: service
kind: capability
phase: 1
block: 6
implements: FEATURE-Operational-Errors.md
covers: DB-002
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md
stack_mode: consumer
size: 8237
instructions: |
  Exit 1 with one stderr line when the database is unreachable, when a non-init command finds its tables missing, or when an input file is unreadable.
  Write nothing to stdout and change nothing.
acceptance: yes
depends: db-location, cli-dispatch
state: pending

## story 8: Drop and recreate the three tables empty for ledger init.
id: schema-init
summary: Drop and recreate the three tables empty for ledger init.
type: service
kind: migration
phase: 1
block: 7
implements: FEATURE-Schema-Init.md
covers: SCHEMA-001
accepts: st-003
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 10761
provides: ledger init
instructions: |
  ledger init drops accounts, categories, and transactions if present, recreates them empty, writes nothing to stdout, and exits 0.
  Apply the schema through the persistence package only.
acceptance: yes
depends: db-transaction, cli-dispatch
state: pending

## story 9: Emit the CSV success output contract for every command except init.
id: cli-output
summary: Emit the CSV success output contract for every command except init.
type: service
kind: capability
phase: 1
block: 8
implements: FEATURE-CLI-Output.md
covers: CLI-003
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: cli.md, python.md
stack_mode: consumer
size: 10756
provides: CSV row writer
instructions: |
  Write a header row then data rows to stdout: comma-separated, unquoted, \n line endings, no trailing spaces.
  Failure diagnostics go to stderr as one line and are never compared.
acceptance: yes
depends: cli-foundation
state: pending

## story 10: Print the row count of each table for ledger count.
id: schema-count
summary: Print the row count of each table for ledger count.
type: service
kind: capability
phase: 1
block: 9
implements: FEATURE-Schema-Count.md
covers: SCHEMA-002
accepts: st-003
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 10866
provides: ledger count
instructions: Print table,rows, then accounts, categories, and transactions counts in that order. Each count is read through its table's count operation.
acceptance: yes
depends: schema-init, cli-output
state: pending

## story 11: Validate codes, names, descriptions, and memos.
id: val-codes
summary: Validate codes, names, descriptions, and memos.
type: service
kind: capability
phase: 2
block: 10
implements: FEATURE-Code-Validation.md
covers: VAL-001
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md
stack_mode: consumer
size: 8675
provides: validate_code, validate_name, validate_memo
instructions: |
  Codes are 1 to 12 characters of A-Z and 0-9. Names and descriptions are 1 to 40 characters. Memos are 0 to 60 characters.
  None may contain a comma or newline. A violation exits 3 with no change.
acceptance: yes
depends: python-foundation
state: pending

## story 12: Parse and format amounts as integer cents.
id: val-amount
summary: Parse and format amounts as integer cents.
type: service
kind: capability
phase: 2
block: 11
implements: FEATURE-Amount-Format.md
covers: VAL-002
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md
stack_mode: consumer
size: 8377
provides: parse_amount_cents, format_amount_cents
instructions: |
  Accept input matching -?DIGITS[.D[D]] as integer cents. Zero in any form (0, 0.00, -0.00) exits 3.
  Format with two decimals, a leading - when negative, and no separators. A zero total prints 0.00, never -0.00. Use no floating point.
acceptance: yes
depends: python-foundation
state: pending

## story 13: Validate real YYYY-MM-DD calendar dates.
id: val-dates
summary: Validate real YYYY-MM-DD calendar dates.
type: service
kind: capability
phase: 2
block: 12
implements: FEATURE-Date-Validation.md
covers: VAL-003
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md
stack_mode: consumer
size: 7827
provides: parse_date
instructions: Accept only real YYYY-MM-DD calendar dates. Impossible dates such as 2026-02-30 exit 3.
acceptance: yes
depends: python-foundation
state: pending

## story 14: Print one line of help per command in the usage diagnostic.
id: cli-help
summary: Print one line of help per command in the usage diagnostic.
type: service
kind: capability
phase: 2
block: 13
implements: FEATURE-CLI-Help.md
covers: CLI-002
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: cli.md, python.md
stack_mode: consumer
size: 10787
provides: usage listing on stderr
instructions: Running ledger with no arguments writes the usage listing of every command and sub-verb to stderr and exits 2. No help command is added.
acceptance: yes
depends: cli-dispatch
state: pending

## story 15: Reject any command that leaves an account below zero before commit.
id: db-balance
summary: Reject any command that leaves an account below zero before commit.
type: service
kind: capability
phase: 3
block: 14
implements: FEATURE-Balance-Rule.md
covers: DB-004
accepts: st-008
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md
stack_mode: consumer
size: 8759
provides: non-negative balance check
instructions: |
  After a command's changes and before commit, compute each touched account's balance as the sum of its transaction amounts.
  Any balance below zero exits 3 with no change.
acceptance: yes
depends: db-transaction, val-amount
state: pending

## story 16: Load the accounts CSV all or nothing.
id: load-accounts
summary: Load the accounts CSV all or nothing.
type: service
kind: capability
phase: 4
block: 15
implements: FEATURE-Load-Accounts.md
covers: LOAD-001
accepts: st-004, st-007
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 12332
provides: ledger load accounts <csv>
instructions: |
  Check the header matches account,name in order. Validate each row, reject duplicate keys, and store all rows or none.
  Print table,loaded then accounts,<rows>. A header-only file loads zero rows and exits 0.
acceptance: yes
depends: database-step, val-codes, db-transaction, cli-output, cli-dispatch
state: pending

## story 17: Load the categories CSV all or nothing.
id: load-categories
summary: Load the categories CSV all or nothing.
type: service
kind: capability
phase: 4
block: 16
implements: FEATURE-Load-Categories.md
covers: LOAD-002
accepts: st-004, st-007
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 12394
provides: ledger load categories <csv>
instructions: |
  Check the header matches category,description in order. Apply the same validation, duplicate, and all-or-none rules as accounts.
  Print table,loaded then categories,<rows>.
acceptance: yes
depends: database-step, val-codes, db-transaction, cli-output, cli-dispatch
state: pending

## story 18: Load the transactions CSV all or nothing under the balance rule.
id: load-transactions
summary: Load the transactions CSV all or nothing under the balance rule.
type: service
kind: capability
phase: 4
block: 17
implements: FEATURE-Load-Transactions.md
covers: LOAD-003
accepts: st-004, st-007
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 12432
provides: ledger load transactions <csv>
instructions: |
  Keep each file's txn_id. Reject unknown accounts or categories and any balance breach for the whole file.
  Store none of the rows on rejection and exit 3. Print table,loaded then transactions,<rows> on success.
acceptance: yes
depends: load-accounts, load-categories, db-balance, val-amount, val-dates, db-transaction, cli-output, cli-dispatch
state: pending

## story 19: Add an account with zero transactions and a zero balance.
id: account-add
summary: Add an account with zero transactions and a zero balance.
type: service
kind: capability
phase: 5
block: 18
implements: FEATURE-Account-Add.md
covers: ACCT-001
accepts: st-006
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 11448
provides: ledger account add <code> <name>
instructions: Print the new row with 0 transactions and balance 0.00. A duplicate code exits 3.
acceptance: yes
depends: val-codes, val-amount, cli-output, db-transaction, cli-dispatch
state: pending

## story 20: Print an account with its transaction count and balance.
id: account-get
summary: Print an account with its transaction count and balance.
type: service
kind: capability
phase: 5
block: 19
implements: FEATURE-Account-Get.md
covers: ACCT-002
accepts: st-006
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 11284
provides: ledger account get <code>
instructions: Print the account row with its transaction count and balance. An absent code exits 4.
acceptance: yes
depends: val-codes, val-amount, cli-output, db-transaction, cli-dispatch
state: pending

## story 21: Rename an account.
id: account-rename
summary: Rename an account.
type: service
kind: capability
phase: 5
block: 20
implements: FEATURE-Account-Rename.md
covers: ACCT-003
accepts: st-006
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 11135
provides: ledger account rename <code> <name>
instructions: Print the updated row. An absent code exits 4. An invalid name exits 3.
acceptance: yes
depends: val-codes, cli-output, db-transaction, cli-dispatch
state: pending

## story 22: Delete an account that has no transactions.
id: account-delete
summary: Delete an account that has no transactions.
type: service
kind: capability
phase: 5
block: 21
implements: FEATURE-Account-Delete.md
covers: ACCT-004
accepts: st-006
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 10901
provides: ledger account delete <code>
instructions: Print deleted and the code. An account referenced by any transaction exits 3. An absent account exits 4.
acceptance: yes
depends: val-codes, cli-output, db-transaction, cli-dispatch
state: pending

## story 23: Post a transaction with the next id after validating every field.
id: txn-post
summary: Post a transaction with the next id after validating every field.
type: service
kind: capability
phase: 6
block: 22
implements: FEATURE-Transaction-Post.md
covers: TXN-001
accepts: st-006, st-007
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 12411
provides: ledger txn post, next_txn_id()
instructions: |
  Validate argument syntax before any lookup, so a malformed amount exits 3 even when the account is absent.
  A missing account or category exits 3. Assign the next id as the largest txn_id plus one, or 1 when the table is empty. Apply the balance rule and print the new row.
acceptance: yes
depends: val-codes, val-amount, val-dates, db-balance, db-transaction, cli-output, cli-dispatch
state: pending

## story 24: Print one transaction by id.
id: txn-get
summary: Print one transaction by id.
type: service
kind: capability
phase: 6
block: 23
implements: FEATURE-Transaction-Get.md
covers: TXN-002
accepts: st-006
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 10722
provides: ledger txn get <id>
instructions: Reject a non-integer id with exit 3 before any lookup. Print the row. An absent id exits 4.
acceptance: yes
depends: val-amount, db-transaction, cli-output, cli-dispatch
state: pending

## story 25: Amend the amount of one transaction.
id: txn-amend
summary: Amend the amount of one transaction.
type: service
kind: capability
phase: 6
block: 24
implements: FEATURE-Transaction-Amend.md
covers: TXN-003
accepts: st-006, st-007
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 11522
provides: ledger txn amend <id> <amount>
instructions: Change only the amount. Apply the balance rule. Print the updated row. An absent id exits 4. A rejected amendment changes nothing.
acceptance: yes
depends: val-amount, db-balance, db-transaction, cli-output, cli-dispatch
state: pending

## story 26: Delete one transaction by id.
id: txn-delete
summary: Delete one transaction by id.
type: service
kind: capability
phase: 6
block: 25
implements: FEATURE-Transaction-Delete.md
covers: TXN-004
accepts: st-006, st-007
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 11531
provides: ledger txn delete <id>
instructions: Apply the balance rule after the delete. Print deleted and the id. An absent id exits 4. A rejected delete changes nothing.
acceptance: yes
depends: db-balance, db-transaction, cli-output, cli-dispatch
state: pending

## story 27: Store a transfer as two TRANSFER rows, or neither.
id: transfer
summary: Store a transfer as two TRANSFER rows, or neither.
type: service
kind: capability
phase: 7
block: 26
implements: FEATURE-Transfer.md
covers: XFER-001
accepts: st-007
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 12636
provides: ledger transfer <from> <to> <amount> <date>
instructions: |
  Require a positive amount, two distinct existing accounts, and a valid date. Take the next two ids from next_txn_id.
  Write -amount on <from> with memo "transfer to <to>" and +amount on <to> with memo "transfer from <from>" in category TRANSFER. Apply the balance rule. Store both rows or neither.
acceptance: yes
depends: txn-post, db-balance, val-amount, val-dates, val-codes, cli-output, cli-dispatch
state: pending

## story 28: Report one row per account and a TOTAL row.
id: report-balances
summary: Report one row per account and a TOTAL row.
type: service
kind: capability
phase: 8
block: 27
implements: FEATURE-Report-Balances.md
covers: RPT-001
accepts: st-005
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 11655
provides: ledger report balances
instructions: Compute every value by query. Print one row per account ordered by code, then TOTAL,,<count>,<sum>. With no accounts, print only TOTAL,,0,0.00.
acceptance: yes
depends: val-amount, db-transaction, cli-output, cli-dispatch
state: pending

## story 29: Report one row per category, including empty ones, and a TOTAL row.
id: report-categories
summary: Report one row per category, including empty ones, and a TOTAL row.
type: service
kind: capability
phase: 8
block: 28
implements: FEATURE-Report-Categories.md
covers: RPT-002
accepts: st-005
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 11868
provides: ledger report categories
instructions: Compute every value by query. Print every category ordered by code, including those with no transactions, then TOTAL,,<count>,<inflow>,<outflow>,<net>.
acceptance: yes
depends: val-amount, db-transaction, cli-output, cli-dispatch
state: pending

## story 30: Report one row per month that has transactions, and a TOTAL row.
id: report-monthly
summary: Report one row per month that has transactions, and a TOTAL row.
type: service
kind: capability
phase: 8
block: 29
implements: FEATURE-Report-Monthly.md
covers: RPT-003
accepts: st-005
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 11851
provides: ledger report monthly
instructions: Compute every value by query. Print one row per YYYY-MM with transactions, ascending, then TOTAL,<count>,<inflow>,<outflow>,<net>. With no transactions, print only TOTAL,0,0.00,0.00,0.00.
acceptance: yes
depends: val-amount, db-transaction, cli-output, cli-dispatch
state: pending

## story 31: Provide the POSIX bin/test.sh that drives the pytest suite against a temporary database.
id: test-suite
summary: Provide the POSIX bin/test.sh that drives the pytest suite against a temporary database.
type: service
kind: test harness
phase: 9
block: 30
implements: FEATURE-Automated-Suite.md
covers: VER-001
accepts: st-002
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md
stack_mode: consumer
size: 9030
provides: bin/test.sh
instructions: |
  Write bin/test.sh as POSIX sh. It runs pytest against a real temporary database and exits zero only when every test passes.
  The suite covers each command, each exit code, and each rule.
acceptance: yes
depends: python-foundation, cli-foundation, database-step
state: pending

## story 32: Pass the supplied acceptance grader end to end against the completed application.
id: terminal-grader
summary: Pass the supplied acceptance grader end to end against the completed application.
type: feature
kind: test harness
phase: 10
block: 31
implements: FEATURE-Acceptance-Grader.md
covers: VER-002
accepts: st-001
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md
stack_mode: consumer
size: 9357
provides: sh sources/run.sh exits 0
instructions: |
  Stage sources/run.sh and the seed files verbatim into the application root. Do not author or modify them.
  Gate on sh sources/run.sh run unfiltered from the application root. Declare Suite: full. Require exit 0.
acceptance: yes
depends: python-foundation, database-step, cli-foundation, db-location, db-errors, db-transaction, schema-init, schema-count, cli-dispatch, cli-output, val-codes, val-amount, val-dates, cli-help, db-balance, load-accounts, load-categories, load-transactions, account-add, account-get, account-rename, account-delete, txn-post, txn-get, txn-amend, txn-delete, transfer, report-balances, report-categories, report-monthly, test-suite
state: pending
