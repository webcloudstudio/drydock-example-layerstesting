# Evidence: Block 2 · Foundational (block-2)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 11991
- execution id: 20261020.160509.740Z-50fe13f8

## Stories built
- Implement the relational persistence contract for the ledger. (persistence) [story]
- Provide the executable ledger command and command validation. (cli-foundation) [story]

## Reusable compacts
- DATABASE_compact.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 747)
- implements: DATABASE.md (SP 1700)
- stack: common.md (SP 1812)
- stack: persistence.md (SP 2407)
- stack: sqlite.md (SP 1818)
- implements: FEATURE-CLI-FOUNDATION.md (SP 840)
- context: ARCHITECTURE_compact.md (SP 130)
- context: DATABASE.md (SP 1700)
- stack: cli.md (SP 1755)

## Build directory changes
- cli.py
- persistence/db.py
- persistence/schema.py
- reports.py
- services.py

## Pre-build acceptance observation
- RED: cli-success-dispatch (FEATURE-CLI-FOUNDATION.md)
  intent: The executable dispatches a supported command and returns its successful exit status.
  return code: 1
  stdout:
    usage: ledger [-h] [{help}]
    ledger: error: argument command: invalid choice: 'init' (choose from help)
  stderr:
    --- drydock: values at failure ---
      result = CompletedProcess(args=['./ledger', 'init'], returncode=2, stdout='', stderr="usage: ledger [-h] [{help}]\nledger: error: argument command: invalid choice: 'init' (choose from help)\n")
    --- drydock: end values ---
    Traceback (most recent call last):
      File "cli-success-dispatch.py", line 10, in <module>
        assert result.returncode == 0
               ^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: cli-usage-error (FEATURE-CLI-FOUNDATION.md)
  intent: An unknown command is reported as a usage error without standard output.
  return code: 1
  stdout:
    usage: ledger [-h] [{help}]
    ledger: error: argument command: invalid choice: 'frobnicate' (choose from help)
  stderr:
    --- drydock: values at failure ---
      result = CompletedProcess(args=['./ledger', 'frobnicate'], returncode=2, stdout='', stderr="usage: ledger [-h] [{help}]\nledger: error: argument command: invalid choice: 'frobnicate' (choose from help)\n")
    --- drydock: end values ---
    Traceback (most recent call last):
      File "cli-usage-error.py", line 12, in <module>
        assert len(result.stderr.splitlines()) == 1
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: cli-database-precedence (FEATURE-CLI-FOUNDATION.md)
  intent: DATABASE_URL takes precedence over DATABASE_PATH when selecting the store.
  return code: 1
  stdout:
    usage: ledger [-h] [{help}]
    ledger: error: argument command: invalid choice: 'init' (choose from help)
  stderr:
    --- drydock: values at failure ---
      result = CompletedProcess(args=['./ledger', 'init'], returncode=2, stdout='', stderr="usage: ledger [-h] [{help}]\nledger: error: argument command: invalid choice: 'init' (choose from help)\n")
    --- drydock: end values ---
    Traceback (most recent call last):
      File "cli-database-precedence.py", line 13, in <module>
        assert result.returncode == 0
               ^^^^^^^^^^^^^^^^^^^^^^
    AssertionError

## Post-build programmatic acceptance
- PASS: cli-success-dispatch (FEATURE-CLI-FOUNDATION.md)
  intent: The executable dispatches a supported command and returns its successful exit status.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-usage-error (FEATURE-CLI-FOUNDATION.md)
  intent: An unknown command is reported as a usage error without standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    usage: ledger init|count|load|account|txn|transfer|report
- PASS: cli-database-precedence (FEATURE-CLI-FOUNDATION.md)
  intent: DATABASE_URL takes precedence over DATABASE_PATH when selecting the store.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
<reusable-compact filename="DATABASE.md">
Relational ledger schema: `accounts(account PK, name)`, `categories(category PK, description)`, and `transactions(txn_id PK, date, account FK, category FK, amount INTEGER cents, memo)`. Use only `persistence.open_database(dsn)` and declared table operations. Enforce foreign keys, integer cents, idempotent schema initialization, and atomic commands. DSN precedence: `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`; PostgreSQL URLs select PostgreSQL, otherwise SQLite.
</reusable-compact>

RESULT: SUCCESS

FILES CHANGED:
- cli.py
- services.py
- reports.py
- persistence/db.py
- persistence/schema.py

SUMMARY:
Implemented persistence operations, transactional services, CLI validation, CSV loading, CRUD, transfers, and reports. `pytest -q` passes; staged harness passes 43/43 checks.

BLOCKERS:
- None
