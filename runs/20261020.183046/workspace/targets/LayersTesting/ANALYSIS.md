# Blueprint Analysis: LayersTesting

## Commander Expectations

- assert the cash ledger passes the supplied conformance harness and preserves atomic, non-negative financial data behavior.
- assert the executable is a Python 3.11+ CLI backed by the shipped relational persistence library.

## Crew

| Crew | Charge |
|---|---|
| Commander | Defines intent and decides what done means. |
| Team Lead | Confirms epic completeness and stakeholder expectations. |
| Planning Crew | Authors atomic specifications and the ordered Manifest. |
| Shipyard Crew | Builds the tickets without synchronous Commander access. |

## Story List

### Feature: CLI Foundation and Schema

| ID | Story | High-level AC |
|---|---|---|
| CLI-001 | Provide the executable CLI and command validation | `ledger` is executable, supports every documented command, reports usage errors with exit code 2, and exposes command help text. |
| CLI-002 | Initialize and inspect the ledger schema | `init` drops and recreates all three tables; `count` reports the required table order and row counts. |

### Feature: Persistence and Bulk Loading

| ID | Story | High-level AC |
|---|---|---|
| DATA-001 | Implement the persistence-library repository boundary | All relational access uses the shipped persistence library selected by `DATABASE_URL`; amounts persist as integer cents. |
| DATA-002 | Load validated account, category, and transaction files atomically | Valid seed files load with exact counts and output; invalid, duplicate, unknown-reference, or rule-breaking files reject with no partial writes. |

### Feature: Ledger Reporting

| ID | Story | High-level AC |
|---|---|---|
| REPORT-001 | Generate account balance reports | Balances report accounts in code order with transaction counts, formatted balances, and the required total. |
| REPORT-002 | Generate category and monthly reports | Category and monthly reports calculate inflow, outflow, net, ordering, zero-transaction categories, and totals from database state. |

### Feature: Account and Transaction Operations

| ID | Story | High-level AC |
|---|---|---|
| OPS-001 | Manage account lifecycle | Account add, get, rename, and delete produce the specified CSV; duplicate, in-use, invalid, and absent accounts use the specified exit codes. |
| OPS-002 | Manage transaction lifecycle | Transaction post, get, amend, and delete produce the specified CSV, allocate IDs correctly, validate references and input, and preserve state on rejection. |

### Feature: Transfers and Financial Invariants

| ID | Story | High-level AC |
|---|---|---|
| FIN-001 | Execute atomic transfers | A transfer creates consecutive outgoing and incoming rows with the required category, amounts, dates, and memos, or creates neither row. |
| FIN-002 | Enforce non-negative balances | Every load, post, amend, delete, and transfer rejects any operation that would leave an account below zero. |

### Feature: Conformance Verification

| ID | Story | High-level AC |
|---|---|---|
| QA-001 | Provide the project test suite and terminal conformance gate | `bin/test.sh` exits zero only when all automated tests pass; `Suite: full` verification runs the supplied harness unfiltered and every supplied case passes. |

## Story Guidance

Named stories planning must produce. Authoritative record: `STORY_GUIDANCE.json`.

None.

## Surfaced Acceptance Criteria

| ID | Story ID | Criterion |
|---|---|---|
| AC-001 | CLI-001 | Every command and sub-verb has discoverable help text or usage guidance. |
| AC-002 | DATA-001 | The application does not open a database driver directly; persistence calls go through the shipped library and honor `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`. |
| AC-003 | OPS-001 | A missing account operation returns exit code 4 and writes no standard output. |
| AC-004 | OPS-002 | A missing transaction operation returns exit code 4 and writes no standard output. |

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
| `sources/INSTRUCTIONS.md` | instruction-to-test | `sources/run.sh` | The instructions define the command, output, exit-code, and atomicity contract exercised by the harness. | Build stories from the command and rule sections; reserve full-suite execution for terminal verification. |
| `sources/run.sh` | conformance harness | `sources/seed_*.csv` | The harness stages the seed files, loads them, and compares exact output for 43 checks. | Stage the harness and fixtures; QA-001 depends on every implementation story. |
| `sources/run.sh` | test-kit-to-implementation | `ledger` | The harness invokes the executable at the application root with `DATABASE_URL`. | The deliverable must be executable and preserve exact stdout and exit-code behavior. |
| `sources/seed_accounts.csv` | fixture-to-implementation | DATA-002 | The harness loads the account fixture and expects four rows. | Stage as a runtime acceptance fixture. |
| `sources/seed_categories.csv` | fixture-to-implementation | DATA-002 | The harness loads the category fixture and expects seven rows. | Stage as a runtime acceptance fixture. |
| `sources/seed_transactions.csv` | fixture-to-implementation | DATA-002 | The harness loads 120 transactions and uses them for report verification. | Stage as a runtime acceptance fixture. |
| `sources/seed_transactions_bad.csv` | fixture-to-implementation | DATA-002 | The harness verifies the bad batch is rejected atomically. | Stage as a runtime acceptance fixture. |

