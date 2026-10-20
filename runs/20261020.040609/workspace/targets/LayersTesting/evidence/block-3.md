# Evidence: Block 3 · Service (block-3)

- block type: block
- date: 2026-10-20
- resulting state: closed/failed
- story points (combined assembled cost): 4260
- execution id: 20261020.043648.991Z-80fda342

## Stories built
- Select the database from DATABASE_URL, DATABASE_PATH, or data/app.db. (foundation-002) [story]

## Acceptance tooling authorization
- FEATURE-DATABASE-SELECTION.md#db-selection-unreachable: python-package=psycopg; scope=runtime; authorization=existing Target environment

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1145)
- implements: FEATURE-DATABASE-SELECTION.md (SP 1266)
- context: ARCHITECTURE_compact.md (SP 450)
- context: DATABASE_compact.md (SP 370)

## Build directory changes
- config.py
- tests/test_database_selection.py

## Pre-build acceptance observation
- RED: db-selection-url-precedence (FEATURE-DATABASE-SELECTION.md)
  intent: DATABASE_URL wins over DATABASE_PATH when both are set, and the value is returned unchanged.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "db-selection-url-precedence.py", line 4, in <module>
        from config import resolve_dsn
    ModuleNotFoundError: No module named 'config'
- RED: db-selection-path-fallback (FEATURE-DATABASE-SELECTION.md)
  intent: DATABASE_PATH is used when DATABASE_URL is unset or empty.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "db-selection-path-fallback.py", line 4, in <module>
        from config import resolve_dsn
    ModuleNotFoundError: No module named 'config'
- RED: db-selection-postgres-dsn (FEATURE-DATABASE-SELECTION.md)
  intent: A PostgreSQL DSN in DATABASE_URL is returned unchanged for the persistence library to select the engine.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "db-selection-postgres-dsn.py", line 1, in <module>
        from config import resolve_dsn
    ModuleNotFoundError: No module named 'config'
- RED: db-selection-default (FEATURE-DATABASE-SELECTION.md)
  intent: With neither variable set, resolution returns a non-empty database location.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "db-selection-default.py", line 1, in <module>
        from config import resolve_dsn
    ModuleNotFoundError: No module named 'config'
- RED: db-selection-unreachable (FEATURE-DATABASE-SELECTION.md)
  intent: An unreachable PostgreSQL server raises PersistenceError instead of returning a database.
  return code: 1
  stderr:
    --- drydock: progress ---
    cases: pass=0 fail=1 total=1 from=e.ConnStatus._member_map_
    --- drydock: end progress ---
    --- drydock: values at failure ---
      last_ex = OperationalError('connection failed: connection to server at "127.0.0.1", port 1 failed: Connection refused\n\tIs the server running on that host and accepting TCP/IP connections?')
    --- drydock: end values ---
    Traceback (most recent call last):
      File "db-selection-unreachable.py", line 6, in <module>
        db.accounts.list()
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/persistence/db.py", line 186, in <lambda>
        return lambda **arguments: self._database.run(operation, arguments)
                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/persistence/db.py", line 244, in run
        connection = self._driver.connect()
                     ^^^^^^^^^^^^^^^^^^^^^^
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/persistence/postgres.py", line 47, in connect
        connection = _driver_module().connect(self._dsn)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/.venv/lib/python3.11/site-packages/psycopg/connection.py", line 126, in connect
        raise last_ex.with_traceback(None)
    psycopg.OperationalError: connection failed: connection to server at "127.0.0.1", port 1 failed: Connection refused
    	Is the server running on that host and accepting TCP/IP connections?

## Post-build programmatic acceptance
- PASS: db-selection-url-precedence (FEATURE-DATABASE-SELECTION.md)
  intent: DATABASE_URL wins over DATABASE_PATH when both are set, and the value is returned unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: db-selection-path-fallback (FEATURE-DATABASE-SELECTION.md)
  intent: DATABASE_PATH is used when DATABASE_URL is unset or empty.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: db-selection-postgres-dsn (FEATURE-DATABASE-SELECTION.md)
  intent: A PostgreSQL DSN in DATABASE_URL is returned unchanged for the persistence library to select the engine.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: db-selection-default (FEATURE-DATABASE-SELECTION.md)
  intent: With neither variable set, resolution returns a non-empty database location.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- FAIL: db-selection-unreachable (FEATURE-DATABASE-SELECTION.md)
  intent: An unreachable PostgreSQL server raises PersistenceError instead of returning a database.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 1
  stderr:
    --- drydock: progress ---
    cases: pass=0 fail=1 total=1 from=e.ConnStatus._member_map_
    --- drydock: end progress ---
    --- drydock: values at failure ---
      last_ex = OperationalError('connection failed: connection to server at "127.0.0.1", port 1 failed: Connection refused\n\tIs the server running on that host and accepting TCP/IP connections?')
    --- drydock: end values ---
    Traceback (most recent call last):
      File "db-selection-unreachable.py", line 6, in <module>
        db.accounts.list()
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/persistence/db.py", line 186, in <lambda>
        return lambda **arguments: self._database.run(operation, arguments)
                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/persistence/db.py", line 244, in run
        connection = self._driver.connect()
                     ^^^^^^^^^^^^^^^^^^^^^^
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/persistence/postgres.py", line 47, in connect
        connection = _driver_module().connect(self._dsn)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/.venv/lib/python3.11/site-packages/psycopg/connection.py", line 126, in connect
        raise last_ex.with_traceback(None)
    psycopg.OperationalError: connection failed: connection to server at "127.0.0.1", port 1 failed: Connection refused
    	Is the server running on that host and accepting TCP/IP connections?

