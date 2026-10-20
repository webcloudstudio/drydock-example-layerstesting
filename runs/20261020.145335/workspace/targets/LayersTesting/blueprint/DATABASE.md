# DATABASE: Ledger Store

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Cash ledger store: accounts, categories, and transactions with integer-cent amounts. |
| Depends On  | ARCHITECTURE.md |
| Provides    | db.accounts, db.categories, db.transactions |

## Purpose

Declares the three tables of the cash ledger and every operation the commands need. Drydock
generates the persistence package from this file. Callers in `commands/` use only the declared
operations.

## Access Patterns

### FEATURE-LEDGER-001 — List accounts

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `accounts.list` |
| Compatibility | unchanged |

Input: `NoInput`

| Field | Type | Notes |
|-------|------|-------|
| — | — | No input fields. |

Output: `AccountRow`

| Field | Type | Notes |
|-------|------|-------|
| account | VARCHAR(12) | Account code. One row per account. |
| name | VARCHAR(40) | Account name. |

### FEATURE-LEDGER-002 — Get an account

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `accounts.get` |
| Compatibility | unchanged |

Input: `AccountKey`

| Field | Type | Notes |
|-------|------|-------|
| account | VARCHAR(12) | Account code to read. |

Output: `AccountRow`

| Field | Type | Notes |
|-------|------|-------|
| account | VARCHAR(12) | Account code. |
| name | VARCHAR(40) | Account name. |

### FEATURE-LEDGER-003 — Create an account

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `accounts.create` |
| Compatibility | unchanged |

Input: `AccountRow`

| Field | Type | Notes |
|-------|------|-------|
| account | VARCHAR(12) | New account code. |
| name | VARCHAR(40) | Account name. |

Output: `AccountRow`

| Field | Type | Notes |
|-------|------|-------|
| account | VARCHAR(12) | Stored account code. |
| name | VARCHAR(40) | Stored account name. |

### FEATURE-LEDGER-004 — Update an account name

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `accounts.update` |
| Compatibility | unchanged |

Input: `AccountRow`

| Field | Type | Notes |
|-------|------|-------|
| account | VARCHAR(12) | Account code to change. |
| name | VARCHAR(40) | New account name. |

Output: `AccountRow`

| Field | Type | Notes |
|-------|------|-------|
| account | VARCHAR(12) | Account code. |
| name | VARCHAR(40) | Stored account name. |

### FEATURE-LEDGER-005 — Delete an account

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `accounts.delete` |
| Compatibility | unchanged |

Input: `AccountKey`

| Field | Type | Notes |
|-------|------|-------|
| account | VARCHAR(12) | Account code to delete. |

Output: `AccountKey`

| Field | Type | Notes |
|-------|------|-------|
| account | VARCHAR(12) | Deleted account code. |

### FEATURE-LEDGER-006 — List categories

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `categories.list` |
| Compatibility | unchanged |

Input: `NoInput`

| Field | Type | Notes |
|-------|------|-------|
| — | — | No input fields. |

Output: `CategoryRow`

| Field | Type | Notes |
|-------|------|-------|
| category | VARCHAR(12) | Category code. One row per category. |
| description | VARCHAR(40) | Category description. |

### FEATURE-LEDGER-007 — Get a category

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `categories.get` |
| Compatibility | unchanged |

Input: `CategoryKey`

| Field | Type | Notes |
|-------|------|-------|
| category | VARCHAR(12) | Category code to read. |

Output: `CategoryRow`

| Field | Type | Notes |
|-------|------|-------|
| category | VARCHAR(12) | Category code. |
| description | VARCHAR(40) | Category description. |

### FEATURE-LEDGER-008 — Create a category

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `categories.create` |
| Compatibility | unchanged |

Input: `CategoryRow`

| Field | Type | Notes |
|-------|------|-------|
| category | VARCHAR(12) | New category code. |
| description | VARCHAR(40) | Category description. |

Output: `CategoryRow`

| Field | Type | Notes |
|-------|------|-------|
| category | VARCHAR(12) | Stored category code. |
| description | VARCHAR(40) | Stored description. |

