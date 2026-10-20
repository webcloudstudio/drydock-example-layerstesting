# MANIFEST: LayersTesting
updated:     2026-10-20T18:37:21+00:00
state:       approved
blocks:      10

applied_specs: |
  ARCHITECTURE.md sha256=750530d15ea45e43f4b4233543217a74fc8c77f4775441af30ff82a665b44dbe commit=44e7a3937f1da5d8973beb3196245f87280e761d applied_by=block-1 applied_at=2026-10-20T18:40:59+00:00 build_sha256=d8c2ebf7d67fc032936816e4a5ae6b7a8fb14879359a9b1f5a30ccd4e5261d65
  ARCHITECTURE_compact.md sha256=f76131315f0f2bcc0bcb3d755fd146951e4e13246f64636f2126b0703c59043d commit=edefbe1f94cd41748f7403d3af42d7d50fcc6513 applied_by=block-4 applied_at=2026-10-20T18:47:14+00:00 build_sha256=f76131315f0f2bcc0bcb3d755fd146951e4e13246f64636f2126b0703c59043d
  DATABASE.md sha256=303bb0ec282f9b3375363468a39a228230a2468245669b4366732e6dfd6eb647 commit=44e7a3937f1da5d8973beb3196245f87280e761d applied_by=block-2 applied_at=2026-10-20T18:43:04+00:00 build_sha256=a9093d531a3d129fea58a512ca9ac80371409a61af4a3a2eae49e734ef44c2be database_operations=FEATURE-ACCOUNT-001:af9e39ad1b676271e206b5432ea8ba418ad611a0faf98e1169c0dc6ed29c2bef;FEATURE-ACCOUNT-002:347b96b1c54ceb2b664764a5f08e34fb5a1a7d6552215dc71f146e0f4073d2c2;FEATURE-ACCOUNT-003:faa7496e0ac3705fd531b039d65a9b53ecaba20865ee1992c2573ccaccd2042e;FEATURE-ACCOUNT-004:3cef903ff63bdf19f8b3abd352cfd53f99fd06d59e1f6c6e4d997eff24710add;FEATURE-ACCOUNT-005:8c0a3f14e3ceb49cb5cac4010314e10565e0b16d9cebbf0a73e6901190f419c5;FEATURE-CATEGORY-001:65961f4112b27ffe26126e86748114bb158543ef114d67f9e1311a5e91c4ca50;FEATURE-CATEGORY-002:e47177e3e52af492d12ee4805091f3205aaf38a2fc9c708275bae8a3c993b3e6;FEATURE-TXN-001:82dd1c3a74b4e74b5cd237bd38bd41be2e35b08bb9994d177b14cd27c3c0d2eb;FEATURE-TXN-002:0fa1e4d809b442c912a8d66a852b41224b48181adfdff9cbf4338195db2c9842;FEATURE-TXN-003:216139a7de2c5fe6e96a649c90c81632aefe4c55accd505f60e2cdbd0a14c111;FEATURE-TXN-004:c1596c6d542be65e7bf7c273b23b01b00c4de19da55bec319ab1038148054ff3;FEATURE-TXN-005:5163d2ab37c945991e6251990fa0a9260f5348a91eb77ea0f9c4882a498632c4
  DATABASE_compact.md sha256=ece75dc13ed47ce9a36a4d0d400dd31caa214a1dcfb96b068f1dbbbc4378ce7a commit=4ffbc4e130231df7c2e09fc6d3409aef9ee8c5ae applied_by=block-4 applied_at=2026-10-20T18:47:14+00:00 build_sha256=ece75dc13ed47ce9a36a4d0d400dd31caa214a1dcfb96b068f1dbbbc4378ce7a
  FEATURE-BULK-LOADING.md sha256=22b30c9970f59612f6e108e72ddb03cfb305d2fdb7e19586ecd5746b3af8a13a commit=44e7a3937f1da5d8973beb3196245f87280e761d applied_by=block-4 applied_at=2026-10-20T18:47:14+00:00 build_sha256=540df132a606e48987ba3fe1f699d2e32dd78e76a2b4b4e5549b2af8733543a0
  FEATURE-CLI-FOUNDATION.md sha256=6ef937eccc705f1f06d1807591e19b59cc22c405626b4551e5dcbf592ba6b9fe commit=44e7a3937f1da5d8973beb3196245f87280e761d applied_by=block-2 applied_at=2026-10-20T18:43:04+00:00 build_sha256=46b3be910860182b4bf89372b1274881af3c8a0fdb468aa58627a5ee10743204
  FEATURE-SCHEMA-LIFECYCLE.md sha256=bcb470e2d07166c42d89e1dfabb1f25ad7a4b3f5aaf031d23b1526b4b829b531 commit=44e7a3937f1da5d8973beb3196245f87280e761d applied_by=block-3 applied_at=2026-10-20T18:44:30+00:00 build_sha256=2223477fa56bc02687cc7ba4052e7ebf098967eb2ed482af41a8767cee8ceefb

