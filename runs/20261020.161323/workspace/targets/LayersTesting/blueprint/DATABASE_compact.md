<!-- Compacted from DATABASE.md sha256=ff2f418d172d52e874121e5a5ae842b9b7bcba38f70b6718f8f7cd77643be755 on 2026-10-20 by drydock build agent -->

Database DSN precedence: `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`. PostgreSQL DSNs use PostgreSQL; other values use SQLite paths, including `sqlite://`.

Schema tables: `accounts(account PK, name)`, `categories(category PK, description)`, and `transactions(txn_id PK, date, account FK, category FK, amount integer cents, memo)`. Foreign keys are enforced.

Persistence access is exclusively through `persistence.open_database(dsn)` and declared typed table operations. Initialization is idempotent and supports recreating all tables. Writes are atomic and fully validated before mutation. No floating-point monetary values.
