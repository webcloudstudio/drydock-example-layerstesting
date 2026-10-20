# Blueprint Analysis: LayersTesting

## Commander Expectations

- assert the product runs as an executable named `ledger` at the application root
- assert `sh sources/run.sh` exits zero against the completed application
- assert every command either completes in full or changes nothing
- assert every report is computed from the database
- assert amounts are stored as integer cents and never as floating point
- assert no account balance goes negative

## Crew

| Crew | Charge |
|---|---|
| Commander | Defines intent and decides what done means. |
| Team Lead | Confirms epic completeness and stakeholder expectations. |
| Planning Crew | Authors atomic specifications and the ordered Manifest. |
| Shipyard Crew | Builds the tickets without synchronous Commander access. |

## Story List

### Feature: Application Foundation

| ID | Story | High-level AC |
|---|---|---|
| FOUNDATION-001 | Executable ledger entry point at the application root | An executable named `ledger` at the application root dispatches every command in the Commands table. |
| FOUNDATION-002 | Database selection by DATABASE_URL, DATABASE_PATH, and default path | DATABASE_URL is used first, then DATABASE_PATH, then `data/app.db`; a `sqlite://` prefix is optional; `postgres://` and `postgresql://` select PostgreSQL. |
| FOUNDATION-003 | Relational access only through the shipped persistence library | Every read and write reaches the database through the persistence library and generated relational layer; no command opens a driver directly. |
| FOUNDATION-004 | Integer-cent amount storage | Amounts are stored as integer cents and converted to two-decimal text only at the output boundary. |
| FOUNDATION-005 | Automated test runner `bin/test.sh` | A POSIX `bin/test.sh` runs the automated suite against a real temporary database, accepts a slice selector, and exits zero only when every test passes. |

### Feature: Command Line Interface

| ID | Story | High-level AC |
|---|---|---|
| CLI-001 | CSV output conventions | Successful commands other than `init` write one header row then data rows, comma-separated, unquoted, no trailing spaces, `\n` line endings. |
| CLI-002 | Exit code mapping and diagnostics | Exit codes 0, 1, 2, 3, and 4 are returned as the Exit codes table states; a failing command writes nothing to standard output and one diagnostic line to standard error. |
| CLI-003 | Usage errors | An unknown command, unknown load table, unknown report, or wrong argument count exits 2. |
| CLI-004 | Help text for every command and sub-verb | Each command and sub-verb prints its usage and arguments on `--help` and exits 0; help output is exempt from the CSV output rule. |

### Feature: Input Validation

| ID | Story | High-level AC |
|---|---|---|
| VALID-001 | Code validation | Codes are 1 to 12 characters from `A-Z` and `0-9`; any other code is rejected with exit 3. |
| VALID-002 | Name, description, and memo validation | Names and descriptions are 1 to 40 characters, memos 0 to 60; none contains a comma or newline; violations exit 3. |
| VALID-003 | Amount validation and formatting | Input amounts match `-?DIGITS[.D[D]]`, are never zero, and have at most two decimal places; output amounts have exactly two decimal places with no thousands separator. |
| VALID-004 | Date validation | Dates are real calendar dates in `YYYY-MM-DD`; `2026-02-30` is rejected with exit 3. |

### Feature: Schema Lifecycle

| ID | Story | High-level AC |
|---|---|---|
| SCHEMA-001 | Initialize an empty schema | `ledger init` drops and recreates the three tables empty, writes nothing, and exits 0. |
| SCHEMA-002 | Count rows per table | `ledger count` writes `table,rows` then the `accounts`, `categories`, and `transactions` counts in that order. |

### Feature: Ledger Integrity

| ID | Story | High-level AC |
|---|---|---|
| INTEG-001 | Every command is one database transaction | A failing command leaves every table exactly as it was; a transfer stores both rows or neither. |
| INTEG-002 | Non-negative balance rule | Post, amend, delete, transfer, and load are checked after the command's changes and before commit; any balance below zero is rejected with exit 3. |

### Feature: Bulk Loading

