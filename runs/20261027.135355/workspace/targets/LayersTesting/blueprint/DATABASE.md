# DATABASE: LayersTesting

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Persistence stores and typed interfaces for the LayersTesting cash ledger. |
| Depends On | ARCHITECTURE.md |
| Provides | persistence.accounts, persistence.categories, persistence.transactions |
| Build Order | 1 |

## Persistence Boundary

| Boundary | Rule |
|----------|------|
| Raw storage access | Only the generated `persistence/` package reaches the store. |
| Caller dependency | Features depend on declared access patterns and their DTOs, not on schemas. |
| Implementation | Generated from this file at the DATABASE build step; never written by hand. |
| Money | Amounts are stored as integer cents; no floating point at any layer. |
| Aggregates | Counts, sums, and the largest `txn_id` are computed by callers from `list` results; no aggregate operation is declared. |

## Access Patterns

### FEATURE-ACCOUNT-001 — Create an account

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `accounts.create` |
| Compatibility | unchanged |

Input: AccountsCreateInput

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |
| name | TEXT | Account name |

Output: AccountsCreateOutput

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |
| name | TEXT | Account name |

### FEATURE-ACCOUNT-002 — Get an account by code

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `accounts.get` |
| Compatibility | unchanged |

Input: AccountsGetInput

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |

Output: AccountsGetOutput

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |
| name | TEXT | Account name |

### FEATURE-ACCOUNT-003 — Rename an account

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `accounts.update` |
| Match | `account` |
| Compatibility | unchanged |

Input: AccountsUpdateInput

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code (match) |
| name | TEXT | New name |

Output: AccountsUpdateOutput

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |
| name | TEXT | Account name |

### FEATURE-ACCOUNT-004 — Delete an account

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `accounts.delete` |
| Match | `account` |
| Compatibility | unchanged |

Input: AccountsDeleteInput

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |

Output: AccountsDeleteOutput

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |

### FEATURE-ACCOUNT-005 — List accounts by code

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `accounts.list` |
| Kind | list |
| Order | `account` asc |
| Compatibility | unchanged |

Input: AccountsListInput

| Field | Type | Notes |
|-------|------|-------|

Output: AccountsListOutput

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |
| name | TEXT | Account name |

### FEATURE-ACCOUNT-006 — Remove accounts from a code onward

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `accounts.clear` |
| Kind | delete |
| Match | `account >= min_account` |
| Compatibility | unchanged |

Input: AccountsClearInput

| Field | Type | Notes |
|-------|------|-------|
| min_account | TEXT | Lowest code removed; an empty string removes every account |

Output: AccountsClearOutput

| Field | Type | Notes |
|-------|------|-------|

### FEATURE-CATEGORY-001 — Create a category

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `categories.create` |
| Compatibility | unchanged |

Input: CategoriesCreateInput

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |
| description | TEXT | Description |

Output: CategoriesCreateOutput

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |
| description | TEXT | Description |

### FEATURE-CATEGORY-002 — Get a category by code

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `categories.get` |
| Compatibility | unchanged |

Input: CategoriesGetInput

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |

Output: CategoriesGetOutput

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |
| description | TEXT | Description |

### FEATURE-CATEGORY-003 — Change a category description

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `categories.update` |
| Match | `category` |
| Compatibility | unchanged |

Input: CategoriesUpdateInput

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code (match) |
| description | TEXT | New description |

Output: CategoriesUpdateOutput

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |
| description | TEXT | Description |

### FEATURE-CATEGORY-004 — Delete a category

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `categories.delete` |
| Match | `category` |
| Compatibility | unchanged |

Input: CategoriesDeleteInput

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |

Output: CategoriesDeleteOutput

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |

### FEATURE-CATEGORY-005 — List categories by code

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `categories.list` |
| Kind | list |
| Order | `category` asc |
| Compatibility | unchanged |

Input: CategoriesListInput

| Field | Type | Notes |
|-------|------|-------|

Output: CategoriesListOutput

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |
| description | TEXT | Description |