## Source Roles

| Path | Role | Plan disposition | Build disposition |
|---|---|---|---|
| `sources/INSTRUCTIONS.md` | normative specification and conformance test suite | context | prompt-only |
| `sources/run.sh` | conformance harness | context | stage |
| `sources/seed_accounts.csv` | asset | context | stage |
| `sources/seed_categories.csv` | asset | context | stage |
| `sources/seed_transactions.csv` | asset | context | stage |
| `sources/seed_transactions_bad.csv` | asset | context | stage |

## Planning Instructions

### Delivery Shape

The system is a local executable CLI. It accepts ledger lifecycle, loading, account, transaction, transfer, and reporting commands; persists three relational tables through the shipped persistence library; and emits exact CSV or diagnostics. The required flow is: initialize schema, load validated data atomically, execute mutations under balance invariants, and compute reports from persisted rows.

### Story Realization Map

| Story | Blueprint scope | Evidence | Related files | Delivery type |
|---|---|---|---|---|
| CLI-001 | executable entry point, argument parsing, help, exit codes | `sources/INSTRUCTIONS.md` Commands and Exit codes | `ledger` | capability |
| CLI-002 | schema lifecycle and count command | `sources/INSTRUCTIONS.md` Database and Commands; `sources/run.sh` A/Z | `sources/run.sh` | capability, migration |
| DATA-001 | persistence adapter and integer-cent model | `sources/INSTRUCTIONS.md` Stack and Database | `sources/run.sh` | integration |
| DATA-002 | CSV parsing, validation, references, atomic loads | `sources/INSTRUCTIONS.md` Rules and load command; seed fixtures | all staged seed files | capability, acceptance contract |
| REPORT-001 | balance aggregation and formatting | `sources/INSTRUCTIONS.md` balances report; `sources/run.sh` C1/H1 | `sources/run.sh` | capability |
| REPORT-002 | category/month aggregation and formatting | `sources/INSTRUCTIONS.md` category/monthly reports; `sources/run.sh` C2/C3/H2/H3 | `sources/run.sh` | capability |
| OPS-001 | account CRUD and in-use protection | `sources/INSTRUCTIONS.md` account commands; `sources/run.sh` E | `sources/run.sh` | capability |
| OPS-002 | transaction CRUD, IDs, validation | `sources/INSTRUCTIONS.md` transaction commands; `sources/run.sh` F | `sources/run.sh` | capability |
| FIN-001 | transfer pair creation and atomicity | `sources/INSTRUCTIONS.md` transfer command; `sources/run.sh` G1/G2 | `sources/run.sh` | capability |
| FIN-002 | balance invariant across all mutations | `sources/INSTRUCTIONS.md` Rules 1–2; `sources/run.sh` G | `sources/run.sh` | acceptance contract |
| QA-001 | project tests and complete supplied harness | `sources/INSTRUCTIONS.md` Tests; `sources/run.sh` | `bin/test.sh`, `sources/run.sh` | test harness, acceptance contract |

### Test and Acceptance Strategy

Each implementation story owns focused tests for its parser, repository calls, formatting, validation, and failure paths. The supplied harness is staged and used only by QA-001 as the terminal `Suite: full` verification. Story-level checks remain scoped to the story; no implementation story claims full-project correctness.

### Sequencing and Dependencies

Build the CLI and persistence boundary before command stories. Establish schema and repository contracts before loading, mutation, and reporting stories. Implement validation before bulk loading and financial mutations. Reports depend on persisted transaction behavior. Stage fixtures before QA-001. The full conformance gate runs last and depends on every implementation story.

### Source Conflicts and Gaps

No unresolved cross-source conflicts or blockers. The sources consistently define a Python CLI over SQLite, three tables, exact CSV output, atomic rejected commands, and exit-code semantics. Authentication, external services, deployment, and sensitive-data requirements are not implied for this local ledger and require no additional planning decision.

## Analysis Notes
generated: 2026-10-20
blueprint: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.183046/workspace/targets/LayersTesting/blueprint

Quality: Ready
  blockers: 0
  questions: 0
  features: 6
  stories: 11
  stack: Python 3.11+, SQLite, shipped Python persistence library, pytest, POSIX shell
  display_name: not proposed
  short_description: not proposed

None.
