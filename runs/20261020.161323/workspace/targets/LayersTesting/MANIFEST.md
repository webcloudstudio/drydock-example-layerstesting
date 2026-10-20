# MANIFEST: LayersTesting
updated:     2026-10-20T16:16:34+00:00
state:       approved
blocks:      13

applied_specs: |
  ARCHITECTURE.md sha256=3360d390c466fa255f8f9444b762fc3f8aa3b3549fc965de9deb50e710830b50 commit=eb580283259f4621a38525d5a5fe1ebe005db210 applied_by=block-1 applied_at=2026-10-20T16:19:37+00:00 build_sha256=42c7ba16a0c72ec43b1231dd00afc21a628a3bc0b593e983b2ab7307e766620f
  ARCHITECTURE_compact.md sha256=d3ef648ef1398be4c30119e1259b16fafd01002568ca9024f36dda45d3f7760c commit=8f703fe1839ffcefe7007e78b1d24a667d725534 applied_by=block-5 applied_at=2026-10-20T16:28:33+00:00 build_sha256=d3ef648ef1398be4c30119e1259b16fafd01002568ca9024f36dda45d3f7760c
  DATABASE.md sha256=ff2f418d172d52e874121e5a5ae842b9b7bcba38f70b6718f8f7cd77643be755 commit=eb580283259f4621a38525d5a5fe1ebe005db210 applied_by=block-2 applied_at=2026-10-20T16:22:34+00:00 build_sha256=d53d7234012392d464f255fd29c461513c7842bb253bb02f8a2a120827a8e862 database_operations=FEATURE-PERSISTENCE-001:0d64e3ed6462727ca7ce14b19c486f33fbb209ffaa58a3b4a59dc60c0e029d82;FEATURE-PERSISTENCE-002:d938f74bfea47f0d2806b349589aa4c835a0aef5e86ebda927562f9c0f62c433;FEATURE-PERSISTENCE-003:23c76a111248842ac7f1fbefd1b0b1a6b8bd784cdfd3c582b9e3982c4dd435fd;FEATURE-PERSISTENCE-004:7594dac3568252a1a8a6368970a645974480f1384e68dc1cd83fe1bfd77797ac;FEATURE-LEDGER-001:4a2699feff05e44f2e8e8642e595c89f86abcaebc93b4fbebba4447ca496e698;FEATURE-LEDGER-002:e3d23ae82c7337a478711b16e2fcbb92909e7e2e4b1ab4ab22b522e0ec3897bb;FEATURE-LEDGER-003:0c59aae6ff342a90afe15bfc3ad89915f11f86fc624e73ce3796ad37d78ba3d8;FEATURE-LEDGER-004:ff59797cea449bff0a25cdf1571364a3458ad4e521356f4213d0a3d070bc3bbe;FEATURE-LEDGER-005:ed19f9e1efe062f537f64b21503ab1cd9428988f344454238c468d1e9b6183ea;FEATURE-LEDGER-006:f637ae94792f9239751e034e41c3aa47ab1361882ce5e3dc6e163b2fd51ba183;FEATURE-LEDGER-007:240734030d414c227ec0cdee1179883ba62ce045669f7852fcfb9c2e5b64687f;FEATURE-LEDGER-008:d403f3441c03d58957fc89a0ed68e820abea3100df19a9c37ac2dd39009c829b;FEATURE-REPORT-001:a07dcba5ae067749fc40efdd454e68aaffdf9e548438d80d04c70eeaa8ad0e96;FEATURE-REPORT-002:3e94e9a7cc29dc97238f9024f758e71bcfa6df9af89b10de40b22fa999399a8d;FEATURE-REPORT-003:bf00eb7934038be3d3bdd421826736014f00e31e679c7e963e29533ce3c0c160
  DATABASE_compact.md sha256=77793068544585463fa19fc0d71a37c429b41b0035eb199b740b202314fc264a commit=211f5129c5965c57b8fabf8f4c1988e988465855 applied_by=block-5 applied_at=2026-10-20T16:28:33+00:00 build_sha256=77793068544585463fa19fc0d71a37c429b41b0035eb199b740b202314fc264a
  FEATURE-Bulk-Reference-Loading.md sha256=70af654fa5d50ceb30a8d7e3c427d979b3f9e0035b8c4474dca7456b163b910b commit=eb580283259f4621a38525d5a5fe1ebe005db210 applied_by=block-5 applied_at=2026-10-20T16:28:33+00:00 build_sha256=7102483b03b878ba20b1e649e668fd2c6a3664c5b0cacb9bf2b98edb0151991e
  FEATURE-Persistence-Lifecycle.md sha256=4e172518d0ff5d4acdc367ee06676afdb973c81332117445134c9c4e667a8cdf commit=eb580283259f4621a38525d5a5fe1ebe005db210 applied_by=block-3 applied_at=2026-10-20T16:24:58+00:00 build_sha256=e0f8fcb888bd5b2f3ab4c538720ffc91484d346672b34b19d8cbea1a02d24e5d
  FEATURE-Validation.md sha256=acbc605d53d6ca201d8b3f232fc6b13165c679232c0ef4453c479c4c2c691af6 commit=eb580283259f4621a38525d5a5fe1ebe005db210 applied_by=block-4 applied_at=2026-10-20T16:26:42+00:00 build_sha256=9c08cc8f56f904ff147650322217753fe9b40fc043805069de45e6cba5058e94
  seed_accounts.csv sha256=48f83f688324264fd811a0a363418c867454043e30ce02bc8bc81683ed28625b commit=eb580283259f4621a38525d5a5fe1ebe005db210 applied_by=block-5 applied_at=2026-10-20T16:28:33+00:00 build_sha256=48f83f688324264fd811a0a363418c867454043e30ce02bc8bc81683ed28625b
  seed_categories.csv sha256=265d594bf154ef991105beec15a61241f46bb2b330aff215f9bffad2a0602b43 commit=eb580283259f4621a38525d5a5fe1ebe005db210 applied_by=block-5 applied_at=2026-10-20T16:28:33+00:00 build_sha256=265d594bf154ef991105beec15a61241f46bb2b330aff215f9bffad2a0602b43

