<!-- Compacted from DATABASE.md sha256=b25b0cd967ed40f31ca38e2a6dfb2c0b86d8e964b7c7b5aa8521387a399a2532 on 2026-10-25 by drydock build agent -->

Tables: accounts(account VARCHAR(12) PK, name VARCHAR(40) NOT NULL); categories(category VARCHAR(12) PK, description VARCHAR(40) NOT NULL); transactions(txn_id INTEGER PK, date VARCHAR(10) NOT NULL, account FK accounts, category FK categories, amount INTEGER NOT NULL signed cents, memo VARCHAR(60) NOT NULL DEFAULT '').
Operations (db.<table>.<name>): accounts.get/list(order account asc)/create/update(match account)/delete(match account)/clear(first_code, delete where account >= first_code); categories.get/list(order category asc)/create/clear(first_code); transactions.get/list(order txn_id asc; optional account, category)/create/update(txn_id; sets amount)/delete(txn_id)/clear(min_id, delete where txn_id >= min_id).
Output rows are frozen dataclasses named <Table><Op>Output. No aggregate operation exists; counts, balances and totals come from list results.
Config: DATABASE_URL (PostgreSQL DSN or sqlite path/sqlite://), else DATABASE_PATH, else data/app.db.
Schema is applied once at the DATABASE step, never at startup.
