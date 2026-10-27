# Blueprint Analysis: LayersTesting

## Commander Expectations

- assert the completed ledger passes every check in the supplied grader, `sh sources/run.sh`, with exit code zero
- assert a rejected command changes no stored record
- assert every report is computed from stored ledger data and never from embedded answers
- assert the ledger runs as a Python 3.11+ command-line executable named `ledger` over SQLite, through the shipped persistence library

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
| LEDGER-001 | Initialize an empty ledger | `init` leaves accounts, categories, and transactions empty and writes nothing; rerunning it removes every record. |
| LEDGER-002 | Count rows per table | `count` writes `table,rows`, then `accounts`, `categories`, and `transactions` rows in that order. |

### Feature: Bulk Loading

| ID | Story | High-level AC |
|---|---|---|
| LOAD-001 | Load accounts from a file | Accepts a file whose header matches and whose rows are all valid; writes `table,loaded` and `accounts,<rows>`; any invalid row or duplicate key exits 3 and stores none of the rows. |
| LOAD-002 | Load categories from a file | Same contract as LOAD-001 for `categories`. |
| LOAD-003 | Load transactions from a file | Keeps each file `txn_id`; any invalid row, unknown account or category, or negative-balance result exits 3 and stores none of the rows. |

### Feature: Account Maintenance

| ID | Story | High-level AC |
|---|---|---|
| ACCT-001 | Add an account | `account add` stores the code and name and writes the new row with 0 transactions and balance `0.00`; a duplicate code exits 3. |
| ACCT-002 | Get an account | `account get` writes the current account row; an absent code exits 4. |
| ACCT-003 | Rename an account | `account rename` changes only the name and writes the updated row; an absent code exits 4; an invalid name exits 3. |
| ACCT-004 | Delete an account | `account delete` writes `deleted` and the code; an account with transactions is refused with exit 3; an absent code exits 4. |

### Feature: Transaction Recording

| ID | Story | High-level AC |
|---|---|---|
| TXN-001 | Post a transaction | `txn post` assigns one more than the largest `txn_id` (or 1 when empty), validates every field, writes the new row, and exits 3 without writing when a rule fails. |
| TXN-002 | Get a transaction | `txn get` writes the stored row; an absent id exits 4. |
| TXN-003 | Amend a transaction amount | `txn amend` changes only the amount and writes the updated row; an absent id exits 4; a result below zero exits 3 and changes nothing. |
| TXN-004 | Delete a transaction | `txn delete` writes `deleted` and the id; an absent id exits 4; a result below zero exits 3 and changes nothing. |

### Feature: Transfers

| ID | Story | High-level AC |
|---|---|---|
| XFER-001 | Transfer cash between two accounts | Stores two rows in category `TRANSFER` with consecutive ids, `-amount` then `+amount`, and writes both; identical accounts or a non-positive amount exits 3; any failure stores neither row. |

### Feature: Reports

| ID | Story | High-level AC |
|---|---|---|
| RPT-001 | Balances report | Writes one row per account ordered by code, then `TOTAL,,<count>,<sum>`, with balances computed from stored transactions. |
| RPT-002 | Categories report | Writes one row per category ordered by code, including categories with no transactions, then the TOTAL row with inflow, outflow, and net. |
| RPT-003 | Monthly report | Writes one row per `YYYY-MM` that has transactions, ascending, then the TOTAL row. |

### Feature: Command Contract

| ID | Story | High-level AC |
|---|---|---|
| CLI-001 | Reject bad command usage | An unknown command, unknown table, unknown report, or wrong argument count exits 2 with nothing on standard output. |

### Feature: Configuration and Storage

| ID | Story | High-level AC |
|---|---|---|
| CFG-001 | Select the database file | The database path comes from `DATABASE_URL` (optional `sqlite://` prefix), then `DATABASE_PATH`, then `data/app.db`. |

### Feature: Application Test Suite

| ID | Story | High-level AC |
|---|---|---|
| TEST-001 | Provide the application test suite | A POSIX-compatible `bin/test.sh` runs the automated suite against a real temporary database, covers each command, exit code, and rule, and exits zero only when every test passes. |

### Feature: Acceptance Verification

| ID | Story | High-level AC |
|---|---|---|
| VER-001 | Pass the supplied grader | `sh sources/run.sh` exits zero with every check passing. This is the terminal story and depends on every implementation story. |

## Story Guidance

Named stories planning must produce. Authoritative record: `STORY_GUIDANCE.json`.

