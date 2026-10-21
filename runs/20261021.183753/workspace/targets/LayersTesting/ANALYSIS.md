# Blueprint Analysis: LayersTesting

## Commander Expectations

- assert every ledger command either completes in full or changes nothing
- assert every report is computed from the database and never from a stored answer
- assert the supplied grader `sources/run.sh` exits zero on the completed ledger
- assert amounts are stored as integer cents and written with exactly two decimal places
- assert the ledger is a command-line executable named `ledger` at the application root

## Crew

| Crew | Charge |
|---|---|
| Commander | Defines intent and decides what done means. |
| Team Lead | Confirms epic completeness and stakeholder expectations. |
| Planning Crew | Authors atomic specifications and the ordered Manifest. |
| Shipyard Crew | Builds the tickets without synchronous Commander access. |

## Story List

### Feature: Persistence and Schema

| ID | Story | High-level AC |
|---|---|---|
| PERSIST-001 | Select the database from configuration | `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`; a PostgreSQL DSN or SQLite path is accepted. |
| PERSIST-002 | Initialize an empty schema | `init` drops and recreates `accounts`, `categories`, and `transactions`, then writes nothing. |
| PERSIST-003 | Count rows per table | `count` writes `table,rows` then the three tables in order. |

### Feature: Bulk Loading

| ID | Story | High-level AC |
|---|---|---|
| LOAD-001 | Load accounts from a CSV file | The 4 seed accounts load; output is `table,loaded` then `accounts,N`; a duplicate key is rejected. |
| LOAD-002 | Load categories from a CSV file | The 7 seed categories load; output follows the same shape. |
| LOAD-003 | Load transactions with reference and rule checks | The 120 seed transactions load keeping `txn_id`; an unknown account or category, or any rule breach, stores none of the file. |

### Feature: Accounts

| ID | Story | High-level AC |
|---|---|---|
| ACCT-001 | Add an account | `account add` writes the new account row; a duplicate code or invalid field exits 3. |
| ACCT-002 | Get an account | `account get` writes the account row with its transaction count and balance; an absent code exits 4. |
| ACCT-003 | Rename an account | `account rename` writes the updated row; an absent code exits 4. |
| ACCT-004 | Delete an account when unused | `account delete` writes `deleted` and the code; an account with transactions exits 3; an absent code exits 4. |

### Feature: Transactions

| ID | Story | High-level AC |
|---|---|---|
| TXN-001 | Post a transaction with the next id | `txn post` assigns the largest `txn_id` plus one, or 1 in an empty table, and writes the new row. |
| TXN-002 | Get a transaction | `txn get` writes the transaction row; an absent id exits 4. |
| TXN-003 | Amend a transaction amount | `txn amend` changes only the amount and writes the updated row; an absent id exits 4. |
| TXN-004 | Delete a transaction | `txn delete` writes `deleted` and the id; an absent id exits 4. |

### Feature: Transfers

| ID | Story | High-level AC |
|---|---|---|
| XFER-001 | Transfer between two accounts atomically | `transfer` stores two `TRANSFER` rows, outgoing then incoming, or neither; both are written with the required memos. |

### Feature: Business Rules

| ID | Story | High-level AC |
|---|---|---|
| RULE-001 | Reject any change that would leave a balance negative | Post, amend, delete, transfer, and load each check every affected balance before the first write and exit 3 on breach. |
| RULE-002 | Validate codes, names, descriptions, and memos | Codes are 1 to 12 characters of `A-Z` and `0-9`; names and descriptions are 1 to 40 characters; memos are 0 to 60 characters; none contains a comma or newline. |
| RULE-003 | Parse and store amounts as integer cents | Input matches `-?DIGITS[.D[D]]` and is non-zero; output has two decimals, a leading `-` when negative, and no separator. |
| RULE-004 | Validate calendar dates | Dates match `YYYY-MM-DD` and name a real day; `2026-02-30` is rejected. |

### Feature: Reports

| ID | Story | High-level AC |
|---|---|---|
| RPT-001 | Balances report | `report balances` writes one row per account by code and a `TOTAL,,<count>,<sum>` row. |
| RPT-002 | Categories report | `report categories` writes every category by code, including those with no transactions, and a TOTAL row. |
| RPT-003 | Monthly report | `report monthly` writes one row per `YYYY-MM` with transactions, ascending, and a TOTAL row. |

### Feature: Command Line Interface

| ID | Story | High-level AC |
|---|---|---|
| CLI-001 | Dispatch commands and reject usage errors | Unknown commands, tables, reports, and wrong argument counts exit 2 with nothing on standard output. |
| CLI-002 | Report outcomes with exit codes and stderr diagnostics | Success writes CSV to standard output; each failure writes one diagnostic line to standard error and exits with its code. |
| CLI-003 | Provide help text for every command | `ledger help` and `ledger <command> --help` print usage for every command and sub-verb to standard error and exit 0. |