### FEATURE-CATEGORY-006 — Remove categories from a code onward

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `categories.clear` |
| Kind | delete |
| Match | `category >= min_category` |
| Compatibility | unchanged |

Input: CategoriesClearInput

| Field | Type | Notes |
|-------|------|-------|
| min_category | TEXT | Lowest code removed; an empty string removes every category |

Output: CategoriesClearOutput

| Field | Type | Notes |
|-------|------|-------|

### FEATURE-TXN-001 — Create a transaction

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `transactions.create` |
| Compatibility | unchanged |

Input: TransactionsCreateInput

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Caller-assigned id (loaded id, or largest id plus one) |
| date | TEXT | YYYY-MM-DD |
| account | TEXT | Existing account code |
| category | TEXT | Existing category code |
| amount | INTEGER | Cents, signed |
| memo | TEXT | Memo, possibly empty |

Output: TransactionsCreateOutput

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |
| date | TEXT | YYYY-MM-DD |
| account | TEXT | Account code |
| category | TEXT | Category code |
| amount | INTEGER | Cents, signed |
| memo | TEXT | Memo |

### FEATURE-TXN-002 — Get a transaction by id

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `transactions.get` |
| Compatibility | unchanged |

Input: TransactionsGetInput

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |

Output: TransactionsGetOutput

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |
| date | TEXT | YYYY-MM-DD |
| account | TEXT | Account code |
| category | TEXT | Category code |
| amount | INTEGER | Cents, signed |
| memo | TEXT | Memo |

### FEATURE-TXN-003 — Amend a transaction amount

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `transactions.update` |
| Match | `txn_id` |
| Compatibility | unchanged |

Input: TransactionsUpdateInput

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id (match) |
| amount | INTEGER | New amount in cents |

Output: TransactionsUpdateOutput

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |
| date | TEXT | YYYY-MM-DD |
| account | TEXT | Account code |
| category | TEXT | Category code |
| amount | INTEGER | Cents, signed |
| memo | TEXT | Memo |

### FEATURE-TXN-004 — Delete a transaction

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `transactions.delete` |
| Match | `txn_id` |
| Compatibility | unchanged |

Input: TransactionsDeleteInput

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |

Output: TransactionsDeleteOutput

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |

### FEATURE-TXN-005 — List transactions by account, category, or date range

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `transactions.list` |
| Kind | list |
| Match | `account`, `category`, `date >= start_date`, `date <= end_date` |
| Order | `txn_id` asc |
| Compatibility | unchanged |

Input: TransactionsListInput

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Optional filter |
| category | TEXT | Optional filter |
| start_date | TEXT | Optional lower bound, inclusive |
| end_date | TEXT | Optional upper bound, inclusive |

Output: TransactionsListOutput

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |
| date | TEXT | YYYY-MM-DD |
| account | TEXT | Account code |
| category | TEXT | Category code |
| amount | INTEGER | Cents, signed |
| memo | TEXT | Memo |

### FEATURE-TXN-006 — Remove transactions from an id onward

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `transactions.clear` |
| Kind | delete |
| Match | `txn_id >= min_txn_id` |
| Compatibility | unchanged |

Input: TransactionsClearInput

| Field | Type | Notes |
|-------|------|-------|
| min_txn_id | INTEGER | Lowest id removed; 0 removes every transaction |

Output: TransactionsClearOutput

| Field | Type | Notes |
|-------|------|-------|

## Schemas

## `accounts`

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT PK | Code, 1 to 12 characters of A-Z and 0-9 |
| name | TEXT NOT NULL | 1 to 40 characters |

## `categories`

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT PK | Code, 1 to 12 characters of A-Z and 0-9 |
| description | TEXT NOT NULL | 1 to 40 characters |

## `transactions`

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER PK | Transaction id |
| date | TEXT NOT NULL | YYYY-MM-DD |
| account | TEXT NOT NULL REFERENCES accounts(account) | Owning account |
| category | TEXT NOT NULL REFERENCES categories(category) | Category |
| amount | INTEGER NOT NULL | Integer cents, signed, never zero |
| memo | TEXT NOT NULL DEFAULT '' | 0 to 60 characters |