| ID | Story | High-level AC |
|---|---|---|
| LOAD-001 | Load accounts from a CSV file | `ledger load accounts <csv>` loads the file and writes `table,loaded` then `accounts,<rows>`. |
| LOAD-002 | Load categories from a CSV file | `ledger load categories <csv>` loads the file and writes `table,loaded` then `categories,<rows>`. |
| LOAD-003 | Load transactions keeping file txn_ids | `ledger load transactions <csv>` loads each row with its file `txn_id` and writes `table,loaded` then `transactions,<rows>`. |
| LOAD-004 | Reject a load atomically | A file with an invalid row or a duplicate key exits 3 and stores none of its rows. |
| LOAD-005 | Reject a load with a mismatched header | A file whose header does not match the table's columns in order exits 3; an unreadable file exits 1. |

### Feature: Accounts

| ID | Story | High-level AC |
|---|---|---|
| ACCT-001 | Add an account | `account add <code> <name>` writes the new account row with zero transactions and balance `0.00`; a duplicate code exits 3. |
| ACCT-002 | Get an account | `account get <code>` writes the account row; an absent code exits 4. |
| ACCT-003 | Rename an account | `account rename <code> <name>` writes the updated account row; an absent code exits 4. |
| ACCT-004 | Delete an account | `account delete <code>` writes `deleted` then the code when the account has no transactions; an account with transactions exits 3; an absent code exits 4. |

### Feature: Transactions

| ID | Story | High-level AC |
|---|---|---|
| TXN-001 | Post a transaction | `txn post` writes the new row with `txn_id` one more than the largest present, or `1` in an empty table; an unknown account or category exits 3. |
| TXN-002 | Get a transaction | `txn get <id>` writes the transaction row; an absent id exits 4. |
| TXN-003 | Amend a transaction amount | `txn amend <id> <amount>` changes only the amount and writes the updated row; an absent id exits 4. |
| TXN-004 | Delete a transaction | `txn delete <id>` writes `deleted` then the id; an absent id exits 4. |

### Feature: Transfers

| ID | Story | High-level AC |
|---|---|---|
| XFER-001 | Transfer between two accounts | `transfer <from> <to> <amount> <date>` stores two rows in category `TRANSFER`: `-amount` on `<from>` then `+amount` on `<to>`, with the memos and ids the Commands table specifies. |
| XFER-002 | Reject an invalid transfer | A transfer with identical accounts, a non-positive amount, or an unknown account exits 3 and changes nothing. |

### Feature: Reports

| ID | Story | High-level AC |
|---|---|---|
| RPT-001 | Balances report | `report balances` writes one row per account ordered by code, then `TOTAL,,<count>,<sum>`. |
| RPT-002 | Categories report | `report categories` writes one row per category ordered by code, including categories with no transactions, then the TOTAL row. |
| RPT-003 | Monthly report | `report monthly` writes one row per `YYYY-MM` that has transactions, ascending, then the TOTAL row. |

### Feature: Acceptance Verification

| ID | Story | High-level AC |
|---|---|---|
| VERIFY-001 | Complete grader and suite gate | `sh sources/run.sh` exits zero with every check passing, and `bin/test.sh` exits zero, from the completed application root. |

## Story Guidance

Named stories planning must produce. Authoritative record: `STORY_GUIDANCE.json`.

| Story ID | Provenance | Gate | Note |
|---|---|---|---|
| CLI-003 | plan | — | sources/run.sh section U (U1, U2); sources/INSTRUCTIONS.md Exit codes 2 |
| SCHEMA-001 | plan | — | sources/run.sh section A (A1) and section Z (Z1); sources/INSTRUCTIONS.md Commands init |
| SCHEMA-002 | plan | — | sources/run.sh section A (A2), section Z (Z2), and the count checks in sections B4, D3, G6 |
| INTEG-002 | plan | — | sources/run.sh section G (G3 to G5); sources/INSTRUCTIONS.md Rule 2 |
| LOAD-001 | plan | — | sources/run.sh section B (B1); sources/seed_accounts.csv |
| LOAD-002 | plan | — | sources/run.sh section B (B2); sources/seed_categories.csv |
| ACCT-001 | plan | — | sources/run.sh section E (E1, E2) |
| ACCT-002 | plan | — | sources/run.sh section E (E3, E5) |
| ACCT-003 | plan | — | sources/run.sh section E (E4) |
| ACCT-004 | plan | — | sources/run.sh section E (E6 to E8); sources/INSTRUCTIONS.md Commands account delete |
| LOAD-003 | plan | — | sources/run.sh section B (B3, B4); sources/seed_transactions.csv |
| LOAD-004 | plan | — | sources/run.sh section D (D1 to D3); sources/seed_transactions_bad.csv |
| TXN-001 | plan | — | sources/run.sh section F (F1, F5 to F7, F10) |
| TXN-002 | plan | — | sources/run.sh section F (F2, F4, F9) |
| TXN-003 | plan | — | sources/run.sh section F (F3) |
| TXN-004 | plan | — | sources/run.sh section F (F8) |
| XFER-001 | plan | — | sources/run.sh section G (G1); sources/INSTRUCTIONS.md Commands transfer |
| XFER-002 | plan | — | sources/run.sh section G (G2) |
| RPT-001 | plan | — | sources/run.sh section C (C1) and section H (H1) |
| RPT-002 | plan | — | sources/run.sh section C (C2) and section H (H2) |
| RPT-003 | plan | — | sources/run.sh section C (C3) and section H (H3) |
| VERIFY-001 | plan | — | sources/run.sh in full, run unfiltered across sections A through Z; sources/INSTRUCTIONS.md Run Harness |

