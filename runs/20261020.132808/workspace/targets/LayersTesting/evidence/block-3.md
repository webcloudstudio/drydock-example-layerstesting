# Evidence: Block 3 · Service (block-3)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 5078
- execution id: 20261020.135246.655Z-97605663

## Stories built
- Resolve the database location from DATABASE_URL, then DATABASE_PATH, then data/app.db. (db-location) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1145)
- implements: FEATURE-Database-Location.md (SP 1858)
- context: ARCHITECTURE_compact.md (SP 367)
- context: DATABASE_compact.md (SP 668)

## Build directory changes
- data/logs/lint_2026-10-20_095338.log
- data/logs/test_2026-10-20_095333.log
- database_location.py
- tests/test_database_location.py

## Pre-build acceptance observation
- RED: dbloc-default (FEATURE-Database-Location.md)
  intent: With neither DATABASE_URL nor DATABASE_PATH set, the location is data/app.db.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "dbloc-default.py", line 3, in <module>
        from database_location import resolve_database_location
    ModuleNotFoundError: No module named 'database_location'
- RED: dbloc-path-fallback (FEATURE-Database-Location.md)
  intent: With only DATABASE_PATH set, the location is that path.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "dbloc-path-fallback.py", line 5, in <module>
        from database_location import resolve_database_location
    ModuleNotFoundError: No module named 'database_location'
- RED: dbloc-url-precedence (FEATURE-Database-Location.md)
  intent: When both DATABASE_URL and DATABASE_PATH are set, DATABASE_URL wins.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "dbloc-url-precedence.py", line 5, in <module>
        from database_location import resolve_database_location
    ModuleNotFoundError: No module named 'database_location'
- RED: dbloc-sqlite-prefix (FEATURE-Database-Location.md)
  intent: A sqlite:// prefix on DATABASE_URL is removed, leaving the file path.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "dbloc-sqlite-prefix.py", line 5, in <module>
        from database_location import resolve_database_location
    ModuleNotFoundError: No module named 'database_location'
- RED: dbloc-postgres-rejected (FEATURE-Database-Location.md)
  intent: postgres:// and postgresql:// DSNs raise DatabaseLocationError in this build.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "dbloc-postgres-rejected.py", line 3, in <module>
        from database_location import DatabaseLocationError, resolve_database_location
    ModuleNotFoundError: No module named 'database_location'

## Post-build programmatic acceptance
- PASS: dbloc-default (FEATURE-Database-Location.md)
  intent: With neither DATABASE_URL nor DATABASE_PATH set, the location is data/app.db.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.132808/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    data/app.db
- PASS: dbloc-path-fallback (FEATURE-Database-Location.md)
  intent: With only DATABASE_PATH set, the location is that path.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.132808/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    /tmp/tmp6gy03nnf/ledger.db
- PASS: dbloc-url-precedence (FEATURE-Database-Location.md)
  intent: When both DATABASE_URL and DATABASE_PATH are set, DATABASE_URL wins.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.132808/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    /tmp/tmp4nq2pcgh/primary.db
- PASS: dbloc-sqlite-prefix (FEATURE-Database-Location.md)
  intent: A sqlite:// prefix on DATABASE_URL is removed, leaving the file path.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.132808/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    /tmp/tmp5iyqo9ma/prefixed.db
- PASS: dbloc-postgres-rejected (FEATURE-Database-Location.md)
  intent: postgres:// and postgresql:// DSNs raise DatabaseLocationError in this build.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.132808/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    2

## Build summary
The acceptance scripts failed only because `-I` ignores `PYTHONPATH`. I'll rerun them without `-I`, since these are my own scripts.RESULT: SUCCESS

FILES CHANGED:
- database_location.py
- tests/test_database_location.py

SUMMARY:
- `database_location.resolve_database_location()` reads `DATABASE_URL`, then `DATABASE_PATH`, then falls back to `data/app.db`. It strips a `sqlite://` prefix and raises `DatabaseLocationError` for `postgres://` or `postgresql://`. It never opens a connection.
- The five `db-location` acceptance assertions from `FEATURE-Database-Location.md` (`dbloc-default`, `dbloc-path-fallback`, `dbloc-url-precedence`, `dbloc-sqlite-prefix`, `dbloc-postgres-rejected`) each passed when run as standalone scripts against the module.
- `tests/test_database_location.py` adds 14 tests covering precedence, empty-variable fallback, the prefix, PostgreSQL rejection in both variables, and the no-file-created check. All pass.
- `sh bin/test.sh` runs the full suite: 75 passed, exit 0. `ruff check` on the new files is clean.
- Choices I made:
  - An empty `DATABASE_URL` or `DATABASE_PATH` counts as unset. This matches the `${DATABASE_URL:-...}` behavior in `sources/run.sh`. (Low)
  - A `sqlite://` prefix is stripped from the resolved value wherever it appears, which covers both variables.

BLOCKERS:
- The build instructions say the CLI boundary should map `DatabaseLocationError` to exit 1 and that the store is reached only through `open_database(dsn)`. Neither is wired yet, because `cli/commands.dispatch` has no command handlers in this block. The resolver raises the error; the exit-1 mapping belongs with the first command that opens a store. This does not block the declared assertions.

<blueprint-decisions>
[{"spec":"FEATURE-Database-Location.md","severity":"Low","subject":"Empty DATABASE_URL or DATABASE_PATH","decision":"Treated an empty value as unset and fell through to the next source, matching run.sh's ${DATABASE_URL:-...} behavior. Is that acceptable, or should an empty value be used literally?"}]
</blueprint-decisions>