## story 1: Define the ledger application architecture and module boundaries.
id:           architecture
finding: ADVISORY: implemented, not verified — no governed acceptance command covers this story. Declare one in ACCEPTANCE.json to gate it.
evidence: evidence/block-1.md
summary:      Define the ledger application architecture and module boundaries.
type:         foundational
kind:         capability
phase:        1
block:        1
implements:   ARCHITECTURE.md
instructions: |
  Define the Python application structure, configuration resolution, command routing,
  service boundaries, and the rule that all database access goes through the shipped
  persistence package.
stack:        python.md
stack_mode:   builder
size:         2504
provides:     application module boundaries, configuration boundary, persistence boundary
acceptance:   yes
state: closed/implemented

## story 2: Establish the relational persistence contract for the cash ledger.
id:           database
finding: ADVISORY: implemented, not verified — no governed acceptance command covers this story. Declare one in ACCEPTANCE.json to gate it.
evidence: evidence/block-2.md
summary:      Establish the relational persistence contract for the cash ledger.
type:         foundational
kind:         migration
phase:        1
block:        2
implements:   DATABASE.md
covers:       DATA-001
accepts:      st-009
context:      ARCHITECTURE.md
instructions: |
  Declare the accounts, categories, and transactions tables, integer-cent amounts,
  foreign keys, repository operations, and database selection precedence. Use the
  shipped persistence library and expose the generated repository contract to callers.
stack:        persistence.md, sqlite.md, python.md
stack_mode:   builder
size:         8693
provides:     accounts repository, categories repository, transactions repository
consumes:     application module boundaries
depends:      architecture
acceptance:   yes
state: closed/implemented

## story 3: Provide the executable ledger command and command validation.
id: cli-foundation
finding: ADVISORY: implemented, not verified — no governed acceptance command covers this story. Declare one in ACCEPTANCE.json to gate it.
evidence: evidence/block-2.md
summary: Provide the executable ledger command and command validation.
type: foundational
kind: capability
phase: 1
block: 2
implements: FEATURE-CLI-FOUNDATION.md
covers: CLI-001
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: cli.md, python.md
stack_mode: builder
size: 6932
provides: ./ledger, CLI command dispatch, usage validation
consumes: accounts repository, categories repository, transactions repository
instructions: |
  Implement the executable ledger entry point, command dispatch, argument-count
  validation, unknown-command handling, and discoverable help or usage guidance for
  every documented command and subcommand.
acceptance: yes
depends: database
state: closed/implemented

## story 4: Initialize and inspect the ledger database schema.
id: schema-lifecycle
finding: ADVISORY: implemented, not verified — no governed acceptance command covers this story. Declare one in ACCEPTANCE.json to gate it.
evidence: evidence/block-3.md
summary: Initialize and inspect the ledger database schema.
type: service
kind: migration
phase: 1
block: 3
implements: FEATURE-SCHEMA-LIFECYCLE.md
covers: CLI-002
accepts: st-003
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: cli.md, sqlite.md, python.md
stack_mode: consumer
size: 8357
provides: ledger init, ledger count
consumes: accounts repository, categories repository, transactions repository
instructions: |
  Implement init so it drops and recreates all three tables atomically and emits no
  output. Implement count with the required table order and row counts.
acceptance: yes
depends: cli-foundation
state: closed/implemented

## story 5: Load validated account, category, and transaction CSV files atomically.
id: bulk-loading
finding: ADVISORY: implemented, not verified — no governed acceptance command covers this story. Declare one in ACCEPTANCE.json to gate it.
evidence: evidence/block-4.md
summary: Load validated account, category, and transaction CSV files atomically.
type: service
kind: capability
phase: 1
block: 4
implements: FEATURE-BULK-LOADING.md
covers: DATA-002
accepts: st-004, st-007
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: cli.md, sqlite.md, python.md
stack_mode: consumer
size: 8934
provides: ledger load accounts, ledger load categories, ledger load transactions
consumes: accounts repository, categories repository, transactions repository
instructions: |
  Implement CSV header and row validation, code/name/memo/amount/date validation,
  duplicate detection, reference validation, integer-cent conversion, balance
  validation, and all-or-nothing loading for each supported table.
acceptance: yes
depends: schema-lifecycle
state: closed/implemented

## story 6: Generate account balance reports from persisted ledger state.
id: balance-reports
finding: step block-5 failed: transaction-post-read
evidence: evidence/block-5.md
summary: Generate account balance reports from persisted ledger state.
type: service
kind: capability
phase: 2
block: 5
implements: FEATURE-BALANCE-REPORTS.md
covers: REPORT-001
accepts: st-005
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: cli.md, sqlite.md, python.md
stack_mode: consumer
size: 8021
provides: ledger report balances
consumes: accounts repository, transactions repository
instructions: |
  Implement the balances report using database queries. Order accounts by code,
  include transaction counts and formatted balances, and emit the required total row.
