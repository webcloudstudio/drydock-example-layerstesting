# DATABASE: LayersTesting

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Persistence stores and typed interfaces for the LayersTesting cash ledger. |
| Depends On | ARCHITECTURE.md |
| Provides | persistence.open_database |
| Build Order | 1 |

## Persistence Boundary

| Boundary | Rule |
|----------|------|
| Raw storage access | Only the generated `persistence/` package reaches the store. |
| Caller dependency | Features depend on declared access patterns and their DTOs, not on schemas. |
| Implementation | Generated from this file at the DATABASE build step; never written by hand. |
| Money | Amounts are integer cents in the `amount` column; no floating point at any layer. |
| Shared ownership | No single command owns a table, so every pattern names `DATABASE.md` as Owner and any Blueprint may cite it. |

## Access Patterns

Row counts are taken as the length of the matching `list`. The highest `txn_id` is the last row of `transactions.list` (ordered ascending). Balances, category totals and monthly totals are computed by callers in integer cents from listed rows.

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

Output: AccountRow

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
| Match | `account` |
| Compatibility | unchanged |

Input: AccountsGetInput

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |

Output: AccountRow

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |
| name | TEXT | Account name |

### FEATURE-ACCOUNT-003 — List all accounts by code

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `accounts.list` |
| Order | `account` asc |
| Compatibility | unchanged |

Input: AccountsListInput

| Field | Type | Notes |
|-------|------|-------|

Output: AccountRow

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |
| name | TEXT | Account name |

### FEATURE-ACCOUNT-004 — Rename an account

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
| account | TEXT | Account code |
| name | TEXT | New name |

Output: AccountRow

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Account code |
| name | TEXT | Account name |

### FEATURE-ACCOUNT-005 — Delete an account

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

### FEATURE-ACCOUNT-006 — Delete every account

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `accounts.delete_all` |
| Kind | delete |
| Compatibility | unchanged |

Input: AccountsDeleteAllInput

| Field | Type | Notes |
|-------|------|-------|

Output: AccountsDeleteAllOutput

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
| description | TEXT | Category description |

Output: CategoryRow

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |
| description | TEXT | Category description |

### FEATURE-CATEGORY-002 — Get a category by code

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `categories.get` |
| Match | `category` |
| Compatibility | unchanged |

Input: CategoriesGetInput

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |

Output: CategoryRow

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |
| description | TEXT | Category description |

### FEATURE-CATEGORY-003 — List all categories by code

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `categories.list` |
| Order | `category` asc |
| Compatibility | unchanged |

Input: CategoriesListInput

| Field | Type | Notes |
|-------|------|-------|

Output: CategoryRow

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |
| description | TEXT | Category description |

### FEATURE-CATEGORY-004 — Update a category description

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
| category | TEXT | Category code |
| description | TEXT | New description |

Output: CategoryRow

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT | Category code |
| description | TEXT | Category description |

### FEATURE-CATEGORY-005 — Delete a category

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

### FEATURE-CATEGORY-006 — Delete every category

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `categories.delete_all` |
| Kind | delete |
| Compatibility | unchanged |

Input: CategoriesDeleteAllInput

| Field | Type | Notes |
|-------|------|-------|

Output: CategoriesDeleteAllOutput

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
| txn_id | INTEGER | Caller-assigned id (file id on load, max+1 on post) |
| date | TEXT | YYYY-MM-DD |
| account | TEXT | Account code |
| category | TEXT | Category code |
| amount | INTEGER | Signed integer cents |
| memo | TEXT | Memo, possibly empty |

Output: TransactionRow

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |
| date | TEXT | YYYY-MM-DD |
| account | TEXT | Account code |
| category | TEXT | Category code |
| amount | INTEGER | Signed integer cents |
| memo | TEXT | Memo |

### FEATURE-TXN-002 — Get a transaction by id

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `transactions.get` |
| Match | `txn_id` |
| Compatibility | unchanged |

Input: TransactionsGetInput

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |

Output: TransactionRow

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |
| date | TEXT | YYYY-MM-DD |
| account | TEXT | Account code |
| category | TEXT | Category code |
| amount | INTEGER | Signed integer cents |
| memo | TEXT | Memo |

### FEATURE-TXN-003 — List transactions, optionally by account or category

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | read |
| Repository operation | `transactions.list` |
| Match | `account`, `category` |
| Order | `txn_id` asc |
| Compatibility | unchanged |

