# DATABASE: Ledger Persistence Contract

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Defines the relational ledger schema, configuration resolution, and typed persistence operations. |
| Depends On  | ARCHITECTURE.md |
| Provides    | DATABASE_URL resolution, DATABASE_PATH fallback, relational ledger schema, persistence operations |
| Consumes    | application module boundaries, configuration boundary, persistence boundary |

## Configuration

Resolve the database DSN in this order:

1. `DATABASE_URL`
2. `DATABASE_PATH`
3. `data/app.db`

A `postgres://` or `postgresql://` value selects PostgreSQL. Any other value is a SQLite path, optionally prefixed with `sqlite://`. Application callers use `persistence.open_database(dsn)` and never open a driver directly.

## Access Patterns

### FEATURE-PERSISTENCE-001 — Initialize schema

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `accounts.create` |
| Compatibility | rebuild |

Input: `InitializationInput`

| Field | Type |
|---|---|
| `drop_existing` | boolean |

Output: `InitializationResult`

| Field | Type |
|---|---|
| `initialized` | boolean |

### FEATURE-PERSISTENCE-002 — Count accounts

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `accounts.list` |
| Compatibility | unchanged |

Input: `CountInput`

| Field | Type |
|---|---|
| `—` | — |

Output: `AccountCount`

| Field | Type |
|---|---|
| `accounts` | integer |

### FEATURE-PERSISTENCE-003 — Count categories

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `categories.list` |
| Compatibility | unchanged |

Input: `CountInput`

| Field | Type |
|---|---|
| `—` | — |

Output: `CategoryCount`

| Field | Type |
|---|---|
| `categories` | integer |

### FEATURE-PERSISTENCE-004 — Count transactions

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `transactions.list` |
| Compatibility | unchanged |

Input: `CountInput`

| Field | Type |
|---|---|
| `—` | — |

Output: `TransactionCount`

| Field | Type |
|---|---|
| `transactions` | integer |

### FEATURE-LEDGER-001 — Create account

| Field | Value |
|---|---|
| Owner | FEATURE-Accounts.md |
| Access | write |
| Repository operation | `accounts.create` |
| Compatibility | data |

Input: `AccountInput`

| Field | Type |
|---|---|
| `account` | VARCHAR(12) |
| `name` | VARCHAR(40) |

Output: `AccountRow`

| Field | Type |
|---|---|
| `account` | VARCHAR(12) |
| `name` | VARCHAR(40) |

### FEATURE-LEDGER-002 — Retrieve account

| Field | Value |
|---|---|
| Owner | FEATURE-Accounts.md |
| Access | read |
| Repository operation | `accounts.get` |
| Compatibility | unchanged |

Input: `AccountKey`

| Field | Type |
|---|---|
| `account` | VARCHAR(12) |

Output: `AccountRow`

| Field | Type |
|---|---|
| `account` | VARCHAR(12) |
| `name` | VARCHAR(40) |

### FEATURE-LEDGER-003 — Update account

| Field | Value |
|---|---|
| Owner | FEATURE-Accounts.md |
| Access | write |
| Repository operation | `accounts.update` |
| Compatibility | data |

Input: `AccountUpdate`

| Field | Type |
|---|---|
| `account` | VARCHAR(12) |
| `name` | VARCHAR(40) |

Output: `AccountRow`

| Field | Type |
|---|---|
| `account` | VARCHAR(12) |
| `name` | VARCHAR(40) |

### FEATURE-LEDGER-004 — Delete account

| Field | Value |
|---|---|
| Owner | FEATURE-Accounts.md |
| Access | write |
| Repository operation | `accounts.delete` |
| Compatibility | data |

Input: `AccountKey`

| Field | Type |
|---|---|
| `account` | VARCHAR(12) |

Output: `DeletionResult`

| Field | Type |
|---|---|
| `deleted` | boolean |

### FEATURE-LEDGER-005 — Create transaction

| Field | Value |
|---|---|
| Owner | FEATURE-Transaction-Posting.md |
| Access | write |
| Repository operation | `transactions.create` |
| Compatibility | data |

Input: `TransactionInput`

| Field | Type |
|---|---|
| `txn_id` | integer |
| `date` | VARCHAR(10) |
| `account` | VARCHAR(12) |
| `category` | VARCHAR(12) |
| `amount` | integer |
| `memo` | VARCHAR(60) |

Output: `TransactionRow`

| Field | Type |
|---|---|
| `txn_id` | integer |
| `date` | VARCHAR(10) |
| `account` | VARCHAR(12) |
| `category` | VARCHAR(12) |
| `amount` | integer |
| `memo` | VARCHAR(60) |

### FEATURE-LEDGER-006 — Retrieve transaction

| Field | Value |
|---|---|
| Owner | FEATURE-Transaction-Posting.md |
| Access | read |
| Repository operation | `transactions.get` |
| Compatibility | unchanged |