## Surfaced Acceptance Criteria

| ID | Story ID | Criterion |
|---|---|---|
| AC-001 | RPT-001 | When no account rows exist, `report balances` shall write the header row and `TOTAL,,0,0.00`. |
| AC-002 | RPT-002 | When no category rows exist, `report categories` shall write the header row and `TOTAL,,0,0.00,0.00,0.00`. |
| AC-003 | RPT-003 | When no transactions exist, `report monthly` shall write the header row and `TOTAL,0,0.00,0.00,0.00`. |
| AC-004 | FOUNDATION-002 | The database connection shall use the persistence library's default connect timeout, and an expired connect attempt shall exit 1. |
| AC-005 | INTEG-001 | If two commands run concurrently against one database, then each shall commit or fail as a single transaction with no partial change. |
| AC-006 | CLI-004 | When `--help` is given to any command or sub-verb, the application shall print its usage and arguments to standard output and exit 0. |

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
| sources/run.sh | instruction-to-test | sources/INSTRUCTIONS.md | run.sh checks A through Z implement the Commands and Output sections | The grader is the executable form of the Commands table; stories cite both. |
| sources/seed_accounts.csv | fixture-to-harness | sources/run.sh | checks B1, D2, C1 | Loader for accounts must accept this exact header and file. |
| sources/seed_categories.csv | fixture-to-harness | sources/run.sh | check B2 | Loader for categories must accept this exact header and file. |
| sources/seed_transactions.csv | fixture-to-harness | sources/run.sh | checks B3, B4, C1 to C3 | Transaction loading and all reports depend on these 120 rows. |
| sources/seed_transactions_bad.csv | fixture-to-harness | sources/run.sh | check D1 | Row 11 names an unknown account; the whole file must be rejected atomically. |
| sources/INSTRUCTIONS.md Rules | dependency | sources/INSTRUCTIONS.md Commands | Rule 1 atomicity and Rule 2 balance apply to every mutating command | INTEG-001 and INTEG-002 precede the mutating stories in the build order. |
| sources/INSTRUCTIONS.md Database | dependency | sources/seed_transactions.csv | Foreign keys from transactions to accounts and categories | Accounts and categories load before transactions. |

## Source Roles

| Path | Role | Plan disposition | Build disposition |
|---|---|---|---|
| sources/INSTRUCTIONS.md | author intent | compass | prompt-only |
| sources/run.sh | conformance harness | context | stage |
| sources/seed_accounts.csv | asset | context | stage |
| sources/seed_categories.csv | asset | context | stage |
| sources/seed_transactions.csv | asset | context | stage |
| sources/seed_transactions_bad.csv | asset | context | stage |

## Planning Instructions

### Delivery Shape

The product is a local, single-user, command-line cash ledger. There is no server, UI, network service, or authentication; the sources name no protected resource.

Inputs are command arguments, three CSV seed files, and the `DATABASE_URL`, `DATABASE_PATH`, or default database path. Outputs are CSV on standard output, one diagnostic line on standard error, and the exit code.

Execution flow for every command: parse arguments, validate each field, open one database transaction, apply the change, check that no balance is negative, then commit or roll back. Successful output is written after commit. The required first command is `ledger init`, followed by loading accounts and categories, then transactions, then any commands or reports.

### Story Realization Map

