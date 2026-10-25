# Blueprint Analysis: drydock Layers Testing Uat Case

## Commander Expectations

- assert the product is a command-line cash ledger that stores data only through the shipped persistence library
- assert every command either completes in full or changes nothing
- assert `sources/run.sh` exits zero against a completed `ledger` executable at the application root
- assert no report value is hard-coded in application code; every report is computed from the database
- assert amounts are stored as integer cents and printed with exactly two decimal places

## Crew

| Crew | Charge |
|---|---|
| Commander | Defines intent and decides what done means. |
| Team Lead | Confirms epic completeness and stakeholder expectations. |
| Planning Crew | Authors atomic specifications and the ordered Manifest. |
| Shipyard Crew | Builds the tickets without synchronous Commander access. |

## Story List

### Feature: Schema and Persistence Access

| ID | Story | High-level AC |
|---|---|---|
| SCHEMA-001 | Initialize an empty ledger schema with `ledger init` | Init drops and recreates accounts, categories, transactions; `count` reports 0 rows in each |
| SCHEMA-002 | Report row counts with `ledger count` | Prints `table,rows` header then accounts, categories, transactions rows |
| SCHEMA-003 | Load accounts from CSV with `ledger load accounts` | Header must match; 4 seed accounts load; output `table,loaded` and `accounts,4` |
| SCHEMA-004 | Load categories from CSV with `ledger load categories` | 7 seed categories load; output `categories,7` |
| SCHEMA-005 | Load transactions from CSV with `ledger load transactions` | 120 seed transactions load; output `transactions,120` |
| SCHEMA-006 | Reject an invalid CSV load atomically | Row 11 with unknown account rejected with exit 3; no rows from the file stored |

### Feature: Account Management

| ID | Story | High-level AC |
|---|---|---|
| ACCT-001 | Add an account with `ledger account add` | Validates code and name; prints the new account row with 0 transactions and 0.00 balance |
| ACCT-002 | Read an account with `ledger account get` | Prints the account row; exit 4 when absent |
| ACCT-003 | Rename an account with `ledger account rename` | Updates name only; prints the updated row; exit 4 when absent |
| ACCT-004 | Delete an account with `ledger account delete` | Prints `deleted` and code; refused with exit 3 while transactions exist; exit 4 when absent |
| ACCT-005 | Reject a duplicate account code | Exit 3 on duplicate key; no change to the table |

### Feature: Transaction Management

| ID | Story | High-level AC |
|---|---|---|
| TXN-001 | Post a transaction with `ledger txn post` | Assigns next txn_id (max+1 or 1); prints the transaction row |
| TXN-002 | Read a transaction with `ledger txn get` | Prints the row; exit 4 when absent |
| TXN-003 | Amend a transaction amount with `ledger txn amend` | Only amount changes; prints updated row; exit 4 when absent |
| TXN-004 | Delete a transaction with `ledger txn delete` | Prints `deleted` and id; exit 4 when absent |
| TXN-005 | Validate transaction inputs on post | Rejects unknown category, bad amount format (e.g. `1.234`), and invalid date (e.g. `2026-02-30`) with exit 3 |

### Feature: Transfers

| ID | Story | High-level AC |
|---|---|---|
| XFER-001 | Transfer funds between accounts with `ledger transfer` | Writes two rows in category TRANSFER (`-amount` then `+amount`) with the specified memos, atomically |
| XFER-002 | Reject a transfer that would overdraw the source account | Exit 3; no rows written |

### Feature: Balance Rule

| ID | Story | High-level AC |
|---|---|---|
| BAL-001 | Reject any post, amend, delete, transfer, or load that leaves a negative balance | Exit 3 before any write; no table changed |

### Feature: Reports

| ID | Story | High-level AC |
|---|---|---|
| RPT-001 | Report balances with `ledger report balances` | Per-account rows ordered by code plus TOTAL row; matches run.sh known answers |
| RPT-002 | Report totals by category with `ledger report categories` | Includes categories with no transactions; inflow, outflow, net per category plus TOTAL |
| RPT-003 | Report totals by month with `ledger report monthly` | Per YYYY-MM with transactions, ascending, plus TOTAL |

### Feature: CLI Contract