### Feature: Test Suite and Delivery

| ID | Story | High-level AC |
|---|---|---|
| TEST-001 | Provide the ledger executable at the application root | An executable named `ledger` exists at the application root and dispatches to the command modules. |
| TEST-002 | Provide the bin/test.sh automated test suite | `bin/test.sh` runs the pytest suite against a temporary database and exits zero only when every test passes. |
| TEST-003 | Pass the full conformance grader | Terminal gate: runs `sources/run.sh` unfiltered and records its exit status and summary line. |

## Story Guidance

Named stories planning must produce. Authoritative record: `STORY_GUIDANCE.json`.

None.

## Surfaced Acceptance Criteria

| ID | Story ID | Criterion |
|---|---|---|
| AC-001 | PERSIST-001 | When `DATABASE_URL` is unset, the application shall use `DATABASE_PATH`, and when that is also unset, `data/app.db` relative to the application root. |
| AC-002 | PERSIST-001 | When `DATABASE_URL` begins `postgres://` or `postgresql://`, the application shall treat it as a PostgreSQL DSN; otherwise it shall treat the value, with any `sqlite://` prefix removed, as a SQLite file path. |
| AC-003 | PERSIST-001 | While a command runs, the application shall rely on the database's own transactions so that each command completes in full or changes nothing. |
| AC-004 | LOAD-001 | If a load file's header does not match the table's columns in order, then the application shall exit 3 and change nothing. |
| AC-005 | LOAD-002 | When a load file has a header and no data rows, the application shall report zero loaded rows and exit 0. |
| AC-006 | LOAD-003 | If a loaded transaction's `txn_id` already exists, then the application shall exit 3 and change nothing. |
| AC-007 | LOAD-001 | When a load appends to a non-empty table, the application shall keep existing rows and add the new rows, rejecting the whole file on any key collision. |
| AC-008 | TXN-001 | When a post omits the memo, the application shall store an empty memo. |
| AC-009 | TXN-003 | When an amend runs, the application shall change only the amount and leave date, account, category, and memo unchanged. |
| AC-010 | TXN-004 | The application shall permit amending or deleting one leg of a transfer without its pair, subject to the non-negative balance rule. |
| AC-011 | XFER-001 | If the transfer amount is zero or negative, or the two accounts are equal, then the application shall exit 3 and change nothing. |
| AC-012 | RULE-002 | If a code contains a character outside `A-Z` and `0-9`, then the application shall exit 3. |
| AC-013 | RULE-003 | If an input amount is zero, including `-0.00`, then the application shall exit 3. |
| AC-014 | RULE-004 | The application shall accept a date only when it matches `YYYY-MM-DD` and names a real calendar day, including leap days. |
| AC-015 | RPT-001 | When no accounts exist, the application shall write the balances header and a `TOTAL,,0,0.00` row. |
| AC-016 | RPT-002 | When no transactions exist, the application shall list every category with zero counts and `0.00` values, then a zero TOTAL row. |
| AC-017 | RPT-003 | When no transactions exist, the application shall write the monthly header and a `TOTAL,0,0.00,0.00,0.00` row. |
| AC-018 | CLI-003 | When help is requested by `ledger help` or `ledger <command> --help`, the application shall print usage to standard error and exit 0. |
| AC-019 | TEST-003 | The terminal gate shall run `sources/run.sh` unfiltered and report its exit status and summary line. |

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
| sources/INSTRUCTIONS.md | instruction-to-test | sources/run.sh | "Run Harness" names `run.sh` as the scoring entry point, with checks A1 to Z2 | Every command's exit code and standard output must match the grader. |
| sources/run.sh | test-kit-to-implementation | ledger executable | `LEDGER="$APP/ledger"` invoked for every check | The executable at the application root is a prerequisite for every story. |
| sources/run.sh | dependency | sources/seed_accounts.csv, sources/seed_categories.csv, sources/seed_transactions.csv | `SEED` path resolves to the staged `sources/` directory | The seed files must be staged under `sources/` beside `run.sh`. |
| sources/seed_transactions_bad.csv | fixture-to-verification | LOAD-003, RULE-001 | Checks D1 and D3; row 11 names unknown account `NOSUCH` | The rejected-load story needs this fixture staged. |
| sources/seed_transactions.csv | fixture-to-verification | LOAD-003, RPT-001 to RPT-003 | Checks B3, C1 to C3, H1 to H3 | Report stories depend on a successful transaction load. |
| sources/INSTRUCTIONS.md (Database) | dependency | shipped persistence library | "reached only through the shipped persistence library" | Every persistence and command story depends on the library boundary. |
| sources/INSTRUCTIONS.md (Tests) | instruction-to-test | bin/test.sh | "POSIX-compatible `bin/test.sh`" | TEST-002 owns the application's own suite. |
| sources/INSTRUCTIONS.md (Rules) | parser-to-normalizer | RULE-003, RULE-004 | Amount and date rules feed every command that accepts them | RULE-003 and RULE-004 precede the write stories. |

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