## story 1: Define the ledger application boundaries and technology usage.
id:           architecture
finding: ADVISORY: implemented, not verified — no governed acceptance command covers this story. Declare one in ACCEPTANCE.json to gate it.
evidence: evidence/block-1.md
summary:      Define the ledger application boundaries and technology usage.
type:         foundational
kind:         capability
phase:        1
block:        1
implements:   ARCHITECTURE.md
scope:        both
instructions: |
  Establish the Python application structure, executable boundary, configuration resolution, service
  organization, and exclusive use of the shipped persistence library. Document ownership of CLI,
  validation, reporting, and persistence responsibilities.
stack:        common.md, python.md
stack_mode:   builder
size:         4348
provides:     application module boundaries, configuration boundary, persistence boundary
acceptance:   yes
state: closed/implemented

## story 2: Provide database configuration and the shipped persistence boundary.
id:           persist-001
finding: ADVISORY: implemented, not verified — no governed acceptance command covers this story. Declare one in ACCEPTANCE.json to gate it.
evidence: evidence/block-2.md
summary:      Provide database configuration and the shipped persistence boundary.
type:         foundational
kind:         capability
phase:        1
block:        2
implements:   DATABASE.md
covers:       PERSIST-001
scope:        both
instructions: |
  Declare the accounts, categories, and transactions schema and every repository operation required
  by the ledger workflows. Use the generated shipped persistence package and support DATABASE_URL,
  DATABASE_PATH, and data/app.db resolution without direct database-driver access.
stack:        common.md, python.md, persistence.md, sqlite.md
stack_mode:   builder
size:         9657
provides:     DATABASE_URL resolution, DATABASE_PATH fallback, relational ledger schema, persistence operations
consumes:     application module boundaries, configuration boundary, persistence boundary
depends:      architecture
acceptance:   yes
state: closed/implemented

## story 3: Initialize the ledger schema and report table counts.
id: persist-002
finding: ADVISORY: implemented, not verified — no governed acceptance command covers this story. Declare one in ACCEPTANCE.json to gate it.
evidence: evidence/block-3.md
summary: Initialize the ledger schema and report table counts.
type: service
kind: capability
phase: 1
block: 3
implements: FEATURE-Persistence-Lifecycle.md
covers: PERSIST-002
accepts: st-003
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, sqlite.md, cli.md
stack_mode: builder
size: 10595
provides: ledger init, ledger count
consumes: relational ledger schema, persistence operations
instructions: |
  Implement ledger init so it recreates the three empty tables and ledger count so it reports the
  required CSV header and deterministic table order. Preserve the specified exit and output behavior.
acceptance: yes
depends: persist-001
state: closed/implemented
scope: target