| ID | Story | High-level AC |
|---|---|---|
| CLI-001 | Return usage errors for unknown commands and reports | Exit 2 for unknown command, unknown table, unknown report, wrong argument count |
| CLI-002 | Write only the documented output and diagnostics | Success prints CSV to stdout with header, no quoting, LF endings; failures write one diagnostic line to stderr and nothing to stdout |
| CLI-003 | Resolve the database from `DATABASE_URL`, `DATABASE_PATH`, or `data/app.db` | PostgreSQL DSN prefixes route to PostgreSQL; other values are SQLite paths, optionally `sqlite://` prefixed |

### Feature: Test Suite

| ID | Story | High-level AC |
|---|---|---|
| TEST-001 | Provide `bin/test.sh` running the application's automated test suite | POSIX-compatible script; exits zero only when every test passes; covers each command, exit code, and rule against a temporary database |

## Story Guidance

Named stories planning must produce. Authoritative record: `STORY_GUIDANCE.json`.

| Story ID | Provenance | Gate | Note |
|---|---|---|---|
| TEST-001 | plan | `sh bin/test.sh` | sources/INSTRUCTIONS.md Tests section: bin/test.sh runs the application's own automated suite and exits zero only when every test passes |

## Surfaced Acceptance Criteria

| ID | Story ID | Criterion |
|---|---|---|
| AC-001 | SCHEMA-002 | `ledger count` with no arguments beyond `count` is a usage error (exit 2) |
| AC-002 | ACCT-001 | An account code longer than 12 characters or containing a character outside `A-Z0-9` is rejected with exit 3 |
| AC-003 | ACCT-001 | An account name longer than 40 characters or containing a comma or newline is rejected with exit 3 |
| AC-004 | TXN-001 | A memo longer than 60 characters or containing a comma or newline is rejected with exit 3 |
| AC-005 | TXN-001 | A post to an unknown account is rejected with exit 3 |
| AC-006 | TXN-001 | A zero amount is rejected with exit 3 |
| AC-007 | TXN-003 | Amending a transaction to an amount that violates the non-negative balance rule is rejected with exit 3 and changes nothing |
| AC-008 | XFER-001 | A transfer with a non-positive amount or identical `from` and `to` accounts is rejected with exit 3 |
| AC-009 | XFER-001 | A transfer to an unknown account is rejected with exit 3 and writes neither row |
| AC-010 | RPT-001 | Amounts in every report print with exactly two decimal places, a leading `-` when negative, and no thousands separator |
| AC-011 | CLI-003 | An unset `DATABASE_URL` falls back to `DATABASE_PATH`, then `data/app.db` |

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
| `sources/run.sh` | test-kit-to-implementation | `ledger` executable at application root | `sources/run.sh:44-47` requires executable `./ledger` and runs every check against it | Build must produce `ledger`; grader is the terminal acceptance |
| `sources/seed_accounts.csv` | dependency | `sources/run.sh` B1, C1 | `sources/run.sh:58-60`, reports at `sources/run.sh:83-89` | Seed loads must precede report verification |
| `sources/seed_categories.csv` | dependency | `sources/run.sh` B2, C2 | `sources/run.sh:62-64` | Seed loads must precede category report |
| `sources/seed_transactions.csv` | dependency | `sources/run.sh` B3, C1–C3 | `sources/run.sh:66-68`, reports | Known totals depend on exact 120-row load |
| `sources/seed_transactions_bad.csv` | dependency | `sources/run.sh` D1 | `sources/run.sh:95` expects exit 3 | Atomic load rule must be proven |
| `sources/INSTRUCTIONS.md` | instruction-to-test | `sources/run.sh` | `sources/INSTRUCTIONS.md` "Run Harness" section and `sources/run.sh:1-3` | Instructions define the contract the grader checks |
| `sources/INSTRUCTIONS.md` Database section | reference-to-replacement | `DATABASE.md` generated relational layer | `sources/INSTRUCTIONS.md` "Database" section | Repository layer must be generated from `DATABASE.md`; application never opens a driver directly |

## Source Roles

