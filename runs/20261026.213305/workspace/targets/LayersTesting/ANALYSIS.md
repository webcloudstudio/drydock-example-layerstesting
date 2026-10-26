# Blueprint Analysis: drydock Layers Testing Uat Case

## Commander Expectations

- assert the completed ledger passes every check in the supplied grader, `sh sources/run.sh`, with exit code zero
- assert every command either completes in full or changes nothing
- assert every report is computed from stored ledger data, never from embedded answers
- assert amounts are stored and reported as integer cents with exactly two decimal places on output
- assert no command leaves any account balance below zero

## Crew

| Crew | Charge |
|---|---|
| Commander | Defines intent and decides what done means. |
| Team Lead | Confirms epic completeness and stakeholder expectations. |
| Planning Crew | Authors atomic specifications and the ordered Manifest. |
| Shipyard Crew | Builds the tickets without synchronous Commander access. |

## Story List

### Feature: Ledger Setup

| ID | Story | High-level AC |
|---|---|---|
| LEDGER-001 | Initialize and reset the ledger with `ledger init` | `init` writes nothing, creates the three empty tables, and removes all rows when rerun. |
| LEDGER-002 | Count stored rows with `ledger count` | `count` writes `table,rows` then the accounts, categories, and transactions rows in that order. |

### Feature: Seed Loading

| ID | Story | High-level AC |
|---|---|---|
| LOAD-001 | Load accounts from a CSV file with `ledger load accounts` | Matching header accepted; all rows stored or none; writes `table,loaded` and `accounts,<rows>`. |
| LOAD-002 | Load categories from a CSV file with `ledger load categories` | Matching header accepted; all rows stored or none; writes `table,loaded` and `categories,<rows>`. |
| LOAD-003 | Load transactions from a CSV file with `ledger load transactions` | Source `txn_id` kept; unknown account or category, bad row, or negative final balance rejects the whole file with exit 3. |

### Feature: Account Maintenance

| ID | Story | High-level AC |
|---|---|---|
| ACCT-001 | Add an account with `ledger account add` | Stores a new unique code with a name and prints the account row with zero transactions and balance 0.00; duplicate code exits 3. |
| ACCT-002 | Read an account with `ledger account get` | Prints the current account row with transaction count and balance computed from stored transactions; absent code exits 4. |
| ACCT-003 | Rename an account with `ledger account rename` | Changes only the name and prints the updated row; absent code exits 4. |
| ACCT-004 | Delete an account with `ledger account delete` | Removes an account with no transactions and prints `deleted` and the code; an account with transactions is refused with exit 3; absent code exits 4. |

### Feature: Transaction Maintenance

| ID | Story | High-level AC |
|---|---|---|
| TXN-001 | Post a transaction with `ledger txn post` | Assigns the next txn_id, validates account, category, amount, date, and memo, rejects any negative balance, and prints the new row. |
| TXN-002 | Read a transaction with `ledger txn get` | Prints the stored row for an id; absent id exits 4. |
| TXN-003 | Amend a transaction amount with `ledger txn amend` | Changes only the amount, rejects any negative resulting balance, and prints the updated row; absent id exits 4. |
| TXN-004 | Delete a transaction with `ledger txn delete` | Removes the row only when no balance goes negative, prints `deleted` and the id; absent id exits 4. |

### Feature: Transfers

| ID | Story | High-level AC |
|---|---|---|
| XFER-001 | Record a transfer between two accounts with `ledger transfer` | Writes a `TRANSFER` debit and credit with consecutive ids, both or neither, and prints both rows; accounts must differ and amount must be positive. |

### Feature: Reports

| ID | Story | High-level AC |
|---|---|---|
| RPT-001 | Report account balances with `ledger report balances` | One row per account ordered by code, then `TOTAL,,<count>,<sum>`, with all values computed from stored data. |
| RPT-002 | Report category totals with `ledger report categories` | One row per category including unused ones, with inflow, outflow, and net, then the TOTAL row. |
| RPT-003 | Report monthly totals with `ledger report monthly` | One row per `YYYY-MM` with transactions, ascending, then the TOTAL row. |

### Feature: CLI Contract

| ID | Story | High-level AC |
|---|---|---|
| CLI-001 | Provide the `ledger` executable and usage errors | Executable at the application root; unknown command, unknown report or table, or wrong argument count exits 2 with usage on stderr only. |
| CLI-002 | Format CSV output for every successful command | Headers, comma separators, no quoting, `\n` endings, amounts with two decimals and a leading `-` when negative. |
| CLI-003 | Map failures to exit codes and stderr diagnostics | Exit 1 for operational failure, 3 for rejection, 4 for not found; one diagnostic line on stderr and nothing on stdout. |

