# DATABASE: Cash Ledger Store

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Persistence contract for the accounts, categories, and transactions tables. |
| Depends On  | ARCHITECTURE.md |
| Provides    | accounts, categories, transactions tables; open_database(dsn) |

## Access Patterns

These patterns are shared. No single feature owns them, so each names `DATABASE.md` as its owner.
Any Blueprint may cite them.

### FEATURE-ACCOUNT-001 — Create account

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `accounts.create` |
| Compatibility | unchanged |

Input: AccountCreate

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |
| name | TEXT | Account name |

Output: AccountRow

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |
| name | TEXT | Account name |

### FEATURE-ACCOUNT-002 — Get account

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `accounts.get` |
| Compatibility | unchanged |

Input: AccountKey

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |

Output: AccountRow

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |
| name | TEXT | Account name |

### FEATURE-ACCOUNT-003 — List accounts

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `accounts.list` |
| Compatibility | unchanged |

Input: NoInput

| Field | Type | Notes |
|-------|------|-------|
| (none) | — | No input fields |

Output: AccountRow

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |
| name | TEXT | Account name |

### FEATURE-ACCOUNT-004 — Rename account

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `accounts.update` |
| Compatibility | unchanged |

Input: AccountUpdate

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |
| name | TEXT | New account name |

Output: AccountRow

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |
| name | TEXT | Account name |

### FEATURE-ACCOUNT-005 — Delete account

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `accounts.delete` |
| Compatibility | unchanged |

Input: AccountKey

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |

Output: DeleteResult

| Field | Type | Notes |
|-------|------|-------|
| deleted | INTEGER | Rows removed |

### FEATURE-CATEGORY-001 — Create category

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `categories.create` |
| Compatibility | unchanged |

Input: CategoryCreate

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |
| description | TEXT | Category description |

Output: CategoryRow

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |
| description | TEXT | Category description |

### FEATURE-CATEGORY-002 — Get category

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `categories.get` |
| Compatibility | unchanged |

Input: CategoryKey

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |

Output: CategoryRow

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |
| description | TEXT | Category description |

### FEATURE-CATEGORY-003 — List categories

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `categories.list` |
| Compatibility | unchanged |

Input: NoInput

| Field | Type | Notes |
|-------|------|-------|
| (none) | — | No input fields |

Output: CategoryRow

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |
| description | TEXT | Category description |

### FEATURE-TXN-001 — Create transaction

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `transactions.create` |
| Compatibility | unchanged |

Input: TransactionCreate

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |
| date | TEXT | Date, YYYY-MM-DD |
| account | TEXT | Account code |
| category | TEXT | Category code |
| amount | INTEGER | Signed integer cents |
| memo | TEXT | Memo |

Output: TransactionRow

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |
| date | TEXT | Date, YYYY-MM-DD |
| account | TEXT | Account code |
| category | TEXT | Category code |
| amount | INTEGER | Signed integer cents |
| memo | TEXT | Memo |

### FEATURE-TXN-002 — Get transaction

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `transactions.get` |
| Compatibility | unchanged |

Input: TransactionKey

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |

Output: TransactionRow

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |
| date | TEXT | Date, YYYY-MM-DD |
| account | TEXT | Account code |
| category | TEXT | Category code |
| amount | INTEGER | Signed integer cents |
| memo | TEXT | Memo |

### FEATURE-TXN-003 — List transactions

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `transactions.list` |
| Compatibility | unchanged |

Input: NoInput

| Field | Type | Notes |
|-------|------|-------|
| (none) | — | No input fields |

Output: TransactionRow

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |
| date | TEXT | Date, YYYY-MM-DD |
| account | TEXT | Account code |
| category | TEXT | Category code |
| amount | INTEGER | Signed integer cents |
| memo | TEXT | Memo |

### FEATURE-TXN-004 — Amend transaction amount

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `transactions.update` |
| Compatibility | unchanged |

Input: TransactionAmend

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |
| amount | INTEGER | New signed integer cents |

Output: TransactionRow

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |
| date | TEXT | Date, YYYY-MM-DD |
| account | TEXT | Account code |
| category | TEXT | Category code |
| amount | INTEGER | Signed integer cents |
| memo | TEXT | Memo |

### FEATURE-TXN-005 — Delete transaction

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `transactions.delete` |
| Compatibility | unchanged |

Input: TransactionKey

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |

Output: DeleteResult

| Field | Type | Notes |
|-------|------|-------|
| deleted | INTEGER | Rows removed |

## Schema

## `accounts`

| Field | Type | Notes |
|-------|------|-------|
| account | VARCHAR(12) PK NOT NULL | Account code, `A-Z` and `0-9` |
| name | VARCHAR(40) NOT NULL | Account name |

## `categories`

| Field | Type | Notes |
|-------|------|-------|
| category | VARCHAR(12) PK NOT NULL | Category code, `A-Z` and `0-9` |
| description | VARCHAR(40) NOT NULL | Category description |

## `transactions`

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER PK NOT NULL | Transaction id |
| date | TEXT NOT NULL | Calendar date, `YYYY-MM-DD` |
| account | VARCHAR(12) NOT NULL REFERENCES accounts(account) | Account the amount posts to |
| category | VARCHAR(12) NOT NULL REFERENCES categories(category) | Category of the amount |
| amount | INTEGER NOT NULL | Signed amount in integer cents |
| memo | VARCHAR(60) NOT NULL DEFAULT '' | Memo, 0 to 60 characters |

## Programmatic Acceptance

- None. Drydock validates declared SQLite schema construction and connectivity invariants deterministically.
## User Acceptance

- None.

## Guardrails

- Money is never stored as `REAL` or `NUMERIC`. Every amount is `INTEGER` cents.
- Application code never imports a database driver. It reaches the tables only through
  `db.<table>.<verb>(...)`.