The system is a single command-line executable, `ledger`, at the application root. It reads commands and CSV files, writes CSV results to standard output, and persists three relational tables (`accounts`, `categories`, `transactions`) through the shipped persistence library. Each command is all-or-nothing: it validates every input and rule, then writes, or it changes nothing. Inputs are command arguments and CSV seed files. Outputs are CSV on standard output, a diagnostic on standard error, and an exit code.

### Story Realization Map

- **PERSIST-001**: capability. Database selection by `DATABASE_URL`, `DATABASE_PATH`, default. Evidence: sources/INSTRUCTIONS.md "Database". Related: the persistence library and every command.
- **PERSIST-002**: capability with migration-free schema. Drop-and-create of three tables. Evidence: sources/INSTRUCTIONS.md Commands `init`; run.sh A1, Z1. Related: PERSIST-003, LOAD-*.
- **PERSIST-003**: capability. Row counts. Evidence: run.sh A2, B4, D3, G6, Z2. Related: PERSIST-002.
- **LOAD-001**: integration (file read) and capability. Accounts load. Evidence: run.sh B1, D2, E-series; INSTRUCTIONS.md Commands `load`. Related: sources/seed_accounts.csv.
- **LOAD-002**: integration and capability. Categories load. Evidence: run.sh B2; sources/seed_categories.csv. Related: TXN-001 (category references).
- **LOAD-003**: integration with atomic rule. Transactions load with reference and balance checks. Evidence: run.sh B3, D1, D3; sources/seed_transactions.csv and seed_transactions_bad.csv. Related: RULE-001, RULE-003, RULE-004.
- **ACCT-001**: capability. Account add. Evidence: run.sh E1, E2. Related: LOAD-001, RULE-002.
- **ACCT-002**: capability. Account get with transaction count and balance. Evidence: run.sh E3, E5, E8. Related: RPT-001.
- **ACCT-003**: capability. Account rename. Evidence: run.sh E4. Related: ACCT-002.
- **ACCT-004**: capability with in-use guard. Account delete. Evidence: run.sh E6, E7, E8. Related: TXN-001, LOAD-003.
- **TXN-001**: capability. Post with next id. Evidence: run.sh F1, F5 to F7, F10. Related: RULE-001, RULE-003, RULE-004.
- **TXN-002**: capability. Transaction get. Evidence: run.sh F2, F4, F9. Related: TXN-001.
- **TXN-003**: capability. Amend amount only. Evidence: run.sh F3, G4. Related: RULE-001.
- **TXN-004**: capability. Transaction delete. Evidence: run.sh F8, G5. Related: RULE-001.
- **XFER-001**: capability with atomic paired write. Transfer. Evidence: run.sh G1, G2; INSTRUCTIONS.md "transfer". Related: RULE-001, TXN-001.
- **RULE-001**: capability cross-cutting over all write stories. Non-negative balance check. Evidence: INSTRUCTIONS.md Rule 2; run.sh G3 to G5. Related: TXN-003, TXN-004, XFER-001, LOAD-003.
- **RULE-002**: capability. Field validation. Evidence: INSTRUCTIONS.md Rules 3 and 4. Related: ACCT-001, TXN-001.
- **RULE-003**: capability. Amount parsing and formatting. Evidence: INSTRUCTIONS.md Rule 5; run.sh F6. Related: every amount-bearing story.
- **RULE-004**: capability. Date validation. Evidence: INSTRUCTIONS.md Rule 6; run.sh F7. Related: TXN-001, XFER-001.
- **RPT-001**: capability. Balances report. Evidence: run.sh C1, H1. Related: LOAD-003, TXN-001.
- **RPT-002**: capability. Categories report. Evidence: run.sh C2, H2. Related: LOAD-002.
- **RPT-003**: capability. Monthly report. Evidence: run.sh C3, H3. Related: TXN-001.
- **CLI-001**: capability. Dispatch and usage errors. Evidence: INSTRUCTIONS.md Exit codes 2; run.sh U1, U2. Related: TEST-001.
- **CLI-002**: capability. Output and exit-code contract. Evidence: INSTRUCTIONS.md Output and Exit codes. Related: every command story.
- **CLI-003**: capability. Help text. Evidence: Core Baseline `cli` check. Related: CLI-001.
- **TEST-001**: integration. Executable at application root. Evidence: run.sh preamble and missing-executable check. Related: CLI-001.
- **TEST-002**: test harness. Application's pytest suite run by `bin/test.sh`. Evidence: INSTRUCTIONS.md Tests and Stack. Related: every implementation story.
- **TEST-003**: acceptance contract. Terminal gate running the unfiltered grader. Evidence: INSTRUCTIONS.md Run Harness; run.sh. Related: all other stories.

