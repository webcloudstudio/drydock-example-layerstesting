# Blueprint Analysis: drydock Layers Testing Uat Case

## Commander Expectations

- assert the supplied grader `sh sources/run.sh` passes every check with exit code zero against a fresh database
- assert the product is an executable named `ledger` at the application root
- assert every command either completes in full or changes nothing
- assert no command leaves any account balance below zero
- assert every report is computed from stored ledger data and never from an embedded answer
- assert transfers conserve cash by recording an equal debit and credit in category `TRANSFER`

## Crew

| Crew | Charge |
|---|---|
| Commander | Defines intent and decides what done means. |
| Team Lead | Confirms epic completeness and stakeholder expectations. |
| Planning Crew | Authors atomic specifications and the ordered Manifest. |
| Shipyard Crew | Builds the tickets without synchronous Commander access. |

## Story List

### Feature: Ledger Lifecycle

| ID | Story | High-level AC |
|---|---|---|
| LEDGER-001 | Initialize an empty ledger | `ledger init` exits 0 and writes nothing; accounts, categories, and transactions are empty afterward; rerunning removes existing records |
| LEDGER-002 | Count rows per table | `ledger count` writes `table,rows`, then `accounts`, `categories`, and `transactions` rows in that order |

### Feature: Ledger Storage

| ID | Story | High-level AC |
|---|---|---|
| DB-001 | Resolve the database location | `DATABASE_URL` is used first, then `DATABASE_PATH`, then `data/app.db`; a `sqlite://` prefix or bare path selects SQLite; a `postgres://` or `postgresql://` value is recognised and passed to the persistence library unchanged |
| DB-002 | Persist ledger state across invocations and fail on unreachable storage | A record written by one invocation is visible to the next; an unreachable database or missing tables exits 1 with a diagnostic on standard error and nothing on standard output |

### Feature: Bulk Loading

| ID | Story | High-level AC |
|---|---|---|
| LOAD-001 | Load accounts from a CSV file | `ledger load accounts <csv>` validates every row before any write; a header other than `account,name` is rejected; success writes `table,loaded` then `accounts,<rows>`; a duplicate code exits 3 with no write |
| LOAD-002 | Load categories from a CSV file | `ledger load categories <csv>` validates every row before any write; a header other than `category,description` is rejected; success writes `table,loaded` then `categories,<rows>`; a duplicate code exits 3 with no write |
| LOAD-003 | Load transactions from a CSV file | `ledger load transactions <csv>` keeps each file `txn_id`; validates date, amount, memo, and references to accounts and categories; rejects the whole file on any bad row, including an unknown account, and on any balance below zero; success writes `table,loaded` then `transactions,<rows>` |

### Feature: Accounts

| ID | Story | High-level AC |
|---|---|---|
| ACC-001 | Add an account | `ledger account add <code> <name>` writes the new row with 0 transactions and balance `0.00`; a duplicate code exits 3 with no write |
| ACC-002 | Retrieve an account | `ledger account get <code>` writes the current row including transaction count and balance; an absent code exits 4 |
| ACC-003 | Rename an account | `ledger account rename <code> <name>` writes the updated row; balance and transaction count are unchanged; an absent code exits 4 |
| ACC-004 | Delete an account | `ledger account delete <code>` writes `deleted` then the code on the next line; an account with transactions is refused with exit 3; an absent code exits 4 |

### Feature: Transactions

| ID | Story | High-level AC |
|---|---|---|
| TXN-001 | Post a transaction | `ledger txn post` writes the new row with id one more than the largest present, or `1` in an empty table; invalid account, category, amount, date, or memo exits 3; a posting that leaves a balance below zero exits 3; nothing is written on any rejection |
| TXN-002 | Retrieve a transaction | `ledger txn get <id>` writes the stored row; an absent id exits 4 |
| TXN-003 | Amend a transaction amount | `ledger txn amend <id> <amount>` changes only the amount and writes the updated row; an absent id exits 4; an amendment that leaves any balance below zero exits 3 and changes nothing |
| TXN-004 | Delete a transaction | `ledger txn delete <id>` writes `deleted` then the id on the next line; an absent id exits 4; a deletion that leaves any balance below zero exits 3 and changes nothing |

### Feature: Transfers

| ID | Story | High-level AC |
|---|---|---|
| XFER-001 | Record a valid transfer | `ledger transfer <from> <to> <amount> <date>` writes two rows in category `TRANSFER`: `-amount` on `<from>` with memo `transfer to <to>`, then `+amount` on `<to>` with memo `transfer from <from>`; both balances update |
| XFER-002 | Refuse an invalid or overdrawing transfer | A transfer with equal accounts, a non-positive amount, an unknown account, an invalid date, or any resulting negative balance exits 3 and stores neither row |

### Feature: Reports

| ID | Story | High-level AC |
|---|---|---|
| RPT-001 | Report account balances | `ledger report balances` writes one row per account ordered by code, then `TOTAL,,<count>,<sum>`; all values come from stored data |
| RPT-002 | Report category totals | `ledger report categories` writes one row per category ordered by code, including categories with no transactions, then the `TOTAL` row; inflow, outflow, and net follow the rules in the sources |
| RPT-003 | Report monthly totals | `ledger report monthly` writes one row per `YYYY-MM` that has transactions in ascending order, then `TOTAL,<count>,<inflow>,<outflow>,<net>` |

