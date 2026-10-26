<!-- Compacted from ARCHITECTURE.md sha256=2f2974f8ae554bacbac8d6a8445ea421229d545accadc839927e9443cb15e501 on 2026-10-25 by drydock build agent -->

# ARCHITECTURE contract surface: LayersTesting

- Executable `ledger` at application root; calls `cli.main`, exits with its return value.
- Packages: `cli/` (dispatch, errors, validators, money, output), `cli/commands/` (one module per command, self-registering), `persistence/` (generated from DATABASE.md, sole importer of DB drivers), `tests/` (pytest; `conftest.py` exposes `db_session` and `cli_runner`).
- `bin/test.sh`: POSIX sh; activates `.venv`, runs `pytest -q` from root; exit 0 only if all tests pass.
- Config: `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`. Resolved in `cli/database` via `persistence.open_database`.
- Money: integer cents at every layer. No floats.
- Exit codes: 0 success, 1 operational, 2 usage, 3 rejected, 4 not found. Stdout is CSV (`\n`, no quoting); diagnostics to stderr.
- Commands validate full input and business rules before the first write; the dispatcher checks arity before opening the database.
- Guardrails: only `persistence/` imports a DB driver; no network; nothing under `sources/` is modified or read by application code.
