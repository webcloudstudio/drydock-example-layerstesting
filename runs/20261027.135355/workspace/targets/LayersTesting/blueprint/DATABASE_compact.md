<!-- Compacted from DATABASE.md sha256=a9d242b773d4d8d48d088bcadf1977d0c725cd9a9a0dd205e5e466a140c35e12 on 2026-10-27 by drydock build agent -->

Database: LayersTesting (version 20261027 V1). Build order 1. Provides persistence.accounts, persistence.categories, persistence.transactions.

Access: `open_database(dsn)` returns `Database`; `db.<table>.<op>(...)`. Money: integer cents everywhere. No aggregate operations; callers compute counts, sums, next txn_id from list results.

Operations (input -> output; * = match key):
- accounts.create(account, name) -> (account, name)
- accounts.get(account*) -> (account, name) | None
- accounts.update(account*, name) -> (account, name)
- accounts.delete(account*) -> (account)
- accounts.list() -> [(account, name)] order account asc
- accounts.clear(min_account) -> count; removes account >= min_account; "" removes all
- categories.create(category, description) -> (category, description)
- categories.get(category*) -> (category, description) | None
- categories.update(category*, description) -> (category, description)
- categories.delete(category*) -> (category)
- categories.list() -> [(category, description)] order category asc
- categories.clear(min_category) -> count; "" removes all
- transactions.create(txn_id, date, account, category, amount, memo) -> (txn_id, date, account, category, amount, memo)
- transactions.get(txn_id*) -> row | None
- transactions.update(txn_id*, amount) -> row
- transactions.delete(txn_id*) -> (txn_id)
- transactions.list(account?, category?, start_date?, end_date?) -> [row] filters account, category, date>=start_date, date<=end_date; order txn_id asc
- transactions.clear(min_txn_id) -> count; 0 removes all

Schema:
- accounts(account TEXT PK, 1-12 chars A-Z0-9; name TEXT NOT NULL, 1-40 chars)
- categories(category TEXT PK, 1-12 chars A-Z0-9; description TEXT NOT NULL, 1-40 chars)
- transactions(txn_id INTEGER PK; date TEXT YYYY-MM-DD; account FK accounts; category FK categories; amount INTEGER cents signed, never zero; memo TEXT 0-60 chars default ''); INDEX(account, date)

Config: DATABASE_URL (SQLite path, optional sqlite:// prefix, wins), DATABASE_PATH (fallback), default data/app.db.

Guardrails: only the persistence package opens a driver; amounts never float; counts/balances never hardcoded.