- INDEX (account, date)

## Migrations

Each relational change has one staged record in `migrations/MIGRATION-<AccessPatternId>.md`.
The record carries Alembic `upgrade`/`downgrade` snippets and progresses from `planned` to `built`
only when its DATABASE build story completes. Alembic records deployment application separately.

| Access Pattern | Revision | State |
|----------------|----------|-------|

## Config (.env)

| Key | Type | Required | Notes |
|-----|------|----------|-------|
| DATABASE_URL | string | No | SQLite file path, optionally prefixed `sqlite://`; consulted first |
| DATABASE_PATH | string | No | SQLite file path; consulted when DATABASE_URL is unset; default `data/app.db` |

## File Stores

| Store | Root dir | Notes |
|-------|----------|-------|

## External Services

| Service | Wrapper | Notes |
|---------|---------|-------|

## External Libraries

| Library | Ownership | Distribution | Consumer Contract |
|---------|-----------|--------------|-------------------|

## Programmatic Acceptance

=== AC accounts-create ===
Intent: accounts.create stores a row and returns the declared Output, which a separate get reads back.

from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

code = "ZZCR1"
label = "Create Probe"
with db_session() as db:
    out = db.accounts.create(account=code, name=label)
    assert f(out, "account") == code
    assert f(out, "name") == label
    back = db.accounts.get(account=code)
    assert back is not None
    assert f(back, "name") == label
=== END AC accounts-create ===

=== AC accounts-get ===
Intent: accounts.get returns the stored row for an existing code and None for an absent one.

from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

code = "ZZGET1"
label = "Get Probe"
with db_session() as db:
    db.accounts.create(account=code, name=label)
    row = db.accounts.get(account=code)
    assert row is not None
    assert f(row, "account") == code
    assert f(row, "name") == label
    assert db.accounts.get(account="ZZGETNONE") is None
=== END AC accounts-get ===

=== AC accounts-update ===
Intent: accounts.update changes only the name and the change is visible on a separate read.

from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

code = "ZZUPD1"
before = "Before Name"
after = "After Name"
with db_session() as db:
    db.accounts.create(account=code, name=before)
    out = db.accounts.update(account=code, name=after)
    assert out is not None
    assert f(out, "name") == after
    back = db.accounts.get(account=code)
    assert f(back, "name") == after
    assert f(back, "account") == code
=== END AC accounts-update ===

=== AC accounts-delete ===
Intent: accounts.delete removes the row so a later get finds nothing.

from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

code = "ZZDEL1"
with db_session() as db:
    db.accounts.create(account=code, name="Delete Probe")
    out = db.accounts.delete(account=code)
    assert out is not None
    assert f(out, "account") == code
    assert db.accounts.get(account=code) is None
=== END AC accounts-delete ===

=== AC accounts-list ===
Intent: accounts.list returns rows ordered by account code ascending; two codes created in reverse order appear in sorted order.

from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

codes = ["ZZLA2", "ZZLA1"]
with db_session() as db:
    for c in codes:
        db.accounts.create(account=c, name="List " + c)
    rows = db.accounts.list()
    seen = [f(r, "account") for r in rows if f(r, "account") in codes]
    assert seen == sorted(codes)
    allcodes = [f(r, "account") for r in rows]
    assert allcodes == sorted(allcodes)
=== END AC accounts-list ===

=== AC accounts-clear ===
Intent: accounts.clear removes accounts whose code is at or above the bound, reports a positive count, and leaves none readable.

from persistence.testing import db_session

code = "ZZCLR1"
with db_session() as db:
    db.accounts.create(account=code, name="Clear Probe")
    removed = db.accounts.clear(min_account=code)
    assert removed >= 1
    assert db.accounts.get(account=code) is None
=== END AC accounts-clear ===