### Feature: CLI Contract

| ID | Story | High-level AC |
|---|---|---|
| CLI-001 | Reject unknown commands, reports, tables, and wrong argument counts | Each case exits 2, writes nothing to standard output, and writes one diagnostic line to standard error |
| CLI-002 | Provide help text for every command and sub-verb | Help text is available for each command and sub-verb listed in the Commands table |

### Feature: Release Gate

| ID | Story | High-level AC |
|---|---|---|
| VER-001 | Pass the supplied end-to-end ledger grader | `sh sources/run.sh` exits 0 and every supplied check passes against the completed application |

## Story Guidance

Named stories planning must produce. Authoritative record: `STORY_GUIDANCE.json`.

None.

## Surfaced Acceptance Criteria

| ID | Story ID | Criterion |
|---|---|---|
| AC-001 | RPT-001 | On an empty ledger the balances report writes its header and a `TOTAL` row with transaction count `0` and balance `0.00`. |
| AC-002 | RPT-002 | On a ledger with no categories the categories report writes its header and a `TOTAL` row with `0` transactions and `0.00` in inflow, outflow, and net. |
| AC-003 | RPT-003 | On an empty ledger the monthly report writes its header and a `TOTAL` row with `0` transactions and `0.00` in inflow, outflow, and net. |
| AC-004 | ACC-002 | A malformed account code given to `account get` exits 3 before any lookup; only a well-formed absent code exits 4. |
| AC-005 | TXN-002 | A non-integer id given to `txn get` exits 3 before any lookup; only an absent integer id exits 4. |
| AC-006 | LOAD-001 | A header-only file loads zero rows, writes `<table>,0` after `table,loaded`, and exits 0; the same applies to `categories` and `transactions`. |
| AC-007 | LOAD-001 | A file whose header does not match the table's columns exits 3 and writes nothing; a missing or unreadable file exits 1. |
| AC-008 | CLI-002 | Help text exists for every sub-verb, including `account` and `txn` sub-verbs, and is available without touching the database. |

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
| sources/run.sh | instruction-to-test | sources/INSTRUCTIONS.md | Commands table, output tables, and Exit codes table define every grader known answer (sections A through Z) | Build to the Commands and Exit codes tables; the grader is the arbiter |
| sources/run.sh | dataset-to-test | sources/seed_accounts.csv, sources/seed_categories.csv, sources/seed_transactions.csv | Checks B1 to B4 and C1 to C3 load and report these files | Stage the three seed files beside run.sh so `$SEED` resolves |
| sources/run.sh | dataset-to-test | sources/seed_transactions_bad.csv | Check D1 expects exit 3 on row 11 with an unknown account | Stage the bad file; the load must reject it without partial writes |
| sources/INSTRUCTIONS.md Tests section | instruction-to-test | bin/test.sh application suite | Suite must cover each command, exit code, and rule against a real temporary database | Each feature story extends the pytest suite exposed through `bin/test.sh` |
| sources/INSTRUCTIONS.md Database section | dependency | Persistence library and generated relational layer | All access goes through the shipped library; the relational layer is generated from DATABASE.md | Plan authors DATABASE.md; no story opens a driver directly |
| sources/INSTRUCTIONS.md Rules 1 and 2 | dependency | All write commands | Every write checks every rule before its first write and balance rule applies to all writes | One shared pre-write validation path serves LOAD, ACC, TXN, and XFER stories |
| sources/INSTRUCTIONS.md Rules 3 to 7 | dependency | Account, category, and transaction input | Code, name, memo, amount, date, and id formats | Shared input validation is folded into each story that accepts the input |

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

The system is a command-line ledger invoked as `ledger <command>` from the application root. It reads argv and CSV files, writes CSV to standard output on success, and writes one diagnostic line to standard error on failure. Ledger state lives in a relational store reached only through the shipped persistence library. The default store is the SQLite file `data/app.db`. Amounts are stored as integer cents. Every write command validates all inputs and rules before its first write.

### Story Realization Map