- FOUNDATION-001: Application root executable. Evidence: sources/INSTRUCTIONS.md Objective; sources/run.sh guard for `./ledger`. Type: capability.
- FOUNDATION-002: Database resolution and PostgreSQL DSN recognition. Evidence: sources/INSTRUCTIONS.md Database. Type: integration.
- FOUNDATION-003: Persistence boundary through the library and generated relational layer. Evidence: sources/INSTRUCTIONS.md Database and Stack. Type: capability.
- FOUNDATION-004: Integer-cent storage. Evidence: sources/INSTRUCTIONS.md Database. Type: capability.
- FOUNDATION-005: `bin/test.sh` runner with slice selector. Evidence: sources/INSTRUCTIONS.md Tests. Type: test harness.
- CLI-001: Output conventions. Evidence: sources/INSTRUCTIONS.md Output. Type: capability.
- CLI-002: Exit codes and diagnostics. Evidence: sources/INSTRUCTIONS.md Exit codes; sources/run.sh stderr is never compared. Type: capability.
- CLI-003: Usage errors. Evidence: run.sh U1, U2; Exit codes 2. Type: capability.
- CLI-004: Help text. Evidence: Core Baseline for CLI; no source text; resolved by AC-006. Type: capability.
- VALID-001: Code rules. Evidence: sources/INSTRUCTIONS.md Rule 3; run.sh F5. Type: capability.
- VALID-002: Name, description, memo rules. Evidence: sources/INSTRUCTIONS.md Rule 4. Type: capability.
- VALID-003: Amount rules. Evidence: sources/INSTRUCTIONS.md Rule 5; run.sh F6. Type: capability.
- VALID-004: Date rules. Evidence: sources/INSTRUCTIONS.md Rule 6; run.sh F7. Type: capability.
- SCHEMA-001: Init. Evidence: run.sh A1, Z1; Commands init. Type: capability.
- SCHEMA-002: Count. Evidence: run.sh A2, Z2, B4, D3, G6. Type: capability.
- INTEG-001: Single-transaction commands. Evidence: INSTRUCTIONS.md Rule 1; run.sh D1 to D3, G1. Type: capability.
- INTEG-002: Non-negative balance rule. Evidence: INSTRUCTIONS.md Rule 2; run.sh G3 to G5. Type: capability.
- LOAD-001: Load accounts. Evidence: run.sh B1; seed_accounts.csv. Type: capability.
- LOAD-002: Load categories. Evidence: run.sh B2; seed_categories.csv. Type: capability.
- LOAD-003: Load transactions. Evidence: run.sh B3, B4; seed_transactions.csv. Type: capability.
- LOAD-004: Atomic rejected load. Evidence: run.sh D1, D2; seed_transactions_bad.csv row 11. Type: capability.
- LOAD-005: Header and file checks. Evidence: INSTRUCTIONS.md Commands load; Exit codes 1 and 3. Type: capability.
- ACCT-001: Add account. Evidence: run.sh E1, E2. Type: capability.
- ACCT-002: Get account. Evidence: run.sh E3, E5. Type: capability.
- ACCT-003: Rename account. Evidence: run.sh E4. Type: capability.
- ACCT-004: Delete account. Evidence: run.sh E6 to E8; Commands account delete. Type: capability.
- TXN-001: Post transaction. Evidence: run.sh F1, F5 to F7, F10. Type: capability.
- TXN-002: Get transaction. Evidence: run.sh F2, F4, F9. Type: capability.
- TXN-003: Amend amount. Evidence: run.sh F3. Type: capability.
- TXN-004: Delete transaction. Evidence: run.sh F8. Type: capability.
- XFER-001: Transfer rows. Evidence: run.sh G1; Commands transfer. Type: capability.
- XFER-002: Transfer rejection. Evidence: run.sh G2. Type: capability.
- RPT-001: Balances report. Evidence: run.sh C1, H1. Type: capability.
- RPT-002: Categories report. Evidence: run.sh C2, H2. Type: capability.
- RPT-003: Monthly report. Evidence: run.sh C3, H3. Type: capability.
- VERIFY-001: Complete grader and suite gate. Evidence: run.sh full file; INSTRUCTIONS.md Run Harness. Type: acceptance contract.

### Test and Acceptance Strategy