=== AC categories-create ===
Intent: categories.create stores a row and returns the declared Output, which a separate get reads back.

from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

code = "ZZCCR1"
text = "Create Probe"
with db_session() as db:
    out = db.categories.create(category=code, description=text)
    assert f(out, "category") == code
    assert f(out, "description") == text
    back = db.categories.get(category=code)
    assert back is not None
    assert f(back, "description") == text
=== END AC categories-create ===

=== AC categories-get ===
Intent: categories.get returns the stored row for an existing code and None for an absent one.

from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

code = "ZZCGET1"
text = "Get Probe"
with db_session() as db:
    db.categories.create(category=code, description=text)
    row = db.categories.get(category=code)
    assert row is not None
    assert f(row, "category") == code
    assert f(row, "description") == text
    assert db.categories.get(category="ZZCGETNONE") is None
=== END AC categories-get ===

=== AC categories-update ===
Intent: categories.update changes the description and the change is visible on a separate read.

from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

code = "ZZCUPD1"
before = "Before Text"
after = "After Text"
with db_session() as db:
    db.categories.create(category=code, description=before)
    out = db.categories.update(category=code, description=after)
    assert out is not None
    assert f(out, "description") == after
    back = db.categories.get(category=code)
    assert f(back, "description") == after
=== END AC categories-update ===

=== AC categories-delete ===
Intent: categories.delete removes the row so a later get finds nothing.

from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

code = "ZZCDEL1"
with db_session() as db:
    db.categories.create(category=code, description="Delete Probe")
    out = db.categories.delete(category=code)
    assert out is not None
    assert f(out, "category") == code
    assert db.categories.get(category=code) is None
=== END AC categories-delete ===

=== AC categories-list ===
Intent: categories.list returns rows ordered by category code ascending; two codes created in reverse order appear in sorted order.

from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

codes = ["ZZCLA2", "ZZCLA1"]
with db_session() as db:
    for c in codes:
        db.categories.create(category=c, description="List " + c)
    rows = db.categories.list()
    seen = [f(r, "category") for r in rows if f(r, "category") in codes]
    assert seen == sorted(codes)
    allcodes = [f(r, "category") for r in rows]
    assert allcodes == sorted(allcodes)
=== END AC categories-list ===

=== AC categories-clear ===
Intent: categories.clear removes categories whose code is at or above the bound, reports a positive count, and leaves none readable.

from persistence.testing import db_session

code = "ZZCCLR1"
with db_session() as db:
    db.categories.create(category=code, description="Clear Probe")
    removed = db.categories.clear(min_category=code)
    assert removed >= 1
    assert db.categories.get(category=code) is None
=== END AC categories-clear ===

=== AC transactions-create ===
Intent: transactions.create stores a signed integer-cents row under the supplied id and returns it, and a separate get reads every column back.

from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

acct, cat = "ZZTA1", "ZZTC1"
tid = 900000001
day = "2026-05-01"
cents = -1234
note = "create probe"
with db_session() as db:
    db.accounts.create(account=acct, name="Txn Account")
    db.categories.create(category=cat, description="Txn Category")
    out = db.transactions.create(txn_id=tid, date=day, account=acct, category=cat, amount=cents, memo=note)
    assert f(out, "txn_id") == tid
    back = db.transactions.get(txn_id=tid)
    assert back is not None
    assert f(back, "date") == day
    assert f(back, "account") == acct
    assert f(back, "category") == cat
    assert f(back, "amount") == cents
    assert f(back, "memo") == note
=== END AC transactions-create ===

=== AC transactions-get ===
Intent: transactions.get returns the stored row for an existing id and None for an absent id.

from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

acct, cat = "ZZTA2", "ZZTC2"
tid = 900000002
cents = 5050
with db_session() as db:
    db.accounts.create(account=acct, name="Txn Account")
    db.categories.create(category=cat, description="Txn Category")
    db.transactions.create(txn_id=tid, date="2026-05-02", account=acct, category=cat, amount=cents, memo="")
    row = db.transactions.get(txn_id=tid)
    assert row is not None
    assert f(row, "amount") == cents
    assert db.transactions.get(txn_id=tid + 1000) is None