### Feature: Verification

| ID | Story | High-level AC |
|---|---|---|
| TEST-001 | Provide the POSIX `bin/test.sh` automated suite | `bin/test.sh` runs pytest cases covering each command, exit code, and rule against a real temporary database; exits zero only when all pass. |
| VERIFY-001 | Pass the supplied LayersTesting grader | `sh sources/run.sh` run unfiltered from the application root exits zero with all 43 checks passing. |

## Story Guidance

Named stories planning must produce. Authoritative record: `STORY_GUIDANCE.json`.

None.

## Surfaced Acceptance Criteria

| ID | Story ID | Criterion |
|---|---|---|
| AC-001 | LEDGER-001 | A failed command writes no database URL, path credential, or DSN password to standard error or standard output. |
| AC-002 | LEDGER-001 | An empty `DATABASE_URL` is treated as unset, and `DATABASE_PATH` is used only when `DATABASE_URL` is unset. |
| AC-003 | LOAD-001 | A file whose header differs from the table's column names or their order is rejected with exit 3 before any row is stored. |
| AC-004 | LOAD-003 | A transactions file containing only its header loads zero rows and reports `transactions,0`. |
| AC-005 | LOAD-003 | The negative-balance rule is judged on each account's final balance after the whole file, so an intermediate row may dip below zero if a later row in the same file restores it. |
| AC-006 | ACCT-001 | Account names may repeat across accounts; only account codes are unique. |
| AC-007 | ACCT-003 | Renaming an account to its current name succeeds and returns the unchanged row. |
| AC-008 | TXN-001 | An amount with no digit before the decimal point, such as `.50`, or with a leading `+`, spaces, or a thousands separator is rejected with exit 3. |
| AC-009 | TXN-001 | Zero is rejected in every accepted form, including `0`, `0.00`, and `-0`. |
| AC-010 | TXN-001 | Leap days are valid only in leap years: `2028-02-29` is accepted and `2026-02-29` is rejected with exit 3. |
| AC-011 | TXN-001 | A posting with no memo argument stores an empty memo and writes the row with an empty final field. |
| AC-012 | TXN-001 | Each posting computes its txn_id and inserts its row in one database transaction, so two concurrent posts never share an id. |
| AC-013 | XFER-001 | The balance checks and both inserts of a transfer run in one database transaction, so a concurrent command cannot take either balance below zero between check and write. |
| AC-014 | RPT-001 | On an empty ledger, `report balances` writes its header and `TOTAL,,0,0.00`. |
| AC-015 | RPT-001 | Every report orders its rows by code using byte order, so digits sort before letters. |
| AC-016 | RPT-003 | On an empty ledger, `report monthly` writes its header and `TOTAL,0,0.00,0.00,0.00`. |
| AC-017 | CLI-002 | A zero total is written as `0.00`, never `-0.00`, in every report. |
| AC-018 | CLI-001 | With no arguments, `ledger` writes its usage text to standard error and exits 2, and the usage text names every command and sub-verb in the command table. |
| AC-019 | TEST-001 | Every test in the `bin/test.sh` suite creates and removes its own temporary database and never touches `data/app.db`. |

## Source Inventory

| Path | Content kind | Disposition | Reason |
|---|---|---|---|
| `sources/INSTRUCTIONS.md` | markdown | analyzed | readable UTF-8 |
| `sources/run.sh` | code | analyzed | readable UTF-8 |
| `sources/seed_accounts.csv` | text | analyzed | readable UTF-8 |
| `sources/seed_categories.csv` | text | analyzed | readable UTF-8 |
| `sources/seed_transactions.csv` | text | analyzed | readable UTF-8 |
| `sources/seed_transactions_bad.csv` | text | analyzed | readable UTF-8 |

## Relationship Model

| Source or group | Relationship type | Related source or group | Evidence | Delivery implication |
|---|---|---|---|---|
| sources/INSTRUCTIONS.md | instruction-to-test | sources/run.sh | Harness section: 43 checks compare exit code and stdout with known answers. | Grader defines release evidence; each story's AC traces to the command table and rules. |
| sources/run.sh | dependency | sources/seed_accounts.csv, sources/seed_categories.csv, sources/seed_transactions.csv | run.sh `$SEED` path and `load` checks B1 to B3. | Seed files must be staged beside the grader at `sources/`. |
| sources/run.sh | dependency | sources/seed_transactions_bad.csv | run.sh check D1 expects exit 3 on row 11 `NOSUCH`. | Rejection story LOAD-003 must stage and enforce all-or-nothing behavior. |
| sources/INSTRUCTIONS.md | dependency | Persistence layer generated from DATABASE.md | Database section: all access goes through the shipped library. | Every data story depends on the persistence boundary; no story opens a driver. |
| sources/INSTRUCTIONS.md | test-kit-to-implementation | bin/test.sh and pytest suite | Tests section: POSIX `bin/test.sh` runs the suite and exits zero only when all pass. | TEST-001 builds the runner; VERIFY-001 does not depend on it for grader evidence. |
| sources/seed_transactions.csv | dependency | sources/seed_accounts.csv, sources/seed_categories.csv | Transactions reference accounts SAFE, PETTY, DRAWER1, DRAWER2 and categories listed in the other files. | Accounts and categories load before transactions. |
| sources/INSTRUCTIONS.md | reference-to-replacement | sources/run.sh | Rule that application code never reads or embeds grader answers. | Reports must be computed from the database; st-012 guards this. |