Input: `TransactionKey`

| Field | Type |
|---|---|
| `txn_id` | integer |

Output: `TransactionRow`

| Field | Type |
|---|---|
| `txn_id` | integer |
| `date` | VARCHAR(10) |
| `account` | VARCHAR(12) |
| `category` | VARCHAR(12) |
| `amount` | integer |
| `memo` | VARCHAR(60) |

### FEATURE-LEDGER-007 — Update transaction

| Field | Value |
|---|---|
| Owner | FEATURE-Transaction-Mutation.md |
| Access | write |
| Repository operation | `transactions.update` |
| Compatibility | data |

Input: `TransactionAmountUpdate`

| Field | Type |
|---|---|
| `txn_id` | integer |
| `amount` | integer |

Output: `TransactionRow`

| Field | Type |
|---|---|
| `txn_id` | integer |
| `date` | VARCHAR(10) |
| `account` | VARCHAR(12) |
| `category` | VARCHAR(12) |
| `amount` | integer |
| `memo` | VARCHAR(60) |

### FEATURE-LEDGER-008 — Delete transaction

| Field | Value |
|---|---|
| Owner | FEATURE-Transaction-Mutation.md |
| Access | write |
| Repository operation | `transactions.delete` |
| Compatibility | data |

Input: `TransactionKey`

| Field | Type |
|---|---|
| `txn_id` | integer |

Output: `DeletionResult`

| Field | Type |
|---|---|
| `deleted` | boolean |

### FEATURE-REPORT-001 — Aggregate account balances

| Field | Value |
|---|---|
| Owner | FEATURE-Balance-Reports.md |
| Access | read |
| Repository operation | `accounts.list` |
| Compatibility | unchanged |

Input: `AccountReportFilter`

| Field | Type |
|---|---|
| `—` | — |

Output: `AccountBalanceRow`

| Field | Type |
|---|---|
| `account` | VARCHAR(12) |
| `name` | VARCHAR(40) |
| `transactions` | integer |
| `balance` | integer |

### FEATURE-REPORT-002 — Aggregate category totals

| Field | Value |
|---|---|
| Owner | FEATURE-Category-Reports.md |
| Access | read |
| Repository operation | `categories.list` |
| Compatibility | unchanged |

Input: `CategoryReportFilter`

| Field | Type |
|---|---|
| `—` | — |

Output: `CategoryTotalRow`

| Field | Type |
|---|---|
| `category` | VARCHAR(12) |
| `description` | VARCHAR(40) |
| `transactions` | integer |
| `inflow` | integer |
| `outflow` | integer |
| `net` | integer |

### FEATURE-REPORT-003 — Aggregate monthly totals

| Field | Value |
|---|---|
| Owner | FEATURE-Monthly-Reports.md |
| Access | read |
| Repository operation | `transactions.list` |
| Compatibility | unchanged |

Input: `MonthlyReportFilter`

| Field | Type |
|---|---|
| `—` | — |

Output: `MonthlyTotalRow`

| Field | Type |
|---|---|
| `month` | VARCHAR(7) |
| `transactions` | integer |
| `inflow` | integer |
| `outflow` | integer |
| `net` | integer |

## Schema

## `accounts`

| Field | Type | Notes |
|---|---|---|
| `account` | VARCHAR(12) NOT NULL [PK] | Uppercase alphanumeric account code |
| `name` | VARCHAR(40) NOT NULL | Account name |

## `categories`

| Field | Type | Notes |
|---|---|---|
| `category` | VARCHAR(12) NOT NULL [PK] | Uppercase alphanumeric category code |
| `description` | VARCHAR(40) NOT NULL | Category description |

## `transactions`

| Field | Type | Notes |
|---|---|---|
| `txn_id` | INTEGER NOT NULL [PK] | Transaction identifier |
| `date` | VARCHAR(10) NOT NULL | Real calendar date in `YYYY-MM-DD` form |
| `account` | VARCHAR(12) NOT NULL REFERENCES accounts(account) | Account code |
| `category` | VARCHAR(12) NOT NULL REFERENCES categories(category) | Category code |
| `amount` | INTEGER NOT NULL | Signed amount in cents |
| `memo` | VARCHAR(60) NOT NULL | Transaction memo |

## Persistence Rules

All writes are preceded by complete validation. Foreign keys are enforced. Transactions are atomic. Amounts are represented only as integers in persistence and formatted to two decimal places at the CLI boundary.

## Programmatic Acceptance

- None. Drydock validates declared SQLite schema construction and connectivity invariants deterministically.
## User Acceptance

- None.

## Guardrails

- No application module may import a database driver.
- Every declared table is reached through a declared repository operation.
- No floating-point amount is stored or used for ledger arithmetic.
- Schema initialization is idempotent and recreates the three ledger tables when requested.