- LEDGER-001: capability. Evidence: INSTRUCTIONS Commands (`init`), Z1 and A1 in run.sh. Related: DB-001, DB-002.
- LEDGER-002: capability. Evidence: INSTRUCTIONS Commands (`count`), run.sh A2, B4, D3, G6, Z2.
- DB-001: integration. Evidence: INSTRUCTIONS Database section. Related: persistence library, DATABASE.md.
- DB-002: integration and acceptance contract. Evidence: INSTRUCTIONS Exit codes (1). Related: DB-001.
- LOAD-001: capability. Evidence: INSTRUCTIONS Commands (`load`), Rule 1; run.sh B1, D2. Related: sources/seed_accounts.csv.
- LOAD-002: capability. Evidence: INSTRUCTIONS Commands (`load`); run.sh B2. Related: sources/seed_categories.csv.
- LOAD-003: capability. Evidence: INSTRUCTIONS Rules 1 and 2, Rule 7; run.sh B3, D1. Related: sources/seed_transactions.csv, sources/seed_transactions_bad.csv, LOAD-001, LOAD-002.
- ACC-001: capability. Evidence: INSTRUCTIONS Commands (`account add`); run.sh E1, E2.
- ACC-002: capability. Evidence: INSTRUCTIONS Commands (`account get`); run.sh E3, E5, E8.
- ACC-003: capability. Evidence: INSTRUCTIONS Commands (`account rename`); run.sh E4.
- ACC-004: capability. Evidence: INSTRUCTIONS Commands (`account delete`); run.sh E6, E7.
- TXN-001: capability. Evidence: INSTRUCTIONS Rules 1 to 7 and Commands (`txn post`); run.sh F1, F5 to F7, F10, G2, G3. Related: ACC-001, categories.
- TXN-002: capability. Evidence: INSTRUCTIONS Commands (`txn get`); run.sh F2, F4, F9.
- TXN-003: capability. Evidence: INSTRUCTIONS Commands (`txn amend`), Rule 2; run.sh F3, G4.
- TXN-004: capability. Evidence: INSTRUCTIONS Commands (`txn delete`), Rule 2; run.sh F8, G5.
- XFER-001: capability. Evidence: INSTRUCTIONS Commands (`transfer`); run.sh G1, H1 to H3.
- XFER-002: capability. Evidence: INSTRUCTIONS Rule 1 and Rule 2; run.sh G2.
- RPT-001: capability. Evidence: INSTRUCTIONS Commands (`report balances`); run.sh C1, H1.
- RPT-002: capability. Evidence: INSTRUCTIONS Commands (`report categories`); run.sh C2, H2.
- RPT-003: capability. Evidence: INSTRUCTIONS Commands (`report monthly`); run.sh C3, H3.
- CLI-001: acceptance contract. Evidence: INSTRUCTIONS Exit codes (2) and Output; run.sh U1, U2.
- CLI-002: capability. Evidence: Core Baseline for cli projects; no help text is specified in the sources (see AC-008).
- VER-001: acceptance contract and release gate. Evidence: run.sh and INSTRUCTIONS Run Harness.

### Test and Acceptance Strategy

Focused story tests run in the application's pytest suite against a real temporary database. Each feature story runs only the slice it owns and declares `Suite: scoped`. The grader has no scope selector, so no feature story runs `sh sources/run.sh`. VER-001 is the single terminal verification story. It depends on every other story and declares `Suite: full`. Its acceptance is the unfiltered run of `sh sources/run.sh` with exit status zero, which corresponds to Sea Trial st-001. `bin/test.sh` remains the application's own suite; VER-001 does not replace it.

### Sequencing and Dependencies

1. DB-001, then DB-002.
2. LEDGER-001 (`init`), then LEDGER-002 (`count`).
3. LOAD-001 and LOAD-002, then LOAD-003, because transaction loads reference accounts and categories.
4. ACC-001, then ACC-002, ACC-003, and ACC-004.
5. TXN-001, then TXN-002, TXN-003, and TXN-004.
6. XFER-001, then XFER-002, which depend on accounts and transactions.
7. RPT-001, RPT-002, and RPT-003, which depend on loaded and posted data.
8. CLI-001 and CLI-002, which may be built any time after LEDGER-001.
9. VER-001, last.

External dependency: the shipped persistence library and the generated relational layer from DATABASE.md, which Plan authors.

### Source Conflicts and Gaps

- Stack versus Database section. The Stack section names SQLite; the Database section also accepts a PostgreSQL DSN. Resolved to the narrowest consistent behavior: the Target is SQLite, the DSN is recognised and passed to the persistence library unchanged, and no grader check exercises PostgreSQL.
- The persistence library is named but not supplied. Treated as the generated relational layer described by Rigging `persistence.md`. Plan authors DATABASE.md.
- Header mismatch on load is not assigned an exit code. Resolved to exit 3 (rejected file row or structure), recorded as AC-007.
- A non-integer id has no stated exit code. Resolved to exit 3 (rejected input), recorded as AC-005.
- Empty-ledger report output is implied but not shown. Resolved to header plus TOTAL row, recorded as AC-001 to AC-003.
- No authentication or access control is stated. The ledger is a local CLI, so none is built.

## Analysis Notes
generated: 2026-10-25
blueprint: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.184252/workspace/targets/LayersTesting/blueprint

Quality: Ready
  blockers: 0
  questions: 0
  features: 9
  stories: 23
  stack: Python 3.11+ over SQLite
  display_name: not proposed
  short_description: not proposed

- Project type: cli.
- STORY_GUIDANCE.json omitted: the sources state a grader without a scope selector, so no per-story gate can be scoped.
- Retired Sea Trial IDs st-002, st-003, and st-009 are not reissued. New guardrail criteria are st-012, st-013, and st-014.
- Surfaced AC rows resolve gaps by narrowest consistent behavior, listed under Source Conflicts and Gaps.
