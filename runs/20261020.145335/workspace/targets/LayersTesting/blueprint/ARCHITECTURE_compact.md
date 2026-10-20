<!-- Compacted from ARCHITECTURE.md sha256=37958524fe72be8e957a73343c887c81eed8f528dd52a8f693f17335adb60003 on 2026-10-20 by drydock build agent -->

Project: `ledger` (Python >=3.11, uv, `package = false`). Runtime dep: `psycopg[binary]>=3.1`. Dev: `pytest>=8.0`. Lock: `uv.lock`. Env: `.venv/`.
Launchers (POSIX sh): `bin/sync.sh` (uv venv + `uv sync --locked`), `bin/test.sh` (activates `.venv`, runs `pytest -q`).
Layout: `ledger` (app-root launcher -> `cli.main` under `.venv`), `config.py` (DB target from env: `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`; never opens connection), `cli/` (no DB access), `commands/` (one tx per command; calls `db.<table>.<verb>(...)` via `persistence.open_database`), `persistence/` + `schema.sql` (generated from DATABASE.md), `tests/`.
Boundaries: cli -> commands -> persistence. Only `persistence/sqlite.py` and `persistence/postgres.py` import drivers. Only `ledger load` reads seed files.
Engines: SQLite (stdlib); PostgreSQL selected by `postgres://` / `postgresql://` DSN.
Balance: negative balance rolls back, exit 3. Money is integer cents everywhere.
