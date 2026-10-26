# Blueprint Analysis: drydock Layers Testing Uat Case

## Commander Expectations

- assert the completed ledger is a command-line cash ledger that runs as an executable named `ledger` at the application root
- assert the ledger persists all data through the shipped persistence library over SQLite
- assert a rejected command changes nothing
- assert no command leaves an account balance below zero
- assert every report is computed from stored database data, never embedded answers
- assert the supplied end-to-end grader `sh sources/run.sh` passes with exit code zero

## Crew

| Crew | Charge |
|---|---|
| Commander | Defines intent and decides what done means. |
| Team Lead | Confirms epic completeness and stakeholder expectations. |
| Planning Crew | Authors atomic specifications and the ordered Manifest. |
| Shipyard Crew | Builds the tickets without synchronous Commander access. |

## Story List

Summary: features: 6, stories: 17

### Feature: Ledger Lifecycle

| ID | Story | High-level AC |
|---|---|---|
| LEDGER-LIFECYCLE-001 | Initialize an empty ledger | `ledger init` prepares an empty database for use, writes nothing to stdout, and removes existing ledger records when rerun |
| LEDGER-LIFECYCLE-002 | Count ledger rows per table | `ledger count` prints `table,rows` then accounts, categories, transactions in that order |

### Feature: Bulk Load

| ID | Story | High-level AC |
|---|---|---|
| BULK-LOAD-001 | Load accounts from CSV | `ledger load accounts <csv>` accepts a file whose header matches `account,name`, writes `table,loaded` and `accounts,<rows>`, and rejects the whole file with exit 3 on any invalid row |
| BULK-LOAD-002 | Load categories from CSV | `ledger load categories <csv>` accepts a file whose header matches `category,description`, writes `table,loaded` and `categories,<rows>`, and rejects the whole file with exit 3 on any invalid row |
| BULK-LOAD-003 | Load transactions from CSV | `ledger load transactions <csv>` accepts a file whose header matches the transaction columns, writes `table,loaded` and `transactions,<rows>`, and rejects the whole file with exit 3 when any row is invalid, references an unknown account or category, or would leave a balance negative |

### Feature: Reporting

| ID | Story | High-level AC |
|---|---|---|
| REPORTING-001 | Report account balances | `ledger report balances` prints `account,name,transactions,balance` per account ordered by code, then a `TOTAL` row |
| REPORTING-002 | Report category totals | `ledger report categories` prints inflow, outflow, and net per category ordered by code, including empty categories, then a `TOTAL` row |
| REPORTING-003 | Report monthly totals | `ledger report monthly` prints inflow, outflow, and net per `YYYY-MM` with transactions in ascending order, then a `TOTAL` row |

### Feature: Account Management

| ID | Story | High-level AC |
|---|---|---|
| ACCOUNT-001 | Add an account | `ledger account add <code> <name>` stores the account and prints its row; duplicate codes exit 3 |
| ACCOUNT-002 | Get an account | `ledger account get <code>` prints the account row; an absent code exits 4 |
| ACCOUNT-003 | Rename an account | `ledger account rename <code> <name>` updates the name and prints the row; an absent code exits 4 |
| ACCOUNT-004 | Delete an account | `ledger account delete <code>` prints `deleted` and the code; an account with transactions is refused with exit 3; an absent code exits 4 |

### Feature: Transaction Management

| ID | Story | High-level AC |
|---|---|---|
| TRANSACTION-001 | Post a transaction | `ledger txn post` stores a row with the next `txn_id`, prints the row, and rejects invalid codes, amounts, dates, or negative balances with exit 3 |
| TRANSACTION-002 | Get a transaction | `ledger txn get <id>` prints the transaction row; an absent id exits 4 |
| TRANSACTION-003 | Amend a transaction amount | `ledger txn amend <id> <amount>` changes only the amount and prints the row; an absent id exits 4; a negative resulting balance exits 3 |
| TRANSACTION-004 | Delete a transaction | `ledger txn delete <id>` removes the row and prints `deleted` and the id; an absent id exits 4; a negative resulting balance exits 3 |

### Feature: Transfers

| ID | Story | High-level AC |
|---|---|---|
| TRANSFER-001 | Transfer cash between accounts | `ledger transfer <from> <to> <amount> <date>` stores two rows in category `TRANSFER` with ids `n` and `n+1`, prints both, and stores both or neither |

## Story Guidance

Named stories planning must produce. Authoritative record: `STORY_GUIDANCE.json`.

None.

## Surfaced Acceptance Criteria

