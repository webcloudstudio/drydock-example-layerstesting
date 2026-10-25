# Blueprint Analysis: LayersTesting

## Commander Expectations

- assert the `ledger` executable at the application root passes the supplied grader `sources/run.sh`
- assert every command either completes in full or changes nothing
- assert every report is computed from the database and never embeds a known answer
- assert no command leaves any account balance below zero
- assert the application reaches the database only through the shipped persistence library, with amounts stored as integer cents

## Crew

| Crew | Charge |
|---|---|
| Commander | Defines intent and decides what done means. |
| Team Lead | Confirms epic completeness and stakeholder expectations. |
| Planning Crew | Authors atomic specifications and the ordered Manifest. |
| Shipyard Crew | Builds the tickets without synchronous Commander access. |

## Story List

features: 11
stories: 30

### Feature: Application Entry and Usage

| ID | Story | High-level AC |
|---|---|---|
| ENTRY-001 | Run `ledger` as an executable at the application root | `./ledger` dispatches each command and returns the exit code defined for it (0 to 4) |
| ENTRY-002 | Reject usage errors | An unknown command, report, or table, or a wrong argument count, exits 2 with no standard output |
| ENTRY-003 | Provide help text for every command and sub-verb | Each command and sub-verb has usage text available on a usage error |

### Feature: Database Selection

| ID | Story | High-level AC |
|---|---|---|
| STORE-001 | Select the database from `DATABASE_URL`, `DATABASE_PATH`, or the default file | Resolution follows the stated order; a PostgreSQL DSN or a SQLite path is accepted; an unreachable database exits 1 |

### Feature: Field Validation

| ID | Story | High-level AC |
|---|---|---|
| VALID-001 | Validate account and category codes | Codes are 1 to 12 characters from `A-Z` and `0-9`; an invalid code exits 3 |
| VALID-002 | Validate names and descriptions | Names and descriptions are 1 to 40 characters with no comma or newline; a violation exits 3 |
| VALID-003 | Validate memos | Memos are 0 to 60 characters with no comma or newline; a violation exits 3 |
| VALID-004 | Parse and format amounts | Input matches `-?DIGITS[.D[D]]`, is never zero, and is stored as integer cents; output has two decimals, a leading `-` when negative, and no thousands separator |
| VALID-005 | Validate calendar dates | Dates are real `YYYY-MM-DD` dates; `2026-02-30` exits 3 |

### Feature: Schema Lifecycle

| ID | Story | High-level AC |
|---|---|---|
| SCHEMA-001 | Initialize an empty schema | `init` drops and recreates the three tables empty and writes nothing |
| SCHEMA-002 | Count rows per table | `count` writes `table,rows` then the `accounts`, `categories`, and `transactions` counts |

### Feature: Bulk Loading

| ID | Story | High-level AC |
|---|---|---|
| LOAD-001 | Load accounts from a CSV file | A file whose header matches `account,name` loads, and the output is `table,loaded` then `accounts,<rows>` |
| LOAD-002 | Load categories from a CSV file | A file whose header matches `category,description` loads, and the output is `table,loaded` then `categories,<rows>` |
| LOAD-003 | Load transactions from a CSV file | A file whose header matches the transaction columns loads, keeps each file `txn_id`, and resolves account and category references |
| LOAD-004 | Reject a load as a whole when any row fails | A failing row stores none of the rows before it; duplicate keys exit 3; an unreadable file exits 1 |

### Feature: Account Maintenance

| ID | Story | High-level AC |
|---|---|---|
| ACCT-001 | Add an account | `account add` returns the new row with 0 transactions and balance `0.00` |
| ACCT-002 | Get an account | `account get` returns the row; an absent code exits 4 |
| ACCT-003 | Rename an account | `account rename` changes only the name and returns the updated row; an absent code exits 4 |
| ACCT-004 | Delete an account | `account delete` writes `deleted` and the code; an account with transactions exits 3; an absent code exits 4 |

### Feature: Transaction Ledger

| ID | Story | High-level AC |
|---|---|---|
| TXN-001 | Post a transaction | `txn post` assigns the next `txn_id` and returns the row; an unknown account or category exits 3 |
| TXN-002 | Get a transaction | `txn get` returns the row; an absent id exits 4 |
| TXN-003 | Amend a transaction amount | `txn amend` changes only the amount and returns the row; an absent id exits 4 |
| TXN-004 | Delete a transaction | `txn delete` writes `deleted` and the id; an absent id exits 4 |

