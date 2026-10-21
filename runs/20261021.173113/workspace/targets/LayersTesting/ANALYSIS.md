# Blueprint Analysis: drydock Layers Testing Uat Case

## Commander Expectations

- assert the product is an executable named `ledger` at the application root
- assert every command either completes in full or changes nothing
- assert no command leaves any account balance below zero
- assert every report is computed from the database and matches the known answers in `sources/run.sh`
- assert the supplied grader `sources/run.sh` exits zero against the completed application

## Crew

| Crew | Charge |
|---|---|
| Commander | Defines intent and decides what done means. |
| Team Lead | Confirms epic completeness and stakeholder expectations. |
| Planning Crew | Authors atomic specifications and the ordered Manifest. |
| Shipyard Crew | Builds the tickets without synchronous Commander access. |

## Story List

### Feature: CLI Foundation

| ID | Story | High-level AC |
|---|---|---|
| CLI-001 | Ledger executable and command dispatch | `ledger` exists at the application root, is executable, and dispatches every command in the Commands table; successes print CSV to standard output. |
| CLI-002 | Usage errors and command help | Unknown command, unknown table or report, or wrong argument count exits 2 with no standard output; each command and sub-verb has help text. |
| CLI-003 | Database location and persistence boundary | `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db` selects the store; all database access goes through the persistence library. |

### Feature: Schema Lifecycle

| ID | Story | High-level AC |
|---|---|---|
| SCHEMA-001 | Initialize empty schema | `init` drops and recreates `accounts`, `categories`, and `transactions` empty and writes nothing. |
| SCHEMA-002 | Row count report | `count` prints `table,rows` then the `accounts`, `categories`, and `transactions` rows in that order. |
| SCHEMA-003 | Relational schema and keys | The three tables carry the columns, primary keys, and references in the Database table; amounts are stored as integer cents. |

### Feature: Bulk Load

| ID | Story | High-level AC |
|---|---|---|
| LOAD-001 | Load accounts | A file whose header matches `account,name` loads into `accounts`, writes `table,loaded` and `accounts,N`, and exits 1 when the file is unreadable. |
| LOAD-002 | Load categories | A file whose header matches `category,description` loads into `categories` with the same output and exit behavior as LOAD-001. |
| LOAD-003 | Load transactions | A file whose header matches the transaction columns loads with `txn_id` kept from the file; unknown account or category, and any invalid row, exits 3. |
| LOAD-004 | Atomic rejected load | A load containing any rejected row stores none of its rows, reports exit 3, and leaves all tables unchanged. |

### Feature: Account Management

| ID | Story | High-level AC |
|---|---|---|
| ACCOUNT-001 | Add account | `account add` inserts the row and prints it with `0` transactions and `0.00`; a duplicate code exits 3. |
| ACCOUNT-002 | Get account | `account get` prints the account row with its transaction count and balance; an absent code exits 4. |
| ACCOUNT-003 | Rename account | `account rename` changes only the name and prints the updated row; an absent code exits 4 and an invalid name exits 3. |
| ACCOUNT-004 | Delete account | `account delete` prints `deleted` and the code when the account has no transactions; an account in use exits 3 and an absent code exits 4. |

### Feature: Transaction Management

| ID | Story | High-level AC |
|---|---|---|
| TXN-001 | Post transaction | `txn post` assigns one more than the largest `txn_id` (or `1`), prints the new row, and rejects invalid input with exit 3. |
| TXN-002 | Get transaction | `txn get` prints the transaction row; an absent id exits 4. |
| TXN-003 | Amend transaction amount | `txn amend` changes only the amount, prints the updated row, refuses a negative balance with exit 3, and exits 4 for an absent id. |
| TXN-004 | Delete transaction | `txn delete` prints `deleted` and the id, refuses a negative balance with exit 3, and exits 4 for an absent id. |

### Feature: Transfers