## story 4: Validate ledger identifiers, values, dates, and relationships.
id: persist-003
finding: ADVISORY: implemented, not verified — no governed acceptance command covers this story. Declare one in ACCEPTANCE.json to gate it.
evidence: evidence/block-4.md
summary: Validate ledger identifiers, values, dates, and relationships.
type: service
kind: capability
phase: 1
block: 4
implements: FEATURE-Validation.md
covers: PERSIST-003
accepts: st-007, st-008
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, sqlite.md, cli.md
stack_mode: consumer
size: 9316
provides: domain validation, integer-cent amount parsing, date validation, balance validation
consumes: relational ledger schema, persistence operations
instructions: |
  Implement shared validation for codes, names, descriptions, memos, integer-cent amounts, real
  calendar dates, identifiers, foreign-key references, atomic preflight checks, and non-negative
  account balances. Ensure rejected operations perform no writes.
acceptance: yes
depends: persist-001
state: closed/implemented
scope: target

## story 5: Load account and category CSV files atomically.
id: load-001
finding: ADVISORY: implemented, not verified — no governed acceptance command covers this story. Declare one in ACCEPTANCE.json to gate it.
evidence: evidence/block-5.md
summary: Load account and category CSV files atomically.
type: service
kind: capability
phase: 1
block: 5
implements: FEATURE-Bulk-Reference-Loading.md
covers: LOAD-001
accepts: st-004, st-007
context: seed_accounts.csv, seed_categories.csv, ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, sqlite.md, cli.md
stack_mode: consumer
size: 9285
provides: ledger load accounts, ledger load categories
consumes: domain validation, relational ledger schema, persistence operations
instructions: |
  Implement CSV header validation and atomic loading for accounts and categories. Validate the full
  file before the first write, reject duplicate or invalid rows, and emit the required loaded-row
  CSV response.
acceptance: yes
depends: persist-002, persist-003
state: closed/implemented
scope: target

## story 6: Load transaction CSV files with complete-batch validation.
id: load-002
finding: programmatic acceptance failed: load-transactions-valid: AssertionError
evidence: evidence/block-6.md
summary: Load transaction CSV files with complete-batch validation.
type: service
kind: capability
phase: 1
block: 6
implements: FEATURE-Bulk-Transaction-Loading.md
covers: LOAD-002
accepts: st-004, st-007, st-008
context: seed_transactions.csv, seed_transactions_bad.csv, ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, sqlite.md, cli.md
stack_mode: consumer
size: 10796
provides: ledger load transactions
consumes: domain validation, relational ledger schema, persistence operations
instructions: |
  Implement atomic transaction-file loading. Validate headers, identifiers, dates, amounts,
  references, duplicate transaction ids, and resulting balances for the complete batch before
  inserting any row.
acceptance: yes
depends: load-001, persist-003
state: closed/failed
scope: target

## story 7: Manage the account lifecycle through the CLI.
id: ledger-001
summary: Manage the account lifecycle through the CLI.
type: service
kind: capability
phase: 2
block: 7
implements: FEATURE-Accounts.md
covers: LEDGER-001
accepts: st-006, st-007
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, sqlite.md, cli.md
stack_mode: consumer
size: 9191
provides: ledger account add, ledger account get, ledger account rename, ledger account delete
consumes: domain validation, relational ledger schema, persistence operations
instructions: |
  Implement account add, get, rename, and delete. Return account rows with transaction counts and
  balances, reject duplicates and in-use accounts, and use the specified not-found and rejection
  exit codes without writing on failure.
acceptance: yes
depends: load-001, persist-003
state: pending
scope: target

## story 8: Post and retrieve individual transactions.
id: ledger-002
summary: Post and retrieve individual transactions.
type: service
kind: capability
phase: 2
block: 8
implements: FEATURE-Transaction-Posting.md
covers: LEDGER-002
accepts: st-006, st-007, st-008
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, sqlite.md, cli.md
stack_mode: consumer
size: 9217
provides: ledger txn post, ledger txn get
consumes: domain validation, relational ledger schema, persistence operations
instructions: |
  Implement transaction posting and retrieval. Assign the next transaction id, validate all
  references and values before writing, enforce non-negative balances, and emit transaction rows
  using exact integer-cent formatting.
acceptance: yes
depends: ledger-001, load-002
state: pending
scope: target

## story 9: Amend and delete transactions safely.
id: ledger-003
summary: Amend and delete transactions safely.
type: service
kind: capability
phase: 2
block: 9
implements: FEATURE-Transaction-Mutation.md
covers: LEDGER-003
accepts: st-006, st-007, st-008
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, sqlite.md, cli.md
stack_mode: consumer
size: 9286
provides: ledger txn amend, ledger txn delete
consumes: domain validation, relational ledger schema, persistence operations
instructions: |
  Implement transaction amendment and deletion with full preflight validation, balance protection,
  exact not-found behavior, and atomic no-write rejection semantics.
