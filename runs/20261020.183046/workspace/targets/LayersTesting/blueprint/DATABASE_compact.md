<!-- Compacted from DATABASE.md sha256=303bb0ec282f9b3375363468a39a228230a2468245669b4366732e6dfd6eb647 on 2026-10-20 by drydock build agent -->

Persistence uses generated `persistence.open_database(dsn)` only; DSN precedence is `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`. SQLite is required locally; PostgreSQL remains supported. Amounts are integer cents.

Tables:
- `accounts(account TEXT PRIMARY KEY NOT NULL, name VARCHAR(40) NOT NULL)`
- `categories(category TEXT PRIMARY KEY NOT NULL, description VARCHAR(40) NOT NULL)`
- `transactions(txn_id INTEGER PRIMARY KEY NOT NULL, date TEXT NOT NULL, account TEXT NOT NULL REFERENCES accounts(account), category TEXT NOT NULL REFERENCES categories(category), amount INTEGER NOT NULL, memo VARCHAR(60) NOT NULL)`

Declared operations:
- accounts: `list()`, `create(account, name)`, `get(account)`, `update(account, name)`, `delete(account)`
- categories: `list()`, `get(category)`
- transactions: `list()`, `create(txn_id, date, account, category, amount, memo)`, `get(txn_id)`, `update(txn_id, amount)`, `delete(txn_id)`

Schema creation is idempotent via generated `schema.sql`; application startup must not create or alter schema. Application code must not import database drivers, use floating point for amounts, or bypass repositories.