| ID | Story | High-level AC |
|---|---|---|
| TRANSFER-001 | Post paired transfer | `transfer` writes two rows in category `TRANSFER`: the outgoing row takes the next id and the incoming row the id after it; both are printed. |
| TRANSFER-002 | Reject invalid transfer | A non-positive amount, identical accounts, an unknown account, or a resulting negative balance exits 3 and writes neither row. |

### Feature: Input Rules

| ID | Story | High-level AC |
|---|---|---|
| RULES-001 | Amount parsing and formatting | Input matches `-?DIGITS[.D[D]]` with no zero amount; output has exactly two decimals, a leading `-` when negative, and no separator. |
| RULES-002 | Code, name, and memo validation | Codes are 1 to 12 characters from `A-Z` and `0-9`; names are 1 to 40 characters; memos are 0 to 60 characters; none contains a comma or newline. |
| RULES-003 | Calendar date validation | Dates are `YYYY-MM-DD` and must be real calendar dates; `2026-02-30` is rejected with exit 3. |
| RULES-004 | Non-negative balance check | Posting, amending, deleting, transferring, and loading each check every resulting balance before the first write and refuse any negative balance with exit 3. |

### Feature: Reports

| ID | Story | High-level AC |
|---|---|---|
| REPORT-001 | Balances report | `report balances` lists each account by code as `account,name,transactions,balance` followed by `TOTAL,,<count>,<sum>`. |
| REPORT-002 | Categories report | `report categories` lists every category by code, including those with no transactions, followed by the `TOTAL` row with inflow, outflow, and net. |
| REPORT-003 | Monthly report | `report monthly` lists each `YYYY-MM` with transactions in ascending order followed by the `TOTAL` row. |

### Feature: Verification

| ID | Story | High-level AC |
|---|---|---|
| VERIFY-001 | Automated test suite | `bin/test.sh` is POSIX-compatible, runs against a real temporary database covering each command, exit code, and rule, and exits zero only when every test passes. |
| VERIFY-002 | Grader acceptance gate | `sh sources/run.sh` exits zero against the completed application root; this is the terminal story and depends on every implementation story. |

## Story Guidance

Named stories planning must produce. Authoritative record: `STORY_GUIDANCE.json`.

| Story ID | Provenance | Gate | Note |
|---|---|---|---|
| SCHEMA-001 | plan | — | sources/run.sh section A (A1) and Z (Z1): init drops and recreates empty tables. |
| SCHEMA-002 | plan | — | sources/run.sh section A (A2) and B4, D3, G6, Z2: count output. |
| LOAD-001 | plan | — | sources/run.sh section B (B1) and D (D2): accounts load and rejected reload. |
| LOAD-002 | plan | — | sources/run.sh section B (B2): categories load. |
| LOAD-003 | plan | — | sources/run.sh section B (B3) and D (D1): transactions load and rejected bad batch. |
| LOAD-004 | plan | — | sources/run.sh section D: a rejected load changes nothing. |
| ACCOUNT-001 | plan | — | sources/run.sh section E (E1, E2): account add and duplicate rejection. |
| ACCOUNT-002 | plan | — | sources/run.sh section E (E3, E5, E8): account get and absent account. |
| ACCOUNT-003 | plan | — | sources/run.sh section E (E4): account rename. |
| ACCOUNT-004 | plan | — | sources/run.sh section E (E6, E7): account delete refusal and deletion. |
| TXN-001 | plan | — | sources/run.sh section F (F1, F5, F6, F7, F10): transaction post and rejections. |
| TXN-002 | plan | — | sources/run.sh section F (F2, F4): transaction get and absent id. |
| TXN-003 | plan | — | sources/run.sh section F (F3): transaction amend. |
| TXN-004 | plan | — | sources/run.sh section F (F8, F9): transaction delete and absent id. |
| TRANSFER-001 | plan | — | sources/run.sh section G (G1): paired transfer. |
| TRANSFER-002 | plan | — | sources/run.sh section G (G2): rejected transfer. |
| RULES-001 | plan | — | sources/run.sh section F (F6): amount format and rejection. |
| RULES-002 | plan | — | INSTRUCTIONS.md Rules 3 and 4: code, name, and memo validation. |
| RULES-003 | plan | — | sources/run.sh section F (F7): invalid calendar date. |
| RULES-004 | plan | — | sources/run.sh section G (G3, G4, G5): non-negative balance checks. |
| REPORT-001 | plan | — | sources/run.sh sections C (C1) and H (H1): balances report. |
| REPORT-002 | plan | — | sources/run.sh sections C (C2) and H (H2): categories report. |
| REPORT-003 | plan | — | sources/run.sh sections C (C3) and H (H3): monthly report. |
| CLI-002 | plan | — | sources/run.sh section U (U1, U2): usage errors. |
| VERIFY-002 | plan | — | sources/run.sh as a whole: the terminal full-suite gate. |

