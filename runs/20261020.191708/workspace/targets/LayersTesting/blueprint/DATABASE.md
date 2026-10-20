# DATABASE: Ledger Persistence

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Define the relational ledger schema and typed persistence operations. |
| Depends On  | ARCHITECTURE.md |
| Provides    | accounts table, categories table, transactions table, schema initialization |
| Consumes    | — |

## Stores

The application uses the relational database selected by `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`. SQLite paths may be prefixed with `sqlite://`; PostgreSQL DSNs begin with `postgres://` or `postgresql://`. Application callers use only `persistence.open_database`.

## Access Patterns

### FEATURE-DB-001 — Initialize schema

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `accounts.create` |
| Compatibility | rebuild |

Input: `InitializeSchema`

| Field | Type |
|---|---|
| drop_existing | INTEGER |

Output: `SchemaStatus`

| Field | Type |
|---|---|
| tables | TEXT |

### FEATURE-DB-002 — Account operations

| Field | Value |
|---|---|
| Owner | FEATURE-Account-Category-Loading.md |
| Access | read-write |
| Repository operation | `accounts.create` |
| Compatibility | unchanged |

Input: `AccountInput`

| Field | Type |
|---|---|
| account | VARCHAR(12) |
| name | VARCHAR(40) |

Output: `AccountRow`

| Field | Type |
|---|---|
| account | VARCHAR(12) |
| name | VARCHAR(40) |

### FEATURE-DB-003 — Category operations

| Field | Value |
|---|---|
| Owner | FEATURE-Account-Category-Loading.md |
| Access | read-write |
| Repository operation | `categories.create` |
| Compatibility | unchanged |

Input: `CategoryInput`

| Field | Type |
|---|---|
| category | VARCHAR(12) |
| description | VARCHAR(40) |

Output: `CategoryRow`

| Field | Type |
|---|---|
| category | VARCHAR(12) |
| description | VARCHAR(40) |

### FEATURE-DB-004 — Transaction operations

| Field | Value |
|---|---|
| Owner | FEATURE-Transaction-Loading.md |
| Access | read-write |
| Repository operation | `transactions.create` |
| Compatibility | unchanged |

Input: `TransactionInput`

| Field | Type |
|---|---|
| txn_id | INTEGER |
| date | VARCHAR(10) |
| account | VARCHAR(12) |
| category | VARCHAR(12) |
| amount | INTEGER |
| memo | VARCHAR(60) |

Output: `TransactionRow`

| Field | Type |
|---|---|
| txn_id | INTEGER |
| date | VARCHAR(10) |
| account | VARCHAR(12) |
| category | VARCHAR(12) |
| amount | INTEGER |
| memo | VARCHAR(60) |

### FEATURE-DB-005 — Account reads and mutations

| Field | Value |
|---|---|
| Owner | FEATURE-Account-Management.md |
| Access | read-write |
| Repository operation | `accounts.get` |
| Compatibility | unchanged |

Input: `AccountLookup`

| Field | Type |
|---|---|
| account | VARCHAR(12) |

Output: `AccountBalanceRow`

| Field | Type |
|---|---|
| account | VARCHAR(12) |
| name | VARCHAR(40) |
| transactions | INTEGER |
| balance | INTEGER |

### FEATURE-DB-006 — Transaction reads and mutations

| Field | Value |
|---|---|
| Owner | FEATURE-Transaction-Management.md |
| Access | read-write |
| Repository operation | `transactions.get` |
| Compatibility | unchanged |

Input: `TransactionLookup`

| Field | Type |
|---|---|
| txn_id | INTEGER |

Output: `TransactionRow`

| Field | Type |
|---|---|
| txn_id | INTEGER |
| date | VARCHAR(10) |
| account | VARCHAR(12) |
| category | VARCHAR(12) |
| amount | INTEGER |
| memo | VARCHAR(60) |

### FEATURE-DB-007 — Report reads

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `accounts.list` |
| Compatibility | unchanged |

Input: `ReportQuery`

| Field | Type |
|---|---|
| report | TEXT |

Output: `ReportRow`

| Field | Type |
|---|---|
| values | TEXT |

## Schema

## `accounts`

| Field | Type | Notes |
|---|---|---|
| account | VARCHAR(12) PK NOT NULL | Account code |
| name | VARCHAR(40) NOT NULL | Account name |

## `categories`

| Field | Type | Notes |
|---|---|---|
| category | VARCHAR(12) PK NOT NULL | Category code |
| description | VARCHAR(40) NOT NULL | Category description |

## `transactions`

| Field | Type | Notes |
|---|---|---|
| txn_id | INTEGER PK NOT NULL | Transaction identifier |
| date | VARCHAR(10) NOT NULL | Calendar date in `YYYY-MM-DD` form |
| account | VARCHAR(12) NOT NULL REFERENCES accounts(account) | Account code |
| category | VARCHAR(12) NOT NULL REFERENCES categories(category) | Category code |
| amount | INTEGER NOT NULL | Integer cents |
| memo | VARCHAR(60) NOT NULL | Transaction memo |

## Atomicity and Invariants

Schema initialization drops and recreates all three tables. Foreign keys are enforced. Every command validates all inputs and prospective balance effects before its first write. Transactions are committed atomically.

## Programmatic Acceptance

- None. Drydock validates declared SQLite schema construction and connectivity invariants deterministically.
## User Acceptance

- None.

## Guardrails

- Amounts are stored as integer cents.
- No application module may open a database driver directly.
- Every rejected command must preserve all existing rows.
- Schema initialization must leave all three tables empty.