| Story ID | Provenance | Gate | Note |
|---|---|---|---|
| LEDGER-001 | plan | — | run.sh sections A1 and Z1 (init and re-initialization) |
| LEDGER-002 | plan | — | run.sh sections A2, B4, D3, G6, and Z2 (count) |
| LOAD-001 | plan | — | run.sh sections B1 and D2 (accounts load and rejected reload) |
| LOAD-002 | plan | — | run.sh section B2 (categories load) |
| LOAD-003 | plan | — | run.sh sections B3 and D1 (transactions load and rejected batch) |
| ACCT-001 | plan | — | run.sh section E1 and E2 |
| ACCT-002 | plan | — | run.sh section E3 and E5 |
| ACCT-003 | plan | — | run.sh section E4 |
| ACCT-004 | plan | — | run.sh sections E6, E7, and E8 |
| TXN-001 | plan | — | run.sh sections F1, F5, F6, F7, and F10 |
| TXN-002 | plan | — | run.sh sections F2, F4, and F9 |
| TXN-003 | plan | — | run.sh sections F3 and G4 |
| TXN-004 | plan | — | run.sh sections F8 and G5 |
| XFER-001 | plan | — | run.sh sections G1 and G2 |
| RPT-001 | plan | — | run.sh sections C1 and H1 |
| RPT-002 | plan | — | run.sh sections C2 and H2 |
| RPT-003 | plan | — | run.sh sections C3 and H3 |
| CLI-001 | plan | — | run.sh sections U1 and U2 |
| VER-001 | plan | — | Terminal story; run.sh is the full grader over all sections |

## Surfaced Acceptance Criteria

| ID | Story ID | Criterion |
|---|---|---|
| AC-001 | CLI-001 | The diagnostic for a usage error names the expected argument form of the command and is written only to standard error. |
| AC-002 | RPT-001 | On an empty ledger, the balances report writes its header and a `TOTAL,,0,0.00` row. |
| AC-003 | RPT-002 | When no categories exist, the categories report writes its header and a `TOTAL,,0,0.00,0.00,0.00` row. |
| AC-004 | RPT-003 | When no transactions exist, the monthly report writes its header and a `TOTAL,0,0.00,0.00,0.00` row. |
| AC-005 | TXN-001 | A date of February 29 is accepted only in a Gregorian leap year and rejected in any other year. |
| AC-006 | TXN-001 | A transaction posted without a memo writes an empty final memo field. |
| AC-007 | LOAD-001 | A file that contains a valid header and no data rows loads zero rows, writes `accounts,0`, and exits 0. |
| AC-008 | CFG-001 | If the database cannot be opened, the command exits 1, writes nothing to standard output, and changes no record. |

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
| sources/INSTRUCTIONS.md | instruction-to-test | sources/run.sh | Check groups A to Z reproduce the command table, exit codes, and rules 1 to 7 | Each command story implements a contract the grader checks; VER-001 is the final proof |
| sources/run.sh | dependency | sources/seed_accounts.csv, sources/seed_categories.csv, sources/seed_transactions.csv | Checks B1 to B4 load these through `$SEED` | All four files are staged beside run.sh before VER-001 |
| sources/run.sh | dependency | sources/seed_transactions_bad.csv | Check D1 expects exit 3 from the batch with unknown account on row 11 | Stage with run.sh; LOAD-003 owns atomic rejection |
| sources/seed_transactions_bad.csv | instruction-to-test | sources/INSTRUCTIONS.md Rule 1 | Rows 1 to 10 are valid and row 11 names an unknown account | LOAD-003 stores none of the batch |
| sources/seed_transactions.csv | dependency | sources/run.sh checks C1 to C3 | Report answers are computed from these 120 rows | RPT stories depend on LOAD-003 |
| sources/INSTRUCTIONS.md | instruction-to-test | Application test suite (`bin/test.sh`) | The Tests section requires a suite run by `bin/test.sh` | TEST-001 owns the suite |

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

The system is a command-line executable named `ledger` at the application root. Inputs are command arguments, CSV files named on the command line, and the database file selected by configuration. Outputs are CSV on standard output for successful commands, one diagnostic line on standard error for failures, and exit codes 0 to 4. Each command validates every input and rule before its first write, then writes all of its changes or none. Reports are computed from stored rows at the time of the command.

### Story Realization Map