## Surfaced Acceptance Criteria

| ID | Story ID | Criterion |
|---|---|---|
| AC-001 | CLI-002 | Every command and sub-verb in the Commands table has help text defined in the application. |
| AC-002 | CLI-003 | A `DATABASE_URL` beginning `postgres://` or `postgresql://` is classified as a PostgreSQL DSN and never treated as a file path. |
| AC-003 | LOAD-001 | A file with a matching header and no data rows loads zero rows, writes `accounts,0` after `table,loaded`, and exits 0. |
| AC-004 | REPORT-001 | With no accounts, `report balances` prints the header and `TOTAL,,0,0.00`. |
| AC-005 | REPORT-002 | A category with no transactions shows `0`, `0.00`, `0.00`, and `0.00` in its transactions, inflow, outflow, and net columns. |

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
| `sources/run.sh` | test-kit-to-implementation | `./ledger` at the application root | Checks A1 to Z2 invoke each command and compare exit code and stdout | The grader is the terminal gate for every implementation story. |
| `sources/run.sh` | dependency | `sources/seed_accounts.csv`, `seed_categories.csv`, `seed_transactions.csv` | Checks B1 to B3 load these files by path from the harness directory | The seed files must be staged alongside the harness. |
| `sources/run.sh` | dependency | `sources/seed_transactions_bad.csv` | Check D1 expects exit 3 from loading this file | The bad batch must be staged. |
| `sources/seed_transactions.csv` | dependency | `seed_accounts.csv`, `seed_categories.csv` | Every row references an account and category code | Load accounts and categories before transactions (LOAD-001 to LOAD-003). |
| `sources/seed_transactions_bad.csv` | fixture-to-rule | `sources/INSTRUCTIONS.md` Rule 1 | Row 211 names unknown account `NOSUCH` | Covered by LOAD-004 atomic rejection. |
| `sources/INSTRUCTIONS.md` | instruction-to-test | `sources/run.sh` | Commands table, exit-code table, and output rules match every check's expected output | VERIFY-002 proves the instruction contract. |
| `sources/INSTRUCTIONS.md` | instruction-to-test | `bin/test.sh` (to be authored) | Tests section requires coverage of each command, exit code, and rule | VERIFY-001 authors the suite. |

## Source Roles

| Path | Role | Plan disposition | Build disposition |
|---|---|---|---|
| `sources/INSTRUCTIONS.md` | author intent | compass | prompt-only |
| `sources/run.sh` | conformance harness | context | stage |
| `sources/seed_accounts.csv` | asset | context | stage |
| `sources/seed_categories.csv` | asset | context | stage |
| `sources/seed_transactions.csv` | asset | context | stage |
| `sources/seed_transactions_bad.csv` | asset | context | stage |

## Planning Instructions

### Delivery Shape