### FEATURE-LEDGER-009 — List transactions

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `transactions.list` |
| Compatibility | unchanged |

Input: `NoInput`

| Field | Type | Notes |
|-------|------|-------|
| — | — | No input fields. |

Output: `TransactionRow`

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id. One row per transaction. |
| date | VARCHAR(10) | Date as YYYY-MM-DD. |
| account | VARCHAR(12) | Account code. |
| category | VARCHAR(12) | Category code. |
| amount | INTEGER | Signed amount in integer cents. |
| memo | VARCHAR(60) | Memo, possibly empty. |

### FEATURE-LEDGER-010 — Get a transaction

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `transactions.get` |
| Compatibility | unchanged |

Input: `TransactionKey`

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id to read. |

Output: `TransactionRow`

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id. |
| date | VARCHAR(10) | Date as YYYY-MM-DD. |
| account | VARCHAR(12) | Account code. |
| category | VARCHAR(12) | Category code. |
| amount | INTEGER | Signed amount in integer cents. |
| memo | VARCHAR(60) | Memo, possibly empty. |

### FEATURE-LEDGER-011 — Create a transaction

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `transactions.create` |
| Compatibility | unchanged |

Input: `TransactionRow`

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Id assigned by the command layer. |
| date | VARCHAR(10) | Date as YYYY-MM-DD. |
| account | VARCHAR(12) | Account code. |
| category | VARCHAR(12) | Category code. |
| amount | INTEGER | Signed amount in integer cents. |
| memo | VARCHAR(60) | Memo, possibly empty. |

Output: `TransactionRow`

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Stored transaction id. |
| date | VARCHAR(10) | Stored date. |
| account | VARCHAR(12) | Stored account code. |
| category | VARCHAR(12) | Stored category code. |
| amount | INTEGER | Stored amount in integer cents. |
| memo | VARCHAR(60) | Stored memo. |

### FEATURE-LEDGER-012 — Update a transaction amount

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `transactions.update` |
| Compatibility | unchanged |

Input: `TransactionAmount`

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id to change. |
| amount | INTEGER | New amount in integer cents. |

Output: `TransactionRow`

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id. |
| date | VARCHAR(10) | Unchanged date. |
| account | VARCHAR(12) | Unchanged account code. |
| category | VARCHAR(12) | Unchanged category code. |
| amount | INTEGER | Stored amount in integer cents. |
| memo | VARCHAR(60) | Unchanged memo. |

### FEATURE-LEDGER-013 — Delete a transaction

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `transactions.delete` |
| Compatibility | unchanged |

Input: `TransactionKey`

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id to delete. |

Output: `TransactionKey`

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Deleted transaction id. |

## Schema

## `accounts`

| Field | Type | Notes |
|-------|------|-------|
| account | VARCHAR(12) PK NOT NULL | Account code, A-Z and 0-9. |
| name | VARCHAR(40) NOT NULL | Account name. |

## `categories`

| Field | Type | Notes |
|-------|------|-------|
| category | VARCHAR(12) PK NOT NULL | Category code, A-Z and 0-9. |
| description | VARCHAR(40) NOT NULL | Category description. |

## `transactions`

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER PK NOT NULL | Transaction id. |
| date | VARCHAR(10) NOT NULL | Date as YYYY-MM-DD. |
| account | VARCHAR(12) NOT NULL REFERENCES accounts(account) | Account the amount posts to. |
| category | VARCHAR(12) NOT NULL REFERENCES categories(category) | Category of the amount. |
| amount | INTEGER NOT NULL | Signed amount in integer cents. |
| memo | VARCHAR(60) NOT NULL DEFAULT '' | Memo, possibly empty. |

## Programmatic Acceptance

- None. Drydock validates declared SQLite schema construction and connectivity invariants deterministically.
## User Acceptance

- None.

## Guardrails

- Amounts are INTEGER cents. No REAL or NUMERIC column stores money.
- Application code reaches these tables only through the declared repository operations.
- Foreign keys enforce that a transaction names an existing account and an existing category.
- Account deletion while transactions exist is refused by the command layer before the delete operation runs.