- CFG-001: database path selection from configuration. Evidence: INSTRUCTIONS.md Database section. Requires a capability and a test harness that points at a temporary database.
- LEDGER-001: initialization and reset. Evidence: Commands table; run.sh A1, Z1, Z2. Requires a capability.
- LEDGER-002: row counts. Evidence: Commands table; run.sh A2, B4, D3, G6, Z2. Requires a capability.
- LOAD-001: accounts load. Evidence: Commands table; run.sh B1, D2; seed_accounts.csv. Requires a capability and a fixture.
- LOAD-002: categories load. Evidence: run.sh B2; seed_categories.csv. Requires a capability and a fixture.
- LOAD-003: transactions load. Evidence: run.sh B3, D1; seed_transactions.csv; seed_transactions_bad.csv; Rules 1 and 2. Requires a capability and a fixture.
- ACCT-001: account add. Evidence: run.sh E1, E2. Requires a capability.
- ACCT-002: account get. Evidence: run.sh E3, E5. Requires a capability.
- ACCT-003: account rename. Evidence: run.sh E4. Requires a capability.
- ACCT-004: account delete. Evidence: run.sh E6, E7, E8. Requires a capability.
- TXN-001: transaction post. Evidence: run.sh F1, F5, F6, F7, F10; Rules 3 to 7. Requires a capability.
- TXN-002: transaction get. Evidence: run.sh F2, F4, F9. Requires a capability.
- TXN-003: transaction amend. Evidence: run.sh F3, G4. Requires a capability.
- TXN-004: transaction delete. Evidence: run.sh F8, G5. Requires a capability.
- XFER-001: transfer. Evidence: run.sh G1, G2; Rule 1; Commands table. Requires a capability.
- RPT-001: balances report. Evidence: run.sh C1, H1. Requires a capability and depends on LOAD-003.
- RPT-002: categories report. Evidence: run.sh C2, H2. Requires a capability and depends on LOAD-003.
- RPT-003: monthly report. Evidence: run.sh C3, H3. Requires a capability and depends on LOAD-003.
- CLI-001: usage errors. Evidence: run.sh U1, U2; Exit codes table. Requires a capability.
- TEST-001: application suite. Evidence: INSTRUCTIONS.md Tests section. Requires a test harness.
- VER-001: supplied grader. Evidence: run.sh; SEA_TRIALS st-001. Requires an acceptance contract.

### Test and Acceptance Strategy

VER-001 is the single terminal verification story. It depends on every implementation story and declares `Suite: full` in its heading block. Its assertion runs `sh sources/run.sh` unfiltered and requires exit code zero with every check passing.

No other story runs `sources/run.sh`. The supplied grader has no scope selector, so each feature story runs focused pytest cases for its own slice and declares `Suite: scoped`. TEST-001 declares `Suite: scoped` and verifies the script's own selection behavior. Focused story tests do not replace the final Sea Trial verification.

### Sequencing and Dependencies

1. CFG-001: every later story reads the database path.
2. LEDGER-001 and LEDGER-002.
3. LOAD-001, LOAD-002, LOAD-003. LOAD-003 requires LOAD-001 and LOAD-002 because its rows reference accounts and categories.
4. ACCT-001 to ACCT-004.
5. TXN-001 to TXN-004. Amend and delete depend on the balance rule introduced in TXN-001.
6. XFER-001.
7. RPT-001 to RPT-003. Report answers depend on the loaded seed data and on TXN and XFER behavior.
8. CLI-001.
9. TEST-001, after every implementation story.
10. VER-001, last.

External dependencies: none. The shipped persistence library is the only storage boundary.

### Source Conflicts and Gaps

No source conflicts were found. `bin/test.sh` (the application's own suite) and the pytest runner named in the stack are compatible: `bin/test.sh` may invoke pytest.

The sources name a "shipped persistence library" without describing it. Planning treats it as the Rigging persistence layer generated from `DATABASE.md`, as recorded in TECHNOLOGY_STACK.md. No additional decision is required.

## Analysis Notes
generated: 2026-10-26
blueprint: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.030445/workspace/targets/LayersTesting/blueprint

Quality: Ready
  blockers: 0
  questions: 0
  features: 10
  stories: 21
  stack: Python 3.11+, SQLite, pytest
  display_name: not proposed
  short_description: not proposed

- Unattended UAT policy applied. No blocker, questionnaire, or open question is emitted. The decisions below are the selected behaviors and are persisted here and in the specifications.
- Authentication: none. The ledger is a local command-line tool. Access to the database file is governed by operating system file permissions. No protected resource with a separate identity is described.
- Database open failure: exit 1 with nothing written (AC-008).
- Usage help: no help command is added. Usage diagnostics on standard error name the expected form (AC-001).
- Calendar dates: Gregorian leap-year rule (AC-005).
- Stack: the sources name no ORM. The Python relational-persistence rule requires the SQLAlchemy and Alembic rows, so both are proposed in TECHNOLOGY_STACK.md. The shipped persistence library remains the only database access boundary.
- Concurrency: the sources describe no shared-state concurrency, so no concurrency criterion is added.
- Story count is 21, below the 80-story threshold, so no story-count question is emitted.
- The application's own `bin/test.sh` suite (TEST-001) and the supplied grader (VER-001) are both required and are distinct.