acceptance: yes
depends: ledger-002
state: pending
scope: target

## story 10: Transfer funds atomically between accounts.
id: ledger-004
summary: Transfer funds atomically between accounts.
type: service
kind: capability
phase: 2
block: 10
implements: FEATURE-Transfers.md
covers: LEDGER-004
accepts: st-006, st-007, st-008
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, sqlite.md, cli.md
stack_mode: consumer
size: 9276
provides: ledger transfer
consumes: domain validation, relational ledger schema, persistence operations
instructions: |
  Implement transfer validation and atomic creation of consecutive outgoing and incoming TRANSFER
  rows with the specified amounts and memos. Reject same-account, invalid, unknown, and
  balance-negative transfers without changing any table.
acceptance: yes
depends: ledger-002
state: pending
scope: target

## story 11: Report balances by account from persisted transactions.
id: report-001
summary: Report balances by account from persisted transactions.
type: service
kind: capability
phase: 2
block: 11
implements: FEATURE-Balance-Reports.md
covers: REPORT-001
accepts: st-005
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, sqlite.md, cli.md
stack_mode: consumer
size: 8941
provides: ledger report balances
consumes: relational ledger schema, persistence operations
instructions: |
  Implement the balances report using database-derived account aggregates. Order accounts by code,
  include transaction counts and formatted balances, and append the required TOTAL row, including
  the empty-ledger case.
acceptance: yes
depends: ledger-001, ledger-002, ledger-003, ledger-004
state: pending
scope: target

## story 12: Report transaction totals by calendar month.
id: report-003
summary: Report transaction totals by calendar month.
type: service
kind: capability
phase: 2
block: 11
implements: FEATURE-Monthly-Reports.md
covers: REPORT-003
accepts: st-005
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, sqlite.md, cli.md
stack_mode: consumer
size: 8904
provides: ledger report monthly
consumes: relational ledger schema, persistence operations
instructions: |
  Implement monthly aggregation from persisted transactions. Emit only transaction-bearing months
  in ascending YYYY-MM order, calculate integer-cent inflow, outflow, and net totals, and append
  the required TOTAL row including the empty-ledger case.
acceptance: yes
depends: report-001
state: pending
scope: target

## story 13: Report totals by category including unused categories.
id: report-002
summary: Report totals by category including unused categories.
type: service
kind: capability
phase: 2
block: 12
implements: FEATURE-Category-Reports.md
covers: REPORT-002
accepts: st-005
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, sqlite.md, cli.md
stack_mode: consumer
size: 8928
provides: ledger report categories
consumes: relational ledger schema, persistence operations
instructions: |
  Implement category aggregation from persisted rows, retaining categories with no transactions,
  calculating inflow, outflow, and net in integer cents, ordering by category code, and emitting
  the required TOTAL row.
acceptance: yes
depends: report-001
state: pending
scope: target

## story 14: Provide the project automated test runner.
id: verify-001
summary: Provide the project automated test runner.
type: service
kind: test harness
phase: 3
block: 13
implements: FEATURE-Test-Runner.md
covers: VERIFY-001
accepts: st-002
context: ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md
stack_mode: consumer
size: 5770
provides: bin/test.sh, pytest test suite
consumes: all ledger command capabilities
instructions: |
  Add the project's automated pytest coverage for commands, exit codes, validation, atomicity,
  persistence, balances, and reports. Provide a POSIX-compatible bin/test.sh that runs the suite
  from the application root and returns success only when every test passes.
acceptance: yes
depends: report-003
state: pending
scope: target

## story 15: Pass the complete supplied ledger conformance harness.
id: verify-002
summary: Pass the complete supplied ledger conformance harness.
type: service
kind: test harness
phase: 3
block: 13
implements: FEATURE-Conformance-Verification.md
covers: VERIFY-002
accepts: st-001
context: run.sh, seed_accounts.csv, seed_categories.csv, seed_transactions.csv, seed_transactions_bad.csv, ARCHITECTURE_compact.md, DATABASE_compact.md
stack: common.md, python.md, sqlite.md, cli.md
stack_mode: consumer
size: 12375
provides: full supplied conformance verification
consumes: all ledger command capabilities
instructions: |
  Run the supplied sources/run.sh unfiltered from the completed application root as the terminal
  release verification. Preserve all staged scoring assets and require the harness to exit zero.
acceptance: yes
depends: verify-001
state: pending
scope: target
