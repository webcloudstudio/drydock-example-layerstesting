# DATABASE: Cash Ledger Store

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Persistence contract for the accounts, categories, and transactions tables. |

## Access Patterns

### FEATURE-ACCOUNT-001 — Create account

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `accounts.create` |
| Compatibility | unchanged |

Input: AccountRow

| Field | Type | Notes |
|---|---|---|
| account | VARCHAR(12) | Account code |
| name | VARCHAR(40) | Account name |

Output: AccountRow

| Field | Type | Notes |
|---|---|---|
| account | VARCHAR(12) | Account code |
| name | VARCHAR(40) | Account name |

### FEATURE-ACCOUNT-002 — Get account

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `accounts.get` |
| Compatibility | unchanged |

Input: AccountKey

| Field | Type | Notes |
|---|---|---|
| account | VARCHAR(12) | Account code |

Output: AccountRow

| Field | Type | Notes |
|---|---|---|
| account | VARCHAR(12) | Account code |
| name | VARCHAR(40) | Account name |

### FEATURE-ACCOUNT-003 — List accounts

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `accounts.list` |
| Compatibility | unchanged |

Input: NoFields

| Field | Type | Notes |
|---|---|---|
| (none) | — | The list takes no filter. |

Output: AccountRow

| Field | Type | Notes |
|---|---|---|
| account | VARCHAR(12) | Account code |
| name | VARCHAR(40) | Account name |

### FEATURE-ACCOUNT-004 — Update account name

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `accounts.update` |
| Compatibility | unchanged |

Input: AccountRow

| Field | Type | Notes |
|---|---|---|
| account | VARCHAR(12) | Account code to update |
| name | VARCHAR(40) | New account name |

Output: AccountRow

| Field | Type | Notes |
|---|---|---|
| account | VARCHAR(12) | Account code |
| name | VARCHAR(40) | Updated account name |

### FEATURE-ACCOUNT-005 — Delete account

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `accounts.delete` |
| Compatibility | unchanged |

Input: AccountKey

| Field | Type | Notes |
|---|---|---|
| account | VARCHAR(12) | Account code |

Output: DeleteResult

| Field | Type | Notes |
|---|---|---|
| rows | INTEGER | Rows removed |

### FEATURE-CATEGORY-001 — Create category

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `categories.create` |
| Compatibility | unchanged |

Input: CategoryRow

| Field | Type | Notes |
|---|---|---|
| category | VARCHAR(12) | Category code |
| description | VARCHAR(40) | Category description |

Output: CategoryRow

| Field | Type | Notes |
|---|---|---|
| category | VARCHAR(12) | Category code |
| description | VARCHAR(40) | Category description |

### FEATURE-CATEGORY-002 — Get category

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `categories.get` |
| Compatibility | unchanged |

Input: CategoryKey

| Field | Type | Notes |
|---|---|---|
| category | VARCHAR(12) | Category code |

Output: CategoryRow

| Field | Type | Notes |
|---|---|---|
| category | VARCHAR(12) | Category code |
| description | VARCHAR(40) | Category description |

### FEATURE-CATEGORY-003 — List categories

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `categories.list` |
| Compatibility | unchanged |

Input: NoFields

| Field | Type | Notes |
|---|---|---|
| (none) | — | The list takes no filter. |

Output: CategoryRow

| Field | Type | Notes |
|---|---|---|
| category | VARCHAR(12) | Category code |
| description | VARCHAR(40) | Category description |

### FEATURE-TXN-001 — Create transaction

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `transactions.create` |
| Compatibility | unchanged |

Input: TransactionRow

| Field | Type | Notes |
|---|---|---|
| txn_id | INTEGER | Transaction id, assigned by the caller |
| date | VARCHAR(10) | Date as YYYY-MM-DD |
| account | VARCHAR(12) | Account code |
| category | VARCHAR(12) | Category code |
| amount | INTEGER | Amount in integer cents |
| memo | VARCHAR(60) | Memo |