acceptance: yes
depends: bulk-loading
state: closed/failed

## story 7: Manage posting, lookup, amendment, and deletion of transactions.
id: transaction-lifecycle
finding: programmatic acceptance failed: transaction-post-read: AssertionError
evidence: evidence/block-5.md
summary: Manage posting, lookup, amendment, and deletion of transactions.
type: service
kind: capability
phase: 2
block: 5
implements: FEATURE-TRANSACTION-LIFECYCLE.md
covers: OPS-002
accepts: st-006, st-007, st-008
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: cli.md, sqlite.md, python.md
stack_mode: consumer
size: 8115
provides: ledger txn post, ledger txn get, ledger txn amend, ledger txn delete
consumes: accounts repository, categories repository, transactions repository
instructions: |
  Implement transaction posting, lookup, amendment, and deletion with ID allocation,
  input validation, absent-record exit code 4 behavior, atomic rejection, and balance
  protection.
acceptance: yes
depends: cli-foundation
state: closed/failed

## story 8: Generate category and monthly ledger reports.
id: aggregate-reports
summary: Generate category and monthly ledger reports.
type: service
kind: capability
phase: 2
block: 6
implements: FEATURE-AGGREGATE-REPORTS.md
covers: REPORT-002
accepts: st-005
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: cli.md, sqlite.md, python.md
stack_mode: consumer
size: 8248
provides: ledger report categories, ledger report monthly
consumes: categories repository, transactions repository
instructions: |
  Implement category and monthly aggregation from persisted transactions, including
  zero-transaction categories, ordering, inflow, outflow, net, and total rows.
acceptance: yes
depends: bulk-loading
state: pending

## story 9: Manage account creation, lookup, rename, and deletion.
id: account-lifecycle
summary: Manage account creation, lookup, rename, and deletion.
type: service
kind: capability
phase: 2
block: 7
implements: FEATURE-ACCOUNT-LIFECYCLE.md
covers: OPS-001
accepts: st-006, st-007
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: cli.md, sqlite.md, python.md
stack_mode: consumer
size: 8222
provides: ledger account add, ledger account get, ledger account rename, ledger account delete
consumes: accounts repository, transactions repository
instructions: |
  Implement account CRUD operations with validation, duplicate handling, absent-record
  exit code 4 behavior, in-use deletion protection, and the specified CSV output.
acceptance: yes
depends: cli-foundation
state: pending

## story 10: Execute paired atomic transfers between accounts.
id: transfers
summary: Execute paired atomic transfers between accounts.
type: service
kind: capability
phase: 2
block: 8
implements: FEATURE-TRANSFERS.md
covers: FIN-001
accepts: st-007, st-008
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: cli.md, sqlite.md, python.md
stack_mode: consumer
size: 8091
provides: ledger transfer
consumes: accounts repository, categories repository, transactions repository
instructions: |
  Implement transfers as one atomic operation that validates distinct existing
  accounts, positive amount, date, available balance, consecutive IDs, TRANSFER
  category, and required memos before writing either row.
acceptance: yes
depends: transaction-lifecycle
state: pending

## story 11: Enforce non-negative account balances across every mutation path.
id: financial-invariants
summary: Enforce non-negative account balances across every mutation path.
type: service
kind: integration
phase: 2
block: 9
implements: FEATURE-FINANCIAL-INVARIANTS.md
covers: FIN-002
accepts: st-007, st-008
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: cli.md, sqlite.md, python.md
stack_mode: consumer
size: 8708
provides: cross-command balance invariant enforcement
consumes: accounts repository, transactions repository
instructions: |
  Apply the non-negative balance invariant consistently to loads, posts, amendments,
  deletes, and transfers. Ensure every rejected operation performs no writes and
  returns exit code 3.
acceptance: yes
depends: bulk-loading, transaction-lifecycle, transfers
state: pending

## story 12: Provide automated tests and run the complete supplied ledger conformance suite.
id: conformance
summary: Provide automated tests and run the complete supplied ledger conformance suite.
type: service
kind: test harness
phase: 3
block: 10
implements: FEATURE-CONFORMANCE.md
covers: QA-001
accepts: st-001, st-002, st-004, st-005, st-006, st-007, st-008, st-009
context: run.sh, seed_accounts.csv, seed_categories.csv, seed_transactions.csv, seed_transactions_bad.csv, ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, cli.md, sqlite.md
stack_mode: builder
size: 14309
provides: bin/test.sh, complete supplied conformance verification
consumes: ./ledger, accounts repository, categories repository, transactions repository
instructions: |
  Add the project's pytest suite and POSIX-compatible bin/test.sh. Stage the supplied
  grader and seed assets unchanged. As the terminal story, run the complete supplied
  suite without filtering and require its successful exit status.
acceptance: yes
depends: architecture, database, cli-foundation, schema-lifecycle, bulk-loading, balance-reports, aggregate-reports, account-lifecycle, transaction-lifecycle, transfers, financial-invariants
state: pending