## Source Roles

| Path | Role | Plan disposition | Build disposition |
|---|---|---|---|
| sources/INSTRUCTIONS.md | normative specification | context | prompt-only |
| sources/run.sh | conformance harness | context | stage |
| sources/seed_accounts.csv | asset | context | stage |
| sources/seed_categories.csv | asset | context | stage |
| sources/seed_transactions.csv | asset | context | stage |
| sources/seed_transactions_bad.csv | asset | context | stage |

## Planning Instructions

### Delivery Shape

The system is a single-operator command-line cash ledger. The executable `ledger` sits at the application root and must have its executable bit set, because `run.sh` tests `-x`. Each invocation resolves the database from `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`, runs one command, and exits. Inputs are command arguments, CSV files, and the database. Outputs are CSV on standard output for successful commands, a single diagnostic line on standard error for failures, and an exit code from the table in the sources. Every write is all-or-nothing.

### Story Realization Map

| Story ID | Durable scope | Evidence | Related | Kind |
|---|---|---|---|---|
| LEDGER-001 | Create or reset the three tables; database resolution | INSTRUCTIONS Database, Commands `init`; run.sh A1, Z1 | persistence layer | capability |
| LEDGER-002 | Row counts in fixed order | INSTRUCTIONS `count`; run.sh A2, B4, D3, Z2 | LEDGER-001 | capability |
| LOAD-001 | Accounts file load | INSTRUCTIONS `load`; seed_accounts.csv; run.sh B1, D2 | LEDGER-001 | capability |
| LOAD-002 | Categories file load | INSTRUCTIONS `load`; seed_categories.csv; run.sh B2 | LEDGER-001 | capability |
| LOAD-003 | Transactions file load with validation and balance rule | INSTRUCTIONS Rules 1 and 2; seed_transactions.csv; seed_transactions_bad.csv; run.sh B3, D1 | LOAD-001, LOAD-002 | capability |
| ACCT-001 | Add account | INSTRUCTIONS `account add`; run.sh E1, E2 | LEDGER-001 | capability |
| ACCT-002 | Get account | INSTRUCTIONS `account get`; run.sh E3, E5, E8 | ACCT-001 | capability |
| ACCT-003 | Rename account | INSTRUCTIONS `account rename`; run.sh E4 | ACCT-001 | capability |
| ACCT-004 | Delete account with in-use refusal | INSTRUCTIONS `account delete`, exit 3 and 4; run.sh E6, E7 | ACCT-001, TXN-001 | capability |
| TXN-001 | Post transaction | INSTRUCTIONS `txn post`, Rules 2 to 7; run.sh F1, F5 to F7, F10, G3 | ACCT-001, LOAD-002 | capability |
| TXN-002 | Get transaction | INSTRUCTIONS `txn get`; run.sh F2, F4, F9 | TXN-001 | capability |
| TXN-003 | Amend transaction amount | INSTRUCTIONS `txn amend`; run.sh F3, G4 | TXN-001 | capability |
| TXN-004 | Delete transaction | INSTRUCTIONS `txn delete`; run.sh F8, G5 | TXN-001 | capability |
| XFER-001 | Paired transfer rows | INSTRUCTIONS `transfer`; run.sh G1, G2 | TXN-001 | capability |
| RPT-001 | Balances report | INSTRUCTIONS `report balances`; run.sh C1, H1 | LOAD-003, XFER-001 | capability |
| RPT-002 | Categories report | INSTRUCTIONS `report categories`; run.sh C2, H2 | LOAD-003, XFER-001 | capability |
| RPT-003 | Monthly report | INSTRUCTIONS `report monthly`; run.sh C3, H3 | LOAD-003, XFER-001 | capability |
| CLI-001 | Executable entry point and usage exit 2 | INSTRUCTIONS Output, Exit codes; run.sh U1, U2 | none | capability |
| CLI-002 | CSV output formatting | INSTRUCTIONS Output and Rule 5; run.sh all stdout checks | RPT-001 to RPT-003 | capability |
| CLI-003 | Exit codes and stderr diagnostics | INSTRUCTIONS Exit codes and Output | CLI-001 | capability |
| TEST-001 | Application test suite via `bin/test.sh` | INSTRUCTIONS Tests | all implementation stories | test harness |
| VERIFY-001 | Terminal grader gate | run.sh; SEA_TRIALS st-001 | all other stories | acceptance contract |