Input: TransactionsListInput

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT | Optional account filter |
| category | TEXT | Optional category filter |

Output: TransactionRow

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |
| date | TEXT | YYYY-MM-DD |
| account | TEXT | Account code |
| category | TEXT | Category code |
| amount | INTEGER | Signed integer cents |
| memo | TEXT | Memo |

### FEATURE-TXN-004 — Change a transaction amount

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `transactions.update_amount` |
| Kind | update |
| Match | `txn_id` |
| Compatibility | unchanged |

Input: TransactionsUpdateAmountInput

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |
| amount | INTEGER | New signed integer cents |

Output: TransactionRow

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER | Transaction id |
| date | TEXT | YYYY-MM-DD |
| account | TEXT | Account code |
| category | TEXT | Category code |
| amount | INTEGER | Signed integer cents |
| memo | TEXT | Memo |

### FEATURE-TXN-005 — Delete a transaction

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

### FEATURE-TXN-006 — Delete every transaction

| Field | Value |
|-------|-------|
| Owner | DATABASE.md |
| Access | write |
| Repository operation | `transactions.delete_all` |
| Kind | delete |
| Compatibility | unchanged |

Input: TransactionsDeleteAllInput

| Field | Type | Notes |
|-------|------|-------|

Output: TransactionsDeleteAllOutput

| Field | Type | Notes |
|-------|------|-------|

## Schemas

## `accounts`

| Field | Type | Notes |
|-------|------|-------|
| account | TEXT PK | Account code, 1 to 12 characters of A-Z and 0-9 |
| name | TEXT NOT NULL | Account name, 1 to 40 characters |

## `categories`

| Field | Type | Notes |
|-------|------|-------|
| category | TEXT PK | Category code, 1 to 12 characters of A-Z and 0-9 |
| description | TEXT NOT NULL | Description, 1 to 40 characters |

## `transactions`

| Field | Type | Notes |
|-------|------|-------|
| txn_id | INTEGER PK | Transaction id |
| date | TEXT NOT NULL | YYYY-MM-DD |
| account | TEXT NOT NULL REFERENCES accounts(account) | Owning account |
| category | TEXT NOT NULL REFERENCES categories(category) | Category |
| amount | INTEGER NOT NULL | Signed integer cents, never zero |
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
| DATABASE_URL | string | No | PostgreSQL DSN or SQLite path; empty is treated as unset |
| DATABASE_PATH | string | No | Used when DATABASE_URL is unset; default `data/app.db` |

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
Intent: accounts.create stores a row and returns it, readable afterwards.

from persistence.testing import db_session

code = "ZQACC01"
name = "Create Test"
with db_session() as db:
    row = db.accounts.create(account=code, name=name)
    assert row.account == code
    assert row.name == name
    back = db.accounts.get(account=code)
    assert back is not None
    assert back.account == code and back.name == name
=== END AC accounts-create ===

=== AC accounts-get ===
Intent: accounts.get returns the row for a present code and None for an absent one.

from persistence.testing import db_session

code = "ZQACC02"
absent = "ZQNONE02"
name = "Get Test"
with db_session() as db:
    db.accounts.create(account=code, name=name)
    row = db.accounts.get(account=code)
    assert row is not None and row.name == name
    assert db.accounts.get(account=absent) is None
=== END AC accounts-get ===

=== AC accounts-list ===
Intent: accounts.list returns accounts ordered by code in byte order.

from persistence.testing import db_session

codes = ["ZQACC3B", "ZQACC39", "ZQACC3A"]
with db_session() as db:
    for c in codes:
        db.accounts.create(account=c, name="List " + c)
    listed = [r.account for r in db.accounts.list()]
    mine = [c for c in listed if c in codes]
    assert mine == sorted(codes)
    assert listed == sorted(listed)
=== END AC accounts-list ===

=== AC accounts-update ===
Intent: accounts.update changes the name only and returns the updated row; an absent code returns None.

from persistence.testing import db_session

code = "ZQACC04"
absent = "ZQNONE04"
old_name = "Before"
new_name = "After"
with db_session() as db:
    db.accounts.create(account=code, name=old_name)
    row = db.accounts.update(account=code, name=new_name)
    assert row is not None
    assert row.account == code and row.name == new_name
    back = db.accounts.get(account=code)
    assert back.name == new_name
    assert db.accounts.update(account=absent, name=new_name) is None