## Repair attempts
- attempt 0 (initial build): failed; 4/5 checks; 0/1 cases model=claude-haiku-5-5; execution 20261020.043345.364Z-7e9a28c0; reason: programmatic acceptance failed: db-selection-unreachable
- attempt 1 (repair 1): failed; 4/5 checks; 0/1 cases model=claude-haiku-5-5; execution 20261020.043546.185Z-9a545f3a; reason: programmatic acceptance failed: db-selection-unreachable
- attempt 2 (repair 2): failed; 4/5 checks; 0/1 cases model=claude-haiku-5-5; execution 20261020.043648.991Z-80fda342; stopped: deterministic acceptance score did not improve on 2 consecutive calls; reason: programmatic acceptance failed: db-selection-unreachable

## Agent self-report (advisory)
The build agent declared a failure. This is advisory only; the programmatic acceptance above is the authority for this block's outcome.
- summary: Shipped persistence library escapes refused PostgreSQL connects as psycopg.OperationalError, so db-selection-unreachable cannot pass in this Target.
- detail:
    The declared check runs `open_database(dsn).accounts.list()` against `postgresql://127.0.0.1:1/ledger` and expects `PersistenceError`. `Database.run()` in the shipped `persistence/db.py` calls `driver.connect()` before its `try`, so the driver's error is raised unwrapped. Making it pass here would require editing a shipped, do-not-edit file, which a rebuild would overwrite. Fix the connect call in Drydock's Rigging source persistence layer and rebuild before rerunning. Do not rerun this block until that fix is in.

## Failure
- summary: programmatic acceptance failed: db-selection-unreachable
- detail:
    Block "Block 3 · Service" [block-3] failed its acceptance criteria.
      Story "Select the database from DATABASE_URL, DATABASE_PATH, or data/app.db." [foundation-002] does not meet its own acceptance criteria:
        - AC db-selection-unreachable — An unreachable PostgreSQL server raises PersistenceError instead of returning a database.
            assertion: psycopg.OperationalError: connection failed: connection to server at "127.0.0.1", port 1 failed: Connection refused
            cases: pass=0 fail=1 total=1 from=e.ConnStatus._member_map_
            raised at: connection.py:126
            process exit code: 1
            error: psycopg.OperationalError: connection failed: connection to server at "127.0.0.1", port 1 failed: Connection refused
            values at failure:
              last_ex = OperationalError('connection failed: connection to server at "127.0.0.1", port 1 failed: Connection refused\n\tIs the server running on that host and accepting TCP/IP connections?')
            check stderr:
              Traceback (most recent call last):
                File "db-selection-unreachable.py", line 6, in <module>
                  db.accounts.list()
                File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/persistence/db.py", line 186, in <lambda>
                  return lambda **arguments: self._database.run(operation, arguments)
                                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/persistence/db.py", line 244, in run
                  connection = self._driver.connect()
                               ^^^^^^^^^^^^^^^^^^^^^^
                File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/persistence/postgres.py", line 47, in connect
                  connection = _driver_module().connect(self._dsn)
                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.040609/build/LayersTesting/.venv/lib/python3.11/site-packages/psycopg/connection.py", line 126, in connect
                  raise last_ex.with_traceback(None)
              psycopg.OperationalError: connection failed: connection to server at "127.0.0.1", port 1 failed: Connection refused
              	Is the server running on that host and accepting TCP/IP connections?

## Build summary
This repair feedback matches the previous pass exactly, and the build directory has not changed since then. I re-checked it last pass and the result holds: `config.py` and `tests/test_database_selection.py` are correct, the suite is 44 passed and 1 xfailed, and `db-selection-unreachable` still fails. The defect is in the shipped `persistence/db.py`, which says it must not be edited here, so I am not making a local patch that a rebuild would overwrite.

I am not emitting `AC_BROKEN`. The criterion matches the spec, so the fault is the shipped library, not the criterion. The fix belongs in Drydock's `Rigging/languages/python/persistence/db.py`: move `self._driver.connect()` inside the `try` in `Database.run()` and in `execute_script()`, and make sure the `except` branch's `connection.rollback()` cannot run on an unbound name. After the rebuild, remove the xfail marker in `tests/test_database_selection.py`.

If you want a local stopgap so the check can run in this build now, say so and I will patch `persistence/db.py` in the build directory. I would label it clearly as temporary, since the next rebuild will overwrite it.

RESULT: FAILED

FILES CHANGED:
- (none in this pass)

SUMMARY:
No changes this pass. Suite via `sh bin/test.sh`: 44 passed, 1 xfailed, exit 0. Declared assertions for URL precedence, path fallback, Postgres DSN passthrough, and default resolution pass. `db-selection-unreachable` fails because the shipped persistence library raises a raw `psycopg.OperationalError` instead of `PersistenceError`.

BLOCKERS:
- Shipped `persistence/db.py` (`Database.run()` near line 218, `execute_script()` near line 244) calls `driver.connect()` outside its `try`. Fix in Drydock's Rigging persistence source, rebuild, then remove the xfail marker.
- Open blueprint-decision from the first pass: is strict xfail acceptable for this check until the library is fixed?

FAILURE_SUMMARY: Shipped persistence library escapes refused PostgreSQL connects as psycopg.OperationalError, so db-selection-unreachable cannot pass in this Target.
FAILURE_DETAIL: The declared check runs `open_database(dsn).accounts.list()` against `postgresql://127.0.0.1:1/ledger` and expects `PersistenceError`. `Database.run()` in the shipped `persistence/db.py` calls `driver.connect()` before its `try`, so the driver's error is raised unwrapped. Making it pass here would require editing a shipped, do-not-edit file, which a rebuild would overwrite. Fix the connect call in Drydock's Rigging source persistence layer and rebuild before rerunning. Do not rerun this block until that fix is in.
