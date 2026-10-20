# Evidence: Block 3 · Service (block-3)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 4751
- execution id: 20261020.151542.070Z-3026385f

## Stories built
- Resolve the database target from DATABASE_URL, DATABASE_PATH, or data/app.db. (PERSIST-001) [story]
- Validate calendar dates in YYYY-MM-DD form. (VALID-003) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1145)
- implements: FEATURE-DatabaseTarget.md (SP 1019)
- context: ARCHITECTURE_compact.md (SP 427)
- context: DATABASE_compact.md (SP 427)
- implements: FEATURE-ValidateDate.md (SP 678)

## Build directory changes
- cli/dates.py
- config.py
- tests/test_config.py
- tests/test_dates.py

## Pre-build acceptance observation
- RED: target-precedence (FEATURE-DatabaseTarget.md)
  intent: DATABASE_URL takes precedence over DATABASE_PATH, which takes precedence over data/app.db, and each value is returned unchanged.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "target-precedence.py", line 2, in <module>
        from config import resolve_database_target
    ModuleNotFoundError: No module named 'config'
- RED: target-opens-store (FEATURE-DatabaseTarget.md)
  intent: The resolved target opens through the shipped persistence library and yields an empty accounts table.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "target-opens-store.py", line 4, in <module>
        from config import resolve_database_target
    ModuleNotFoundError: No module named 'config'
- RED: valid-date-accepts (FEATURE-ValidateDate.md)
  intent: check_date returns each real calendar date in YYYY-MM-DD form unchanged, including a leap day.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "valid-date-accepts.py", line 1, in <module>
        from cli.dates import check_date
    ModuleNotFoundError: No module named 'cli.dates'
- RED: valid-date-rejects (FEATURE-ValidateDate.md)
  intent: check_date raises ValueError for impossible dates and for every malformed shape.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "valid-date-rejects.py", line 1, in <module>
        from cli.dates import check_date
    ModuleNotFoundError: No module named 'cli.dates'

## Post-build programmatic acceptance
- PASS: target-precedence (FEATURE-DatabaseTarget.md)
  intent: DATABASE_URL takes precedence over DATABASE_PATH, which takes precedence over data/app.db, and each value is returned unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: target-opens-store (FEATURE-DatabaseTarget.md)
  intent: The resolved target opens through the shipped persistence library and yields an empty accounts table.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    []
- PASS: valid-date-accepts (FEATURE-ValidateDate.md)
  intent: check_date returns each real calendar date in YYYY-MM-DD form unchanged, including a leap day.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: valid-date-rejects (FEATURE-ValidateDate.md)
  intent: check_date raises ValueError for impossible dates and for every malformed shape.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
The build block needs `config.py` (target resolution) and `cli/dates.py` (date check), plus tests. Nothing in `config.py` or `cli/dates.py` exists yet, and `persistence/` is already shipped, so I'll write the two modules and their tests.Now I'll run the project's declared test command, then the two acceptance snippets verbatim.The pytest suite passed (56 tests). The snippet run failed only because `-I` ignores `PYTHONPATH`; I'll put the project root on `sys.path` explicitly and rerun.RESULT: SUCCESS

FILES CHANGED:
- config.py
- cli/dates.py
- tests/test_config.py
- tests/test_dates.py

SUMMARY:
- **PERSIST-001:** `config.resolve_database_target()` returns `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`. Empty values fall through to the next setting. The value is returned unchanged, and the function opens no connection. The store is opened only through `persistence.open_database` (via `db_session` in the tests).
- **VALID-003:** `cli.dates.check_date(text)` accepts only the exact `YYYY-MM-DD` shape (ASCII digits, no whitespace or sign) and then checks the calendar with `date.fromisoformat`, so leap years are handled. It returns the input unchanged or raises `ValueError`.
- **Tests:** 56 pytest tests pass under `sh bin/test.sh` (exit 0). They cover the precedence rules, empty-value fall-through, the no-connection guarantee, a store round-trip through `accounts.create`/`get`, and calendar and shape boundaries (leap years 1900/2000/2100, year 0000, malformed shapes, Unicode digits). I also ran the three declared acceptance snippets (target-precedence, target-opens-store, valid-date-accepts/rejects) verbatim, and all pass.
- **Not covered by this block:** VALID-003's "rejected with exit 3" is a CLI-level behavior. No command exists yet, so exit-code mapping is untested here and belongs to a later block.
- **Not run:** `sh sources/run.sh`, which is the terminal story and not part of this block. I did not touch `sources/`, `MANIFEST.md`, `COMPASS.md`, `blueprint/`, or `QuarterDeck/`/`evidence/`. No git operations were performed.

Choices made:
- `check_date` uses an explicit regex for shape before the calendar check, so `date.fromisoformat` alone (which accepts forms like `20260101`) cannot let through non-spec input.
- The tests live in new files (`test_config.py`, `test_dates.py`) rather than extending `test_cli.py`, to keep each module's tests separate.

<blueprint-decisions>
[{"spec":"FEATURE-ValidateDate.md","severity":"Low","subject":"Shape check before calendar check","decision":"check_date enforces the exact YYYY-MM-DD shape with an ASCII-digit regex before calling date.fromisoformat, because fromisoformat also accepts compact forms like 20260101. Is that acceptable?"}]
</blueprint-decisions>