=== END AC accounts-update ===

=== AC accounts-delete ===
Intent: accounts.delete removes the row so a later get returns None.

from persistence.testing import db_session

code = "ZQACC05"
with db_session() as db:
    db.accounts.create(account=code, name="Delete Test")
    assert db.accounts.get(account=code) is not None
    db.accounts.delete(account=code)
    assert db.accounts.get(account=code) is None
=== END AC accounts-delete ===

=== AC accounts-delete-all ===
Intent: accounts.delete_all removes every account once dependent rows are gone.

from persistence.testing import db_session

with db_session() as db:
    db.accounts.create(account="ZQACC06", name="Delete All")
    db.transactions.delete_all()
    db.categories.delete_all()
    db.accounts.delete_all()
    assert db.accounts.list() == []
=== END AC accounts-delete-all ===

=== AC categories-create ===
Intent: categories.create stores a row and returns it, readable afterwards.

from persistence.testing import db_session

code = "ZQCAT01"
desc = "Create Test"
with db_session() as db:
    row = db.categories.create(category=code, description=desc)
    assert row.category == code and row.description == desc
    back = db.categories.get(category=code)
    assert back is not None and back.description == desc
=== END AC categories-create ===

=== AC categories-get ===
Intent: categories.get returns the row for a present code and None for an absent one.

from persistence.testing import db_session

code = "ZQCAT02"
absent = "ZQNONE02"
desc = "Get Test"
with db_session() as db:
    db.categories.create(category=code, description=desc)
    row = db.categories.get(category=code)
    assert row is not None and row.description == desc
    assert db.categories.get(category=absent) is None
=== END AC categories-get ===

=== AC categories-list ===
Intent: categories.list returns categories ordered by code in byte order.

from persistence.testing import db_session

codes = ["ZQCAT3B", "ZQCAT39", "ZQCAT3A"]
with db_session() as db:
    for c in codes:
        db.categories.create(category=c, description="List " + c)
    listed = [r.category for r in db.categories.list()]
    mine = [c for c in listed if c in codes]
    assert mine == sorted(codes)
    assert listed == sorted(listed)
=== END AC categories-list ===

=== AC categories-update ===
Intent: categories.update changes the description and returns the updated row.

from persistence.testing import db_session

code = "ZQCAT04"
new_desc = "After"
with db_session() as db:
    db.categories.create(category=code, description="Before")
    row = db.categories.update(category=code, description=new_desc)
    assert row is not None and row.description == new_desc
    assert db.categories.get(category=code).description == new_desc
=== END AC categories-update ===

=== AC categories-delete ===
Intent: categories.delete removes the row so a later get returns None.

from persistence.testing import db_session

code = "ZQCAT05"
with db_session() as db:
    db.categories.create(category=code, description="Delete Test")
    db.categories.delete(category=code)
    assert db.categories.get(category=code) is None
=== END AC categories-delete ===

=== AC categories-delete-all ===
Intent: categories.delete_all removes every category once dependent transactions are gone.

from persistence.testing import db_session

with db_session() as db:
    db.categories.create(category="ZQCAT06", description="Delete All")
    db.transactions.delete_all()
    db.categories.delete_all()
    assert db.categories.list() == []
=== END AC categories-delete-all ===

=== AC transactions-create ===
Intent: transactions.create stores every column as given and the row reads back.

from persistence.testing import db_session

acct = "ZQTXA01"
cat = "ZQTXC01"
txn_id = 900001
date = "2026-04-01"
amount = -1234
memo = "round trip"
with db_session() as db:
    db.accounts.create(account=acct, name="Txn Account")
    db.categories.create(category=cat, description="Txn Category")
    row = db.transactions.create(
        txn_id=txn_id, date=date, account=acct, category=cat, amount=amount, memo=memo
    )
    assert row.txn_id == txn_id and row.amount == amount
    back = db.transactions.get(txn_id=txn_id)
    assert back is not None
    assert (back.date, back.account, back.category, back.amount, back.memo) == (
        date, acct, cat, amount, memo
    )
    assert isinstance(back.amount, int)
=== END AC transactions-create ===

=== AC transactions-get ===
Intent: transactions.get returns a present row and None for an absent id.

from persistence.testing import db_session