The system is a single-user command-line program named `ledger`, implemented in Python 3.11 or newer over SQLite. Inputs are command-line arguments and three CSV seed files. Outputs are CSV on standard output on success, a single diagnostic line on standard error on failure, and rows in the database.

Execution flow: every command resolves the database location, validates every input and rule, checks the non-negative balance rule, and only then performs its writes. Rejected commands write nothing.

Repository-call contracts, all with consumer sensitivity `data` (CLI consumer):

- `FEATURE-LOAD-001`: insert validated rows into `accounts`, `categories`, or `transactions`; input is a parsed file; output is the loaded count.
- `FEATURE-ACCOUNT-001`: add, get, rename, and delete an account row; output is the account row with its count and balance.
- `FEATURE-TRANSACTION-001`: post, get, amend, and delete a transaction row, and return the next free `txn_id`.
- `FEATURE-REPORT-001`: aggregate reads over accounts, categories, and transactions for the three reports.

### Story Realization Map

| Story ID | Durable scope | Cited evidence | Requires |
|---|---|---|---|
| CLI-001 | Entry point and dispatch for all commands | Commands table; `sources/run.sh` check A1 | capability |
| CLI-002 | Exit 2 usage errors and help text | Exit codes table; `sources/run.sh` checks U1, U2 | capability |
| CLI-003 | Database location and persistence boundary | Database section; `sources/run.sh` header comment | integration |
| SCHEMA-001 | `init` drop and recreate | Commands table; `sources/run.sh` checks A1, Z1 | migration-free schema build, acceptance contract |
| SCHEMA-002 | `count` output | Commands table; `sources/run.sh` checks A2, B4, D3, G6, Z2 | capability |
| SCHEMA-003 | Table definitions and keys | Database table; Rule 7 | capability |
| LOAD-001 | Accounts load | Commands table; `sources/run.sh` B1, D2; `seed_accounts.csv` | capability, fixture |
| LOAD-002 | Categories load | Commands table; `sources/run.sh` B2; `seed_categories.csv` | capability, fixture |
| LOAD-003 | Transactions load | Commands table; `sources/run.sh` B3, D1; `seed_transactions.csv`, `seed_transactions_bad.csv` | capability, fixture |
| LOAD-004 | Atomic all-or-nothing load | Rule 1; `sources/run.sh` D1, D2, D3 | capability, acceptance contract |
| ACCOUNT-001 | Account add | `sources/run.sh` E1, E2 | capability |
| ACCOUNT-002 | Account get | `sources/run.sh` E3, E5, E8 | capability |
| ACCOUNT-003 | Account rename | `sources/run.sh` E4 | capability |
| ACCOUNT-004 | Account delete with in-use refusal | Commands table; `sources/run.sh` E6, E7, E8 | capability |
| TXN-001 | Transaction post and id assignment | Rule 7; `sources/run.sh` F1, F5, F6, F7, F10 | capability |
| TXN-002 | Transaction get | `sources/run.sh` F2, F4 | capability |
| TXN-003 | Transaction amend | `sources/run.sh` F3, G4 | capability |
| TXN-004 | Transaction delete | `sources/run.sh` F8, F9, G5 | capability |
| TRANSFER-001 | Paired transfer write | Commands table; `sources/run.sh` G1 | capability |
| TRANSFER-002 | Transfer rejection | `sources/run.sh` G2 | capability |
| RULES-001 | Amount codec | Rule 5; `sources/run.sh` F6 | capability |
| RULES-002 | Code, name, memo rules | Rules 3, 4 | capability |
| RULES-003 | Date rule | Rule 6; `sources/run.sh` F7 | capability |
| RULES-004 | Non-negative balance check | Rule 2; `sources/run.sh` G2, G3, G4, G5 | capability |
| REPORT-001 | Balances report | Commands table; `sources/run.sh` C1, H1 | capability |
| REPORT-002 | Categories report | Commands table; `sources/run.sh` C2, H2 | capability |
| REPORT-003 | Monthly report | Commands table; `sources/run.sh` C3, H3 | capability |
| VERIFY-001 | Bin test suite | Tests section; `sources/INSTRUCTIONS.md` | test harness |
| VERIFY-002 | Full grader gate | Run Harness section; `sources/run.sh` | acceptance contract, test harness |