### Feature: Transfers

| ID | Story | High-level AC |
|---|---|---|
| XFER-001 | Transfer between two accounts | `transfer` stores two `TRANSFER` rows, both or neither; the amount is positive and the accounts differ |

### Feature: Balance Protection

| ID | Story | High-level AC |
|---|---|---|
| BAL-001 | Reject any command that would leave a negative balance | Post, amend, delete, transfer, and load check the balance rule before their first write and exit 3 on violation |

### Feature: Reports

| ID | Story | High-level AC |
|---|---|---|
| RPT-001 | Report balances by account | Rows ordered by code, then `TOTAL,,<count>,<sum>` |
| RPT-002 | Report totals by category | Every category ordered by code, including those with no transactions, then the `TOTAL` row with inflow, outflow, and net |
| RPT-003 | Report totals by month | One row per `YYYY-MM` with transactions, ascending, then the `TOTAL` row |

### Feature: Verification

| ID | Story | High-level AC |
|---|---|---|
| TEST-001 | Provide the application test suite | `bin/test.sh` runs the automated suite against a real temporary database and exits zero only when every test passes |
| ACCEPT-001 | Pass the supplied grader end to end | `sh sources/run.sh` exits zero with every check passing; this terminal story gates on the complete suite |

## Story Guidance

Named stories planning must produce. Authoritative record: `STORY_GUIDANCE.json`.

| Story ID | Provenance | Gate | Note |
|---|---|---|---|
| SCHEMA-001 | plan | — | sources/run.sh sections A and Z: init creates an empty schema, and re-initialization drops every row |
| SCHEMA-002 | plan | — | sources/run.sh sections A2, B4, D3, G6, and Z2: count reports row counts per table |
| LOAD-001 | plan | — | sources/run.sh section B1: load accounts |
| LOAD-002 | plan | — | sources/run.sh section B2: load categories |
| LOAD-003 | plan | — | sources/run.sh section B3: load transactions |
| LOAD-004 | plan | — | sources/run.sh section D: rejected loads change nothing |
| RPT-001 | plan | — | sources/run.sh sections C1 and H1: balances report before and after changes |
| RPT-002 | plan | — | sources/run.sh sections C2 and H2: categories report before and after changes |
| RPT-003 | plan | — | sources/run.sh sections C3 and H3: monthly report before and after changes |
| ACCT-001 | plan | — | sources/run.sh section E: account add |
| ACCT-002 | plan | — | sources/run.sh section E: account get and absent account |
| ACCT-003 | plan | — | sources/run.sh section E: account rename |
| ACCT-004 | plan | — | sources/run.sh section E: account delete, refused while in use |
| TXN-001 | plan | — | sources/run.sh section F: transaction post |
| TXN-002 | plan | — | sources/run.sh section F: transaction get and absent id |
| TXN-003 | plan | — | sources/run.sh section F: transaction amend |
| TXN-004 | plan | — | sources/run.sh section F: transaction delete |
| XFER-001 | plan | — | sources/run.sh section G: atomic transfer |
| BAL-001 | plan | — | sources/run.sh section G: non-negative balance rule |
| ENTRY-002 | plan | — | sources/run.sh section U: usage errors |

## Surfaced Acceptance Criteria