acct = "ZQTXA02"
cat = "ZQTXC02"
txn_id = 900002
absent_id = 900999
with db_session() as db:
    db.accounts.create(account=acct, name="Txn Account")
    db.categories.create(category=cat, description="Txn Category")
    db.transactions.create(
        txn_id=txn_id, date="2026-04-02", account=acct, category=cat, amount=500, memo=""
    )
    row = db.transactions.get(txn_id=txn_id)
    assert row is not None and row.memo == ""
    assert db.transactions.get(txn_id=absent_id) is None
=== END AC transactions-get ===

=== AC transactions-list ===
Intent: transactions.list filters by account and category and orders by txn_id ascending.

from persistence.testing import db_session

a1, a2 = "ZQTXA03", "ZQTXA33"
c1, c2 = "ZQTXC03", "ZQTXC33"
ids = [900013, 900011, 900012]
with db_session() as db:
    for a in (a1, a2):
        db.accounts.create(account=a, name="Txn " + a)
    for c in (c1, c2):
        db.categories.create(category=c, description="Cat " + c)
    db.transactions.create(txn_id=ids[0], date="2026-04-03", account=a1, category=c1, amount=100, memo="x")
    db.transactions.create(txn_id=ids[1], date="2026-04-03", account=a1, category=c2, amount=200, memo="y")
    db.transactions.create(txn_id=ids[2], date="2026-04-03", account=a2, category=c1, amount=300, memo="z")
    by_account = [r.txn_id for r in db.transactions.list(account=a1)]
    assert by_account == sorted([ids[0], ids[1]])
    by_category = [r.txn_id for r in db.transactions.list(category=c1)]
    assert by_category == sorted([ids[0], ids[2]])
    both = [r.txn_id for r in db.transactions.list(account=a1, category=c1)]
    assert both == [ids[0]]
    everything = [r.txn_id for r in db.transactions.list()]
    assert everything == sorted(everything)
    assert set(ids) <= set(everything)
=== END AC transactions-list ===

=== AC transactions-update-amount ===
Intent: transactions.update_amount changes only the amount and returns the updated row.

from persistence.testing import db_session

acct = "ZQTXA04"
cat = "ZQTXC04"
txn_id = 900004
absent_id = 900998
old_amount = 1000
new_amount = 2550
with db_session() as db:
    db.accounts.create(account=acct, name="Txn Account")
    db.categories.create(category=cat, description="Txn Category")
    db.transactions.create(
        txn_id=txn_id, date="2026-04-04", account=acct, category=cat, amount=old_amount, memo="keep"
    )
    row = db.transactions.update_amount(txn_id=txn_id, amount=new_amount)
    assert row is not None and row.amount == new_amount
    back = db.transactions.get(txn_id=txn_id)
    assert back.amount == new_amount
    assert (back.date, back.account, back.category, back.memo) == ("2026-04-04", acct, cat, "keep")
    assert db.transactions.update_amount(txn_id=absent_id, amount=new_amount) is None
=== END AC transactions-update-amount ===

=== AC transactions-delete ===
Intent: transactions.delete removes the row so a later get returns None.

from persistence.testing import db_session

acct = "ZQTXA05"
cat = "ZQTXC05"
txn_id = 900005
with db_session() as db:
    db.accounts.create(account=acct, name="Txn Account")
    db.categories.create(category=cat, description="Txn Category")
    db.transactions.create(
        txn_id=txn_id, date="2026-04-05", account=acct, category=cat, amount=700, memo=""
    )
    db.transactions.delete(txn_id=txn_id)
    assert db.transactions.get(txn_id=txn_id) is None
=== END AC transactions-delete ===

=== AC transactions-delete-all ===
Intent: transactions.delete_all removes every transaction row.

from persistence.testing import db_session

acct = "ZQTXA06"
cat = "ZQTXC06"
with db_session() as db:
    db.accounts.create(account=acct, name="Txn Account")
    db.categories.create(category=cat, description="Txn Category")
    db.transactions.create(
        txn_id=900006, date="2026-04-06", account=acct, category=cat, amount=100, memo=""
    )
    db.transactions.delete_all()
    assert db.transactions.list() == []
=== END AC transactions-delete-all ===

## User Acceptance

- None.

## Guardrails

- Only the generated `persistence/` package reaches the store; no caller imports a database driver.
- Amounts are stored as integer cents and never as floating point.
- Report aggregation is computed by callers from stored rows; no report value is stored or embedded.
