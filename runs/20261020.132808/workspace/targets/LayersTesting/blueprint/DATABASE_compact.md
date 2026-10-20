<!-- Compacted from DATABASE.md sha256=650916af259dc734c7ccc409d6e94a7ac33236f48bcbcafce67250823e473913 on 2026-10-20 by drydock build agent -->

Tables (SQLite DDL, schema.sql, CREATE IF NOT EXISTS):
- accounts(account VARCHAR(12) PK NOT NULL, name VARCHAR(40) NOT NULL)
- categories(category VARCHAR(12) PK NOT NULL, description VARCHAR(40) NOT NULL)
- transactions(txn_id INTEGER PK NOT NULL, date VARCHAR(10) NOT NULL, account VARCHAR(12) NOT NULL REFERENCES accounts(account), category VARCHAR(12) NOT NULL REFERENCES categories(category), amount INTEGER NOT NULL [integer cents], memo VARCHAR(60) NOT NULL)
- Indexes: transactions_account_idx, transactions_category_idx

Python surface: persistence.open_database(dsn) -> Database; persistence.testing.db_session(dsn=None) context manager applies schema.sql to a fresh store.
Exports: Database, PersistenceError, UnknownOperation, SCHEMA, open_database.
Operations (db.<table>.<verb>(**kwargs)):
- accounts.create(account, name) -> identity; accounts.get(account) -> AccountRow|None; accounts.list() -> list[AccountRow]; accounts.update(account, name) -> rowcount; accounts.delete(account) -> rowcount
- categories.create(category, description); categories.get(category); categories.list()
- transactions.create(txn_id, date, account, category, amount, memo); transactions.get(txn_id); transactions.list(); transactions.update(txn_id, amount) -> rowcount; transactions.delete(txn_id) -> rowcount
Undeclared verb -> UnknownOperation. Unknown kwarg, FK violation, duplicate key, or driver failure -> PersistenceError.
DSN: bare path or sqlite:// selects SQLite (foreign keys ON); postgres:// selects PostgreSQL (needs psycopg, not in dependencies).
SQLite does not enforce VARCHAR length.