| ID | Story ID | Criterion |
|---|---|---|
| AC-001 | LEDGER-LIFECYCLE-001 | `init` writes nothing to standard output and exits 0 |
| AC-002 | BULK-LOAD-001 | A load that rejects any row stores none of the preceding rows |
| AC-003 | BULK-LOAD-003 | A transaction load assigns each loaded `txn_id` from its file and prints the loaded count |
| AC-004 | TRANSACTION-001 | A posted transaction receives one more than the largest stored `txn_id`, or `1` in an empty table |
| AC-005 | TRANSFER-001 | A transfer with equal accounts, a non-positive amount, or an unknown account exits 3 and stores no rows |
| AC-006 | ACCOUNT-004 | Deleting an account with no transactions succeeds and prints `deleted` and the code |

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
| `sources/run.sh` | instruction-to-test | `sources/INSTRUCTIONS.md` | `run.sh` header and checks cite the command contract in `INSTRUCTIONS.md` | The grader is the terminal verification; stories must match its exact stdout and exit codes |
| `sources/seed_accounts.csv` | dependency | `sources/seed_transactions.csv` | Transactions reference account codes `DRAWER1`, `DRAWER2`, `PETTY`, `SAFE` | Accounts must load before transactions |
| `sources/seed_categories.csv` | dependency | `sources/seed_transactions.csv` | Transactions reference categories `OPENING`, `SALES`, `REFUND`, `TRANSFER`, `SUPPLY`, `PAYROLL`, `RENT` | Categories must load before transactions |
| `sources/seed_transactions_bad.csv` | test-kit-to-implementation | BULK-LOAD-003 | Row 11 names unknown account `NOSUCH`; check D1 expects exit 3 | Load validation must be all-or-nothing |

## Source Roles

| Path | Role | Plan disposition | Build disposition |
|---|---|---|---|
| sources/INSTRUCTIONS.md | author intent | compass | prompt-only |
| sources/run.sh | conformance harness | compass | stage |
| sources/seed_accounts.csv | asset | context | stage |
| sources/seed_categories.csv | asset | context | stage |
| sources/seed_transactions.csv | asset | context | stage |
| sources/seed_transactions_bad.csv | asset | context | stage |

## Planning Instructions

### Delivery Shape

The system is a single-executable CLI named `ledger` at the application root. Inputs are CSV seed files and command-line arguments. Outputs are CSV on standard output for success and a single diagnostic line on standard error for failure. Persistence is SQLite through the shipped persistence library, with three tables: `accounts`, `categories`, and `transactions`. Amounts are integer cents.

Required execution flow: `init` → `load accounts` → `load categories` → `load transactions` → reports and mutations, with every mutation validated before its first write.

### Story Realization Map

- LEDGER-LIFECYCLE-001 — `sources/INSTRUCTIONS.md` Commands and Exit codes; `sources/run.sh` A1, Z1. Requires persistence capability.
- LEDGER-LIFECYCLE-002 — `sources/run.sh` A2, B4, D3, G6, Z2. Requires persistence capability.
- BULK-LOAD-001 — `sources/seed_accounts.csv`; `sources/run.sh` B1, D2. Requires persistence capability and CSV parsing.
- BULK-LOAD-002 — `sources/seed_categories.csv`; `sources/run.sh` B2. Requires persistence capability and CSV parsing.
- BULK-LOAD-003 — `sources/seed_transactions.csv`, `sources/seed_transactions_bad.csv`; `sources/run.sh` B3, D1. Requires persistence capability, CSV parsing, and balance validation.
- REPORTING-001 — `sources/run.sh` C1, H1. Requires computed aggregation from the database.
- REPORTING-002 — `sources/run.sh` C2, H2. Requires computed aggregation from the database.
- REPORTING-003 — `sources/run.sh` C3, H3. Requires computed aggregation from the database.
- ACCOUNT-001 — `sources/run.sh` E1, E2. Requires persistence capability.
- ACCOUNT-002 — `sources/run.sh` E3, E5, E8. Requires persistence capability.
- ACCOUNT-003 — `sources/run.sh` E4. Requires persistence capability.
- ACCOUNT-004 — `sources/run.sh` E6, E7. Requires persistence capability and a reference check against transactions.
- TRANSACTION-001 — `sources/run.sh` F1, F5, F6, F7, F10. Requires persistence capability and balance validation.
- TRANSACTION-002 — `sources/run.sh` F2, F4, F9. Requires persistence capability.
- TRANSACTION-003 — `sources/run.sh` F3. Requires persistence capability and balance validation.
- TRANSACTION-004 — `sources/run.sh` F8. Requires persistence capability and balance validation.
- TRANSFER-001 — `sources/run.sh` G1, G2. Requires persistence capability and atomic dual-row write.

### Test and Acceptance Strategy

Focused story tests run per story against a temporary database. The terminal verification story runs the unfiltered grader `sh sources/run.sh` with `Suite: full`.

### Sequencing and Dependencies

- `init` precedes all other commands.
- Accounts load before categories and transactions.
- Categories load before transactions.
- Transaction validation depends on loaded accounts and categories.
- The terminal verification story depends on every implementation story.

### Source Conflicts and Gaps

- `sources/INSTRUCTIONS.md` names the Python 3.11 SQLite stack, and the brief's Database section defines `DATABASE_URL` precedence. No conflicting definitions were found across sources.
- Ambiguity resolved for the unattended run: the `ledger transfer` contract is taken exactly as written in the brief. A transfer amount of zero is treated as non-positive and rejected with exit 3, as AC-005 states.
- Ambiguity resolved: `account delete` on an absent code exits 4 per the brief's exit code table.

## Analysis Notes
generated: 2026-10-25
blueprint: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/workspace/targets/LayersTesting/blueprint

Quality: Ready
  blockers: 0
  questions: 0
  features: 6
  stories: 17
  stack: Python 3.11, SQLite
  display_name: not proposed
  short_description: not proposed

None.