| ID | Story ID | Criterion |
|---|---|---|
| AC-001 | ENTRY-003 | Each command and sub-verb has usage text that is written to standard error, with exit code 2, on a usage error for that command. |
| AC-002 | ENTRY-002 | Running `ledger` with no command writes usage text to standard error and exits 2 with no standard output. |
| AC-003 | LOAD-004 | A load whose file header does not match the table's columns in order is rejected with exit code 3 and stores no rows. |
| AC-004 | LOAD-004 | A load whose file cannot be read exits 1 and stores no rows. |
| AC-005 | RPT-001 | With no accounts, `report balances` writes the header and a `TOTAL` row with count 0 and balance `0.00`. |
| AC-006 | RPT-002 | With no categories, `report categories` writes the header and a `TOTAL` row with zero counts and `0.00` amounts. |
| AC-007 | RPT-003 | With no transactions, `report monthly` writes the header and a `TOTAL` row with count 0 and `0.00` amounts. |

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
| sources/run.sh | test-kit-to-implementation | `ledger` at the application root | The `check` function runs `"$APP/ledger"` for every check | The grader is the final verdict on the executable's exit codes and stdout |
| sources/run.sh | dependency | sources/seed_accounts.csv, sources/seed_categories.csv, sources/seed_transactions.csv, sources/seed_transactions_bad.csv | `SEED` resolves beside the harness; checks B1 to B3 and D1 to D2 load these files | The four seed files must be staged beside the harness, unchanged |
| sources/INSTRUCTIONS.md | instruction-to-test | sources/run.sh | The Commands table, Rules, and Exit codes mirror checks A to Z | Each command story's behavior follows the grader's expected output and exit code |
| sources/INSTRUCTIONS.md | dependency | sources/seed_*.csv | The "Read-only scoring assets" section gives the row counts of each file | Loads must accept the seed files as shipped |
| sources/seed_transactions_bad.csv | fixture-before-verification | sources/run.sh | Check D1 loads it and expects exit 3; row 211 names the unknown account `NOSUCH` | LOAD-004 must reject before any write |
| sources/seed_transactions.csv | dependency | sources/seed_accounts.csv, sources/seed_categories.csv | Transaction rows reference the account and category codes in the other two files | Accounts and categories load before transactions |

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

The system is a command-line cash ledger: one executable, `ledger`, at the application root, over a relational database. Inputs are CLI arguments and the CSV seed files. Outputs are CSV on standard output, one diagnostic line on standard error, and the exit codes 0 to 4. Every command validates its inputs and checks the balance rule before its first write, writes inside a single transaction, and then formats its output. The database is selected by `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`.

### Story Realization Map

| Story ID | Durable scope | Evidence | Related files | Kind |
|---|---|---|---|---|
| ENTRY-001 | `ledger` executable dispatching all commands | INSTRUCTIONS.md Objective, Run Harness; run.sh `check` | run.sh | capability |
| ENTRY-002 | Usage errors: exit 2, empty stdout | INSTRUCTIONS.md Exit codes; run.sh U1, U2 | run.sh | capability |
| ENTRY-003 | Help text per command and sub-verb | INSTRUCTIONS.md Commands; Core Baseline (cli) | none | capability |
| STORE-001 | Database selection by `DATABASE_URL`, `DATABASE_PATH`, default path | INSTRUCTIONS.md Database; run.sh sets `DATABASE_URL` | run.sh | integration |
| VALID-001 | Code validation | INSTRUCTIONS.md Rule 3; run.sh F5 | none | capability |
| VALID-002 | Name and description validation | INSTRUCTIONS.md Rule 4 | none | capability |
| VALID-003 | Memo validation | INSTRUCTIONS.md Rule 4 | none | capability |
| VALID-004 | Amount parsing, integer-cent storage, and output format | INSTRUCTIONS.md Rule 5, Database; run.sh F6 | none | capability |
| VALID-005 | Calendar date validation | INSTRUCTIONS.md Rule 6; run.sh F7 | none | capability |
| SCHEMA-001 | Schema init and re-init | INSTRUCTIONS.md Commands; run.sh A1, Z1 | run.sh | capability |
| SCHEMA-002 | Row counts per table | INSTRUCTIONS.md Commands; run.sh A2, B4, D3, G6, Z2 | run.sh | capability |
| LOAD-001 | Load accounts | INSTRUCTIONS.md Commands; run.sh B1; sources/seed_accounts.csv | seed_accounts.csv | capability |
| LOAD-002 | Load categories | INSTRUCTIONS.md Commands; run.sh B2; sources/seed_categories.csv | seed_categories.csv | capability |
| LOAD-003 | Load transactions keeping file `txn_id` | INSTRUCTIONS.md Rule 7; run.sh B3; sources/seed_transactions.csv | seed_transactions.csv | capability |
| LOAD-004 | Atomic rejected loads | INSTRUCTIONS.md Rule 1; run.sh D1, D2; sources/seed_transactions_bad.csv | seed_transactions_bad.csv | acceptance contract |
| ACCT-001 | Account add | INSTRUCTIONS.md Commands; run.sh E1, E2 | none | capability |
| ACCT-002 | Account get, absent exits 4 | INSTRUCTIONS.md Exit codes; run.sh E3, E5, E8 | none | capability |
| ACCT-003 | Account rename | INSTRUCTIONS.md Commands; run.sh E4 | none | capability |
| ACCT-004 | Account delete, refused while in use | INSTRUCTIONS.md Commands; run.sh E6, E7 | none | capability |
| TXN-001 | Transaction post | INSTRUCTIONS.md Rule 7, Commands; run.sh F1, F5, F10 | none | capability |
| TXN-002 | Transaction get | INSTRUCTIONS.md Commands; run.sh F2, F4, F9 | none | capability |
| TXN-003 | Transaction amend | INSTRUCTIONS.md Commands; run.sh F3 | none | capability |
| TXN-004 | Transaction delete | INSTRUCTIONS.md Commands; run.sh F8 | none | capability |
| XFER-001 | Atomic transfer | INSTRUCTIONS.md Rule 1, Commands; run.sh G1, G2 | none | capability |
| BAL-001 | Non-negative balance rule across writes | INSTRUCTIONS.md Rule 2; run.sh G3, G4, G5 | none | capability |
| RPT-001 | Balances report | INSTRUCTIONS.md Commands, Output; run.sh C1, H1 | none | capability |
| RPT-002 | Categories report | INSTRUCTIONS.md Commands, Output; run.sh C2, H2 | none | capability |
| RPT-003 | Monthly report | INSTRUCTIONS.md Commands, Output; run.sh C3, H3 | none | capability |
| TEST-001 | Application test suite via `bin/test.sh` | INSTRUCTIONS.md Tests; SEA_TRIALS st-002 | none | test harness |
| ACCEPT-001 | Complete grader run | INSTRUCTIONS.md Run Harness; run.sh | run.sh, seed files | acceptance contract |

