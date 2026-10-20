<!-- Compacted from DATABASE.md sha256=c2c7a21823268140462ca3271d2e0ad6d6a29a891ae8e7105a8bbc59e8d9c5d7 on 2026-10-20 by drydock build agent -->

Store: SQLite via open_database(dsn) (plain path or sqlite://); PostgreSQL when DSN is postgresql://. Tables:
- accounts(account VARCHAR(12) PK, name VARCHAR(40))
- categories(category VARCHAR(12) PK, description VARCHAR(40))
- transactions(txn_id INTEGER PK, date TEXT, account VARCHAR(12) FK->accounts, category VARCHAR(12) FK->categories, amount INTEGER cents signed, memo VARCHAR(60) DEFAULT '')
Operations (db.<table>.<verb>): accounts.{create,get,list,update,delete}; categories.{create,get,list}; transactions.{create,get,list,update(txn_id,amount),delete}. get returns a row dataclass or None; update/delete return rowcount; create returns the key; unlisted verbs raise UnknownOperation; FK violations raise PersistenceError.
Schema applied from schema.sql (CREATE IF NOT EXISTS). Money is INTEGER cents only.
