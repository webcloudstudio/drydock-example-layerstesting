<!-- Compacted from ARCHITECTURE.md sha256=8682d0c9f0d87b106f340b759213c221be6db4c78cc5f1f5efdc9a6642dacc8c on 2026-10-20 by drydock build agent -->

Cash ledger: local single-user CLI. Executable `ledger` at app root; `./ledger <command>`.
Layout: `ledger` (cli dispatch), `cli/` (dispatch, CSV stdout, exit codes, usage errors), `amounts.py` (integer cents <-> two-decimal text), `config.py` (DATABASE_URL, then DATABASE_PATH, then data/app.db), `persistence/` (generated; the only place `sqlite3`/`psycopg` may be imported), `schema.sql` (generated DDL), `bin/test.sh` (POSIX runner with slice selector), `tests/` (pytest), `pyproject.toml` + `uv.lock` + `.venv/`.
Stack: Python >=3.11 (pytest); SQLite default; PostgreSQL when DSN is postgres:// or postgresql:// (psycopg[binary]); network only to the PostgreSQL server named by DATABASE_URL.
Decisions: money as integer cents, no floats; each command = one DB transaction via `open_database(dsn)`; manifest declares >=3.11, pytest, psycopg[binary]; uv.lock committed.
Acceptance: `scaffold-pyproject` (requires-python >=3.11; pytest and psycopg present), `scaffold-environment` (uv.lock, .venv, pyproject.toml exist).