- Story-level tests are scoped. Each feature story runs only the slice of `bin/test.sh` it owns and declares `Suite: scoped`. FOUNDATION-005 creates the slice selector that every later story uses. No feature story runs `sources/run.sh` whole, because run.sh has no selector.
- Exactly one terminal verification story, VERIFY-001, gates on the complete suite. It depends on all 35 implementation stories and declares `Suite: full` in its heading block. It runs `sh sources/run.sh` unfiltered and requires zero failed checks, and runs `bin/test.sh` unfiltered.
- Sea Trial st-001 is the one conformance proof of the complete grader. Seed counts and report totals appear only as Sea Trial criteria and as check values inside run.sh. They are not restated as story thresholds.
- Story-level checks use the owned command and exit code; they do not restate the known report answers.

### Sequencing and Dependencies

Build order, one story per line:

1. FOUNDATION-001
2. FOUNDATION-002
3. FOUNDATION-003
4. FOUNDATION-004
5. FOUNDATION-005
6. CLI-001
7. CLI-002
8. CLI-003
9. VALID-001
10. VALID-002
11. VALID-003
12. VALID-004
13. SCHEMA-001
14. SCHEMA-002
15. INTEG-001
16. INTEG-002
17. LOAD-001
18. LOAD-002
19. ACCT-001
20. ACCT-002
21. ACCT-003
22. ACCT-004
23. LOAD-003
24. LOAD-004
25. LOAD-005
26. TXN-001
27. TXN-002
28. TXN-003
29. TXN-004
30. XFER-001
31. XFER-002
32. RPT-001
33. RPT-002
34. RPT-003
35. CLI-004
36. VERIFY-001

Constraints:
- Test runner (FOUNDATION-005) precedes every other story's test slice.
- Validation (VALID-*) precedes every story that accepts input.
- Schema (SCHEMA-001) precedes every story that reads or writes a table.
- INTEG-002 precedes every balance-changing story (TXN-003, TXN-004, XFER-001, LOAD-003, LOAD-004).
- LOAD-001 and LOAD-002 precede LOAD-003, because transactions reference accounts and categories.
- TXN-001 precedes XFER-001, because transfers reuse the posting path.
- Reports depend on loaded and posted data, so RPT-* follow the mutating stories.
- Persistence is built before any command: FOUNDATION-002 and FOUNDATION-003 precede all data stories.

### Source Conflicts and Gaps

Resolved under the unattended policy; none is a blocker or questionnaire.

- DATABASE.md is cited by the brief but not supplied. The Database table in sources/INSTRUCTIONS.md is treated as the schema. The relational layer is generated from that table.
- The "shipped persistence library" is not supplied. The Target builds that library as part of FOUNDATION-003.
- Rigging `sqlalchemy.md` says it is superseded for Target persistence by the generated package. The stack rule for Python relational persistence requires SQLAlchemy and Alembic rows. The resolution is: the generated relational layer is the only data-access path, and SQLAlchemy and Alembic are recorded as selected dependencies with that constraint in their notes.
- Header mismatch in a load is treated as an invalid file row (exit 3). An unreadable file is an operational failure (exit 1).
- Help text is written to standard output with exit 0 and is exempt from the CSV rule.
- No authentication is built. The sources describe a single-user local tool with no protected resource.

## Analysis Notes
generated: 2026-10-20
blueprint: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/workspace/targets/LayersTesting/blueprint

Quality: Ready
  blockers: 0
  questions: 0
  features: 11
  stories: 36
  stack: Python 3.11+ over SQLite; PostgreSQL when DATABASE_URL is a PostgreSQL DSN
  display_name: not proposed
  short_description: not proposed

Observations:
- Unattended UAT policy in effect. No questionnaires, questions, or blockers were emitted. Each ambiguity is resolved as described under Source Conflicts and Gaps.
- DISPLAY_NAME and SHORT_DESCRIPTION are already set, so no identity questionnaire is emitted.
- COMPASS.md exists and is not pending format, so no COMPASS block is emitted.
- Delete commands (`account delete`, `txn delete`) write a two-line CSV: header `deleted`, then the code or id. This follows the output convention and is taken from run.sh checks E7 and F8.
- Amount `0` is rejected on input; output `0.00` is allowed on reports.
- Amount `1.234` (more than two decimals) is rejected with exit 3, per run.sh F6.
- Posted ids are reused after deletion (run.sh F8 then F10): the next post takes the largest present id plus one.
- Story count is 36, below the 80-story threshold; no story-count questionnaire is needed.