### Test and Acceptance Strategy

Focused story tests run per feature. Each feature story declares `Suite: scoped` and runs only the `bin/test.sh` slice it owns; no feature story executes `sources/run.sh`, which has no scope selector.

VERIFY-002 declares `Suite: full` in its heading block. It runs `sh sources/run.sh` unfiltered as the single full-suite proof and depends on every implementation story. Its acceptance is exit zero with zero failed checks.

Final Sea Trial verification is recorded in `SEA_TRIALS.md`. The grader exit status is the sole acceptance verdict.

### Sequencing and Dependencies

- CLI-001 and CLI-003 precede every other story.
- SCHEMA-001 and SCHEMA-002 precede all load and mutation stories.
- LOAD-001 and LOAD-002 precede LOAD-003, because transactions reference accounts and categories.
- RULES-001 through RULES-003 precede any story that accepts their inputs.
- RULES-004 precedes TXN-001, TXN-003, TXN-004, TRANSFER-001, and LOAD-003 writes.
- ACCOUNT-001 precedes ACCOUNT-002 through ACCOUNT-004; ACCOUNT-004 requires the transaction table.
- TXN-001 precedes TXN-002 through TXN-004 and TRANSFER-001.
- All REPORT stories follow every write story, because their expected output depends on the seeded and mutated data.
- VERIFY-001 follows the implementation stories it covers; VERIFY-002 is last.

### Source Conflicts and Gaps

- No conflicting source definitions were found. Each command, exit code, and output rule is stated once in `sources/INSTRUCTIONS.md` and matched by `sources/run.sh`.
- The shipped persistence library and the relational layer generated from `DATABASE.md` are named by the sources but are not among the imported sources. Resolved behavior: the library is treated as available to the build through the persistence boundary in `persistence.md`, and CLI-003 owns the access layer.
- No deployment target is stated. Resolved behavior: a local command-line program run on the operator's machine, with SQLite as the default store.
- No concurrency model is described. Resolved behavior: single-process, single-user access; no concurrency requirements are authored.
- No authentication or sensitive-data handling is stated for a local ledger. Resolved behavior: none required.

## Analysis Notes
generated: 2026-10-21
blueprint: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261021.173113/workspace/targets/LayersTesting/blueprint

Quality: Ready
  blockers: 0
  questions: 0
  features: 9
  stories: 29
  stack: Python 3.11+ over SQLite; pytest
  display_name: not proposed
  short_description: not proposed

- Unattended UAT policy applied: no blockers and no questionnaires were emitted. Ambiguities were resolved by the narrowest behavior consistent with the sources, as recorded in Source Conflicts and Gaps.
- Stack rule conflict: the sources name the shipped persistence library and do not name SQLAlchemy or Alembic. The Python relational-persistence gate requires `sqlalchemy.md` and `alembic.md`, so both are selected in `TECHNOLOGY_STACK.md`. `sqlalchemy.md` is marked superseded for generated-package targets, so this selection should be reviewed.
- `sources/run.sh` is the conformance harness; VERIFY-002 is the single full-suite gate.
- Prior `SEA_TRIALS.md` criteria st-001 through st-009 are preserved with their stable IDs. st-010 is added for the source-stated prohibition on reading the grader and embedding answers.
- `STORY_GUIDANCE.json` is emitted because `sources/run.sh` is partitioned into lettered check groups. No gate is supplied because the harness takes no scope selector.
- Help text content is not specified in the sources; AC-001 requires only that help text exists.
- Empty-state behavior (AC-003 to AC-005) is derived from the stated rules and is not stated explicitly in the sources.
