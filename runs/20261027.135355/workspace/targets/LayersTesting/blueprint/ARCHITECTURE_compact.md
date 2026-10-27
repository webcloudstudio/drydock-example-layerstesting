<!-- Compacted from ARCHITECTURE.md sha256=5c919fe47ef8fc30da6c74103c97b0528a77ab903c7c0e7a51838b17c57c163d on 2026-10-27 by drydock build agent -->

Foundation contract (foundation-python):
- Python >=3.11; deps in pyproject.toml; uv.lock committed; .venv local (gitignored).
- bin/test.sh (POSIX sh): runs `pytest -q` from root; exit status = verdict.
- conftest.py fixtures: db_session (delegates to persistence.testing.db_session), cli_runner (delegates to cli.testing.cli_runner).
- ledger_core.config.database_path() -> str: DATABASE_URL (strip leading "sqlite://"), else DATABASE_PATH, else "data/app.db"; empty = unset.
- ledger_core.errors: LedgerError(Exception) with exit_code:int; Rejected=3, NotFound=4, Operational=1.
- Boundary: no module under ledger_core/ or cli/ imports sqlite3/psycopg/psycopg2; no float calls or float literals in ledger_core/.