### Test and Acceptance Strategy

Each implementation story is verified by focused pytest cases it owns, declared `Suite: scoped`. A story runs only its own slice and never the whole suite. TEST-001 runs only the test files it adds.

VERIFY-001 is the single terminal verification story. It depends on every implementation story, declares `Suite: full`, and runs `sh sources/run.sh` unfiltered. It proves SEA_TRIALS st-001 with exit code zero and all 43 checks passing.

The grader accepts no scope selector, so no per-story gate is declared. Sea Trial criteria st-004 through st-011 and st-015 are proven by VERIFY-001 and TEST-001. The guardrails st-012 and st-013 are proven by grep checks. st-014 is judged by LLM review.

### Sequencing and Dependencies

1. CLI-001 and LEDGER-001 (executable and empty schema).
2. LEDGER-002 and LOAD-001, LOAD-002 (counts and reference data).
3. LOAD-003 (transactions require accounts and categories).
4. ACCT-001 to ACCT-004 and TXN-001 to TXN-004 (maintenance; ACCT-004 depends on TXN-001 for the in-use check).
5. XFER-001 (depends on TXN-001).
6. RPT-001 to RPT-003 (depend on loaded and posted data).
7. CLI-002 and CLI-003 (output and exit-code contract, applied across the commands above).
8. TEST-001 (after the commands it covers).
9. VERIFY-001 (terminal, after everything).

Fixtures: the four seed CSV files must be staged at `sources/` before any LOAD story runs.

### Source Conflicts and Gaps

Resolved with the narrowest consistent behavior, per the unattended policy:

- Balance rule timing: Rule 2 says no command leaves a balance below zero, so it is judged on the final state after the whole command. This is recorded in AC-005.
- Authentication: the sources state no user model. The ledger is a single-operator local tool and relies on database access control. No application-level auth is built.
- Credentials in diagnostics: AC-001 forbids echoing DSN secrets.
- Usage and help text: the sources do not define it. AC-018 derives it from the command table.
- Pytest and `bin/test.sh`: these are not in conflict. `bin/test.sh` is the POSIX entry point, and pytest runs underneath it.
- Tests and grader: the grader remains the release evidence. `bin/test.sh` is the application's own suite.

## Analysis Notes
generated: 2026-10-26
blueprint: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261026.213305/workspace/targets/LayersTesting/blueprint

Quality: Ready
  blockers: 0
  questions: 0
  features: 8
  stories: 22
  stack: Python 3.11+ over SQLite through the shipped persistence library
  display_name: not proposed
  short_description: not proposed

- Unattended UAT policy applied: no blocker, questionnaire, or open question was emitted. Every ambiguity is resolved in the Planning Instructions and Surfaced Acceptance Criteria.
- Identity: `DISPLAY_NAME` and `SHORT_DESCRIPTION` are both set, so no identity questionnaire was emitted.
- Stack: SQLAlchemy and Alembic rows are included because the stack rule requires them for relational Python persistence. The sources do not use them directly. The shipped persistence library is the access layer, and the Rigging catalog supersedes SQLAlchemy for Target persistence. The Commander may remove these rows.
- COMPASS.md omitted: `COMPASS_EXISTS` is true and `COMPASS_PENDING_FORMAT` is false.
- STORY_GUIDANCE.json omitted: the imported grader partitions its checks by section but accepts no scope selector, so it supplies no runner gate.
- Prior project criteria: st-001, st-004 through st-008, st-010, and st-011 are preserved with their IDs and text. st-002, st-003, and st-009 are retired and not re-emitted. The prior `Testability` and `Consequence` fields are not in the emitted schema and are dropped. The prior Policy and Acceptance scope prose is reader documentation and is not re-emitted.
- New criteria: st-012 (no grader reads or embedded answers), st-013 (no floating-point amounts), st-014 (no direct driver access), and st-015 (`bin/test.sh` suite) are derived from explicit prohibitions and requirements in the sources.
- st-014 is `llm`-verified and marked required, so it lowers the acceptance coverage score. The team accepts that cost because no reliable automated check exists for driver access.
- Spot check: H1 DRAWER1 balance 1799.38 equals C1 2299.38 minus the 500.00 transfer in G1, and the 123-transaction total in H1 agrees with the grader's sequence.