### Test and Acceptance Strategy

Focused story tests live in `bin/test.sh` and run against a real temporary database. Each non-terminal story runs only its own slice of that suite and declares `Suite: scoped`. `sources/run.sh` accepts no `--pattern` or `--number` selector, so no bounded story runs it.

Final verification is one terminal story, ACCEPT-001. It depends on every implementation story, runs `sh sources/run.sh` unfiltered, and declares `Suite: full` in its heading block. Sea Trial st-001 is the proof for that run.

### Sequencing and Dependencies

- SCHEMA-001 precedes every other story, because each check begins with `init`.
- VALID-001 to VALID-005 precede every write story, because each write validates before storing.
- Loads of accounts and categories precede loads of transactions, because transactions reference both.
- BAL-001 precedes the post, amend, delete, transfer, and load stories that it constrains.
- Account delete (ACCT-004) depends on transaction storage (TXN-001).
- Reports (RPT-001 to RPT-003) follow the loads and writes whose totals they show.
- TEST-001 follows all implementation stories; ACCEPT-001 follows TEST-001.
- External dependency: a Python 3.11+ runtime, with SQLite available.

### Source Conflicts and Gaps

- Reading INSTRUCTIONS.md, run.sh, the seed files, and the existing SEA_TRIALS.md, I found no conflicting definitions of any product concept, and no source gives explicit precedence that would need a Commander decision. The sources do not state every expected total, and I did not recompute them here; run.sh is the authority for those values.
- Gaps resolved to the narrowest behavior consistent with the sources, with no questionnaire raised:
  - Help text content is not specified. Usage text is written to standard error on a usage error (AC-001).
  - Header mismatch on a load is not specified. It is rejected with exit 3 (AC-003).
  - Unreadable load files exit 1 (stated), and store nothing (AC-004).
  - Concurrency between processes writing one database is not specified. Each command is one database transaction; no further concurrency guarantee is claimed.
  - No deployment target is stated beyond an executable at the application root. The product is a local CLI.
  - No auth model is required. The product is a local CLI with no protected resource.
- The relational-persistence gate applies. `TECHNOLOGY_STACK.md` selects `sqlalchemy.md` and `alembic.md`. The Manifest records SQLAlchemy as superseded by the generated package for Target persistence, so the generated package stays the only access path.

## Analysis Notes
generated: 2026-10-25
blueprint: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.155813/workspace/targets/LayersTesting/blueprint

Quality: Ready
  blockers: 0
  questions: 0
  features: 11
  stories: 30
  stack: Python 3.11+ over SQLite, through the shipped persistence library
  display_name: not proposed
  short_description: not proposed

Only the "Source Conflicts and Gaps" entries above affect planning, and each has a narrow default. Nothing needs a Commander decision.