| Path | Role | Plan disposition | Build disposition |
|---|---|---|---|
| sources/INSTRUCTIONS.md | author intent | compass | prompt-only |
| sources/run.sh | conformance harness | context | stage |
| sources/seed_accounts.csv | test helper | context | stage |
| sources/seed_categories.csv | test helper | context | stage |
| sources/seed_transactions.csv | test helper | context | stage |
| sources/seed_transactions_bad.csv | test helper | context | stage |

## Planning Instructions

### Delivery Shape

The system is a single executable `ledger` at the application root, implemented in Python 3.11+ over SQLite, with PostgreSQL reachable through the shipped persistence library via `DATABASE_URL`. Inputs are CLI arguments and CSV files; outputs are CSV on stdout and one diagnostic line on stderr for failures. Persistence is three tables (`accounts`, `categories`, `transactions`) reached only through the shipped library. Execution flow: `init` → `load` seeds → commands and reports → grader.

### Story Realization Map

| Story ID | Durable scope | Evidence | Related files | Requires |
|---|---|---|---|---|
| SCHEMA-001 | init drops and recreates three tables | `sources/INSTRUCTIONS.md` Commands; `sources/run.sh:A1–A2` | persistence library, DATABASE.md | capability |
| SCHEMA-002 | count command | `sources/run.sh:A2, B4` | persistence library | capability |
| SCHEMA-003 | load accounts | `sources/run.sh:B1` | seed_accounts.csv | capability |
| SCHEMA-004 | load categories | `sources/run.sh:B2` | seed_categories.csv | capability |
| SCHEMA-005 | load transactions | `sources/run.sh:B3` | seed_transactions.csv | capability |
| SCHEMA-006 | atomic load rejection | `sources/run.sh:D1–D3`, Rule 1 | seed_transactions_bad.csv | capability, test harness |
| ACCT-001–005 | account commands | `sources/run.sh:E1–E8`, Commands table | — | capability |
| TXN-001–005 | transaction commands | `sources/run.sh:F1–F10`, Rules 3–7 | — | capability |
| XFER-001–002 | transfer command | `sources/run.sh:G1–G2`, Rule 1 | — | capability |
| BAL-001 | non-negative balance rule | `sources/run.sh:G3–G5`, Rule 2 | — | capability |
| RPT-001–003 | reports | `sources/run.sh:C1–C3, H1–H3`, Output | — | capability |
| CLI-001 | usage errors | `sources/run.sh:U1–U2` | — | capability |
| CLI-002 | output and diagnostic contract | Output section | — | capability |
| CLI-003 | database resolution | Database section | — | capability |
| TEST-001 | application test suite | Tests section | bin/test.sh | test harness |

### Test and Acceptance Strategy

Focused story tests run per story against the application's own pytest-style suite. The terminal verification story runs `sh sources/run.sh` unfiltered and gates on its exit status (`Suite: full`). Bounded stories run only their own slice. The grader is the sole acceptance verdict.

### Sequencing and Dependencies

Ordering: SCHEMA-001 → SCHEMA-002 → SCHEMA-003..005 → SCHEMA-006 → ACCT-* and TXN-* → XFER-* → BAL-001 → RPT-* → CLI-* → TEST-001 → terminal grader verification. Fixture (seed CSVs) must be staged before any load story. Persistence library and generated relational layer precede every data-touching story.

### Source Conflicts and Gaps

No cross-source conflicts. Stack is not named in the sources beyond Python 3.11+ and SQLite; the TECHNOLOGY_STACK.md proposal fills the remaining slots conventionally. Surfaced acceptance criteria above derive from `sources/INSTRUCTIONS.md` Rules and Commands and carry the chosen narrowest behavior where the sources are silent (e.g., account-code and name validation boundary is stated, not invented).

## Analysis Notes
generated: 2026-10-25
blueprint: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/workspace/targets/LayersTesting/blueprint

Quality: Ready
  blockers: 0
  questions: 0
  features: 7
  stories: 26
  stack: not declared
  display_name: not proposed
  short_description: not proposed

Selected behaviors (unattended UAT policy): 
- Empty-argument and malformed-argument cases for every command resolve to exit 2 (usage error).
- A `load` that encounters a duplicate primary key within a file is rejected with exit 3 and writes nothing.
- A `txn post` with a date outside the source-stated format resolves to exit 3.
- `DATABASE_URL` precedence follows the stated order; an unset value uses `data/app.db` relative to the application root.