=== END AC transactions-get ===

=== AC transactions-update ===
Intent: transactions.update changes only the amount and the change is visible on a separate read.

from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

acct, cat = "ZZTA3", "ZZTC3"
tid = 900000003
day = "2026-05-03"
note = "amend probe"
old, new = 1000, 2500
with db_session() as db:
    db.accounts.create(account=acct, name="Txn Account")
    db.categories.create(category=cat, description="Txn Category")
    db.transactions.create(txn_id=tid, date=day, account=acct, category=cat, amount=old, memo=note)
    out = db.transactions.update(txn_id=tid, amount=new)
    assert out is not None
    assert f(out, "amount") == new
    back = db.transactions.get(txn_id=tid)
    assert f(back, "amount") == new
    assert f(back, "date") == day
    assert f(back, "memo") == note
    assert f(back, "account") == acct
=== END AC transactions-update ===

=== AC transactions-delete ===
Intent: transactions.delete removes the row so a later get finds nothing.

from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

acct, cat = "ZZTA4", "ZZTC4"
tid = 900000004
with db_session() as db:
    db.accounts.create(account=acct, name="Txn Account")
    db.categories.create(category=cat, description="Txn Category")
    db.transactions.create(txn_id=tid, date="2026-05-04", account=acct, category=cat, amount=700, memo="")
    out = db.transactions.delete(txn_id=tid)
    assert out is not None
    assert f(out, "txn_id") == tid
    assert db.transactions.get(txn_id=tid) is None
=== END AC transactions-delete ===

=== AC transactions-list ===
Intent: transactions.list filters by account and inclusive date range and returns rows by txn_id ascending; rows outside the range or on another account are excluded.

from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

acct, other, cat = "ZZTA5", "ZZTA6", "ZZTC5"
rows_in = [(900000012, "2026-06-10"), (900000011, "2026-06-05")]
outside = (900000013, "2026-07-01")
with db_session() as db:
    db.accounts.create(account=acct, name="Txn Account")
    db.accounts.create(account=other, name="Other Account")
    db.categories.create(category=cat, description="Txn Category")
    for tid, day in rows_in:
        db.transactions.create(txn_id=tid, date=day, account=acct, category=cat, amount=100, memo="")
    db.transactions.create(txn_id=outside[0], date=outside[1], account=acct, category=cat, amount=100, memo="")
    db.transactions.create(txn_id=900000014, date="2026-06-07", account=other, category=cat, amount=100, memo="")
    got = db.transactions.list(account=acct, start_date="2026-06-01", end_date="2026-06-30")
    ids = [f(r, "txn_id") for r in got]
    assert ids == sorted(t for t, _ in rows_in)
    assert all(f(r, "account") == acct for r in got)
=== END AC transactions-list ===

=== AC transactions-clear ===
Intent: transactions.clear removes transactions at or above the bound, reports a positive count, and leaves none readable.

from persistence.testing import db_session

acct, cat = "ZZTA7", "ZZTC7"
tid = 900000021
with db_session() as db:
    db.accounts.create(account=acct, name="Txn Account")
    db.categories.create(category=cat, description="Txn Category")
    db.transactions.create(txn_id=tid, date="2026-05-07", account=acct, category=cat, amount=300, memo="")
    removed = db.transactions.clear(min_txn_id=tid)
    assert removed >= 1
    assert db.transactions.get(txn_id=tid) is None
=== END AC transactions-clear ===

## User Acceptance

- None.

## Guardrails

- Only the generated `persistence/` package opens a database driver; application code calls `db.<table>.<operation>(...)`.
- Amounts are integer cents in every column, DTO, and caller; floating point is never used for money.
- Counts, balances, and the next `txn_id` are computed by callers from `list` results, never hardcoded.
- Acceptance criteria never apply DDL, replace DATABASE_URL or DATABASE_PATH, or assume an empty store.