Output: TransactionRow

| Field | Type | Notes |
|---|---|---|
| txn_id | INTEGER | Transaction id |
| date | VARCHAR(10) | Date as YYYY-MM-DD |
| account | VARCHAR(12) | Account code |
| category | VARCHAR(12) | Category code |
| amount | INTEGER | Amount in integer cents |
| memo | VARCHAR(60) | Memo |

### FEATURE-TXN-002 — Get transaction

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `transactions.get` |
| Compatibility | unchanged |

Input: TransactionKey

| Field | Type | Notes |
|---|---|---|
| txn_id | INTEGER | Transaction id |

Output: TransactionRow

| Field | Type | Notes |
|---|---|---|
| txn_id | INTEGER | Transaction id |
| date | VARCHAR(10) | Date as YYYY-MM-DD |
| account | VARCHAR(12) | Account code |
| category | VARCHAR(12) | Category code |
| amount | INTEGER | Amount in integer cents |
| memo | VARCHAR(60) | Memo |

### FEATURE-TXN-003 — List transactions

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `transactions.list` |
| Compatibility | unchanged |

Input: NoFields

| Field | Type | Notes |
|---|---|---|
| (none) | — | The list takes no filter. Callers compute maxima, balances, and totals from the rows. |

Output: TransactionRow

| Field | Type | Notes |
|---|---|---|
| txn_id | INTEGER | Transaction id |
| date | VARCHAR(10) | Date as YYYY-MM-DD |
| account | VARCHAR(12) | Account code |
| category | VARCHAR(12) | Category code |
| amount | INTEGER | Amount in integer cents |
| memo | VARCHAR(60) | Memo |

### FEATURE-TXN-004 — Amend transaction amount

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `transactions.update` |
| Compatibility | unchanged |

Input: TransactionAmount

| Field | Type | Notes |
|---|---|---|
| txn_id | INTEGER | Transaction id to amend |
| amount | INTEGER | New amount in integer cents |

Output: TransactionRow

| Field | Type | Notes |
|---|---|---|
| txn_id | INTEGER | Transaction id |
| date | VARCHAR(10) | Date as YYYY-MM-DD |
| account | VARCHAR(12) | Account code |
| category | VARCHAR(12) | Category code |
| amount | INTEGER | Amount in integer cents |
| memo | VARCHAR(60) | Memo |

### FEATURE-TXN-005 — Delete transaction

| Field | Value |
|---|---|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `transactions.delete` |
| Compatibility | unchanged |

Input: TransactionKey

| Field | Type | Notes |
|---|---|---|
| txn_id | INTEGER | Transaction id |

Output: DeleteResult

| Field | Type | Notes |
|---|---|---|
| rows | INTEGER | Rows removed |

## Schema

## `accounts`

| Field | Type | Notes |
|---|---|---|
| account | VARCHAR(12) PK NOT NULL | Account code, primary key |
| name | VARCHAR(40) NOT NULL | Account name |

## `categories`

| Field | Type | Notes |
|---|---|---|
| category | VARCHAR(12) PK NOT NULL | Category code, primary key |
| description | VARCHAR(40) NOT NULL | Category description |

## `transactions`

| Field | Type | Notes |
|---|---|---|
| txn_id | INTEGER PK NOT NULL | Transaction id, primary key |
| date | VARCHAR(10) NOT NULL | Date as YYYY-MM-DD |
| account | VARCHAR(12) NOT NULL REFERENCES accounts(account) | Account code |
| category | VARCHAR(12) NOT NULL REFERENCES categories(category) | Category code |
| amount | INTEGER NOT NULL | Amount in integer cents |
| memo | VARCHAR(60) NOT NULL | Memo, zero to sixty characters |

## Programmatic Acceptance

- None. Drydock validates declared SQLite schema construction and connectivity invariants deterministically.
## User Acceptance

- None.

## Guardrails

- Application code reaches these tables only through the `persistence` package operations.
- No module imports a database driver.