### Test and Acceptance Strategy

- Each feature story is verified by its own pytest tests, run through `bin/test.sh`, and declares `Suite: scoped`. Each feature story runs only the slice it owns.
- `sources/run.sh` accepts no pattern or number selector, so no feature story runs it. Feature stories must not use it as a scoped gate.
- TEST-003 is the single terminal verification story. It depends on every other story and declares `Suite: full`. It runs `sources/run.sh` unfiltered. The full-suite proof is `st-001`.
- Story-level tests use a real temporary SQLite database, one per test, created through `init`.
- A sample proves a unit works. It never proves the project is correct; only TEST-003 and `st-001` do.

### Sequencing and Dependencies

- TEST-001 (executable skeleton) and CLI-001 (dispatch) come first; every other story depends on them.
- PERSIST-001 precedes PERSIST-002, which precedes PERSIST-003 and every LOAD story.
- RULE-002, RULE-003, and RULE-004 precede ACCT-001, TXN-001, XFER-001, and LOAD-003, because each depends on the validators.
- LOAD-001 and LOAD-002 precede LOAD-003, which precedes RULE-001 enforcement against seeded balances.
- ACCT-002 and ACCT-004 depend on TXN-001 and LOAD-003 for the in-use check.
- RPT-001 to RPT-003 depend on LOAD-003 and TXN-001.
- TXN-003, TXN-004, and XFER-001 depend on RULE-001.
- CLI-002 and CLI-003 depend on every command story for their output contract.
- TEST-002 depends on every implementation story. TEST-003 depends on TEST-002.
- External dependency: the shipped persistence library. Its existence is an input assumption from the sources.

### Source Conflicts and Gaps

No cross-source conflicts were found. `pytest` runs inside `bin/test.sh`, which is consistent with the Tests section. The gaps below were resolved for planning by the narrowest reading consistent with the sources. No questionnaire was emitted, per the unattended UAT policy.

- **Transfer rejection**: a transfer whose amount is zero or negative, or whose accounts are equal, exits 3 and changes nothing.
- **Zero amount**: "never zero" is read as no zero input amount. `0`, `0.00`, and `-0.00` exit 3.
- **Code case**: codes accept uppercase `A-Z` and digits only. Lowercase exits 3.
- **Memo omitted**: stored as an empty memo.
- **Default database path**: `data/app.db` is resolved relative to the application root.
- **`sqlite://` prefix**: the remainder of the value is the file path.
- **Load header mismatch**: exits 3. A header-only file loads zero rows and exits 0. An unreadable file exits 1. Loads append and reject the whole file on any key collision.
- **Empty-database reports**: the balances report writes a zero TOTAL row. The categories report lists every seeded category with zero values. The monthly report writes a zero TOTAL row.
- **Help output**: `ledger help` and `ledger <command> --help` write usage to standard error and exit 0, so standard output stays CSV-only.
- **Transfer legs**: amending or deleting one leg of a transfer is permitted, subject to the balance rule. Pairing is not enforced. Posting with category `TRANSFER` directly is permitted.
- **Concurrency**: each command relies on the database's own transactions. No application-level locking is added.
- **Authentication**: none stated. The CLI trusts the operator who can reach the database. No auth layer is built.
- **Timeouts**: no value stated. An unreachable database fails immediately with exit 1 and changes nothing.
- **Deployment**: the ledger runs as a local executable from the application root.
- **Stack rule**: the Python relational-persistence rule requires the SQLAlchemy and Alembic rows. Both are recorded in `TECHNOLOGY_STACK.md` with notes.

## Analysis Notes
generated: 2026-10-21
blueprint: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261021.183753/workspace/targets/LayersTesting/blueprint

Quality: Ready
  blockers: 0
  questions: 0
  features: 9
  stories: 28
  stack: Python 3.11 or newer over SQLite, with pytest and POSIX sh
  display_name: not proposed
  short_description: not proposed

Observations:
- Unattended UAT policy applied. No Commander is available, so no questionnaire or blocker was emitted. Every ambiguity is resolved in the Source Conflicts and Gaps section above.
- `SEA_TRIALS.md` criteria `st-001` to `st-009` keep their prior IDs and titles. Their prior `Testability` and `Consequence` fields are not in the emitted shape and are not carried.
- `sources/run.sh` has no pattern or number selector. Scoped gates therefore use pytest selectors over the application's own tests.
- No `STORY_GUIDANCE.json` was emitted. The grader groups its checks by letter, but it exposes no runner selector a story gate could use.
- The story count (28) is below the 80-story granularity threshold, so no story-count questionnaire applies.
