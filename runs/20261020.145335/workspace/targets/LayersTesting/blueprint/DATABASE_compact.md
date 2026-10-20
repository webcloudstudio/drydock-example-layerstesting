<!-- Compacted from DATABASE.md sha256=62b0f32f265ed71e9bea293f8942c2f314b9d4e677ffb81673cc8425ac8625a5 on 2026-10-20 by drydock build agent -->

Database: `persistence.open_database(dsn) -> Database`; `persistence.testing.db_session()` yields a fresh store with `schema.sql` applied. Engines: SQLite (stdlib) and PostgreSQL (`postgres://` / `postgresql://` DSN).
Tables (all amounts INTEGER cents):
- `accounts(account VARCHAR(12) PK, name VARCHAR(40))`
- `categories(category VARCHAR(12) PK, description VARCHAR(40))`
- `transactions(txn_id INTEGER PK, date VARCHAR(10), account VARCHAR(12) -> accounts, category VARCHAR(12) -> categories, amount INTEGER, memo VARCHAR(60) DEFAULT '')`
Operations: `accounts.{list,get,create,update,delete}`, `categories.{list,get,create}`, `transactions.{list,get,create,update,delete}`. Keyword args are the declared input fields (for example `transactions.update(txn_id=, amount=)`). Rows are frozen dataclasses `AccountRow`, `CategoryRow`, `TransactionRow`.
Foreign keys are enforced. Deleting an account with transactions is refused by the command layer, not by the store.
