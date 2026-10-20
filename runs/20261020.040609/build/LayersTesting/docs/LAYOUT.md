# Project Layout and Technology Stack

## Technology Stack

- Python 3.11 or newer, with `pytest` as the test runner.
- `psycopg[binary]` for PostgreSQL, reached only through the shipped persistence library.
- `uv` manages the environment (`.venv/`) and the committed lockfile (`uv.lock`).

## Package Layout

| Path | Owner | Status |
|------|-------|--------|
| `pyproject.toml` | language foundation | Dependency manifest (Python >= 3.11, pytest, psycopg[binary]) |
| `uv.lock` | language foundation | Committed lockfile |
| `.venv/` | language foundation | Created by `uv venv`, not committed |
| `tests/` | project suite | pytest tests, one behavior per test |
| `docs/` | project docs | This file |
| `ledger` | cli | Executable at the application root (later block) |
| `cli/` | cli | Command dispatch (later block) |
| `amounts.py` | amounts | Integer-cent conversion (later block) |
| `config.py` | config | `DATABASE_URL` / `DATABASE_PATH` resolution (later block) |
| `persistence/` | generated | Shipped persistence library and generated declaration (later block) |
| `schema.sql` | generated | Generated DDL (later block) |

Later stories add packages beside these entries. They do not replace the manifest, lockfile,
environment, or test runner contracts recorded here.

## Commands

```sh
uv sync            # create or update .venv from uv.lock
uv run pytest -q   # run the project test suite
```
