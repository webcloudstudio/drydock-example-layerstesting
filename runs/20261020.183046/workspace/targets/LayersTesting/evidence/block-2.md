# Evidence: Block 2 · Foundational (block-2)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 10420
- execution id: 20261020.184104.258Z-8e9a3538

## Stories built
- Establish the relational persistence contract for the cash ledger. (database) [story]
- Provide the executable ledger command and command validation. (cli-foundation) [story]

## Reusable compacts
- DATABASE_compact.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: DATABASE.md (SP 2104)
- context: ARCHITECTURE_compact.md (SP 152)
- stack: persistence.md (SP 2407)
- stack: sqlite.md (SP 1818)
- implements: FEATURE-CLI-FOUNDATION.md (SP 716)
- context: DATABASE.md (SP 2104)
- stack: cli.md (SP 1755)

## Build directory changes
- cli/__init__.py
- cli/__main__.py
- cli/commands.py
- cli/parser.py
- cli/testing.py
- ledger_app/services.py
- tests/test_cli_foundation.py
- tests/test_persistence_contract.py
- cli.py

## Pre-build acceptance observation
- RED: cli-help (FEATURE-CLI-FOUNDATION.md)
  intent: The executable command surface provides successful help or usage entry points.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "cli-help.py", line 1, in <module>
        from cli.testing import cli_runner
    ModuleNotFoundError: No module named 'cli.testing'; 'cli' is not a package
- RED: cli-unknown-command (FEATURE-CLI-FOUNDATION.md)
  intent: An unknown root command is rejected with the documented usage exit code.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "cli-unknown-command.py", line 1, in <module>
        from cli.testing import cli_runner
    ModuleNotFoundError: No module named 'cli.testing'; 'cli' is not a package
- RED: cli-unknown-report (FEATURE-CLI-FOUNDATION.md)
  intent: An unknown report name is rejected with the documented usage exit code.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "cli-unknown-report.py", line 1, in <module>
        from cli.testing import cli_runner
    ModuleNotFoundError: No module named 'cli.testing'; 'cli' is not a package
- RED: cli-argument-validation (FEATURE-CLI-FOUNDATION.md)
  intent: Missing required command arguments are rejected without standard output.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "cli-argument-validation.py", line 1, in <module>
        from cli.testing import cli_runner
    ModuleNotFoundError: No module named 'cli.testing'; 'cli' is not a package

## Post-build programmatic acceptance
- PASS: cli-help (FEATURE-CLI-FOUNDATION.md)
  intent: The executable command surface provides successful help or usage entry points.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-unknown-command (FEATURE-CLI-FOUNDATION.md)
  intent: An unknown root command is rejected with the documented usage exit code.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-unknown-report (FEATURE-CLI-FOUNDATION.md)
  intent: An unknown report name is rejected with the documented usage exit code.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-argument-validation (FEATURE-CLI-FOUNDATION.md)
  intent: Missing required command arguments are rejected without standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
<reusable-compact filename="DATABASE.md">
Persistence uses generated `persistence.open_database(dsn)` only; DSN precedence is `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`. SQLite is required locally; PostgreSQL remains supported. Amounts are integer cents.

Tables:
- `accounts(account TEXT PRIMARY KEY NOT NULL, name VARCHAR(40) NOT NULL)`
- `categories(category TEXT PRIMARY KEY NOT NULL, description VARCHAR(40) NOT NULL)`
- `transactions(txn_id INTEGER PRIMARY KEY NOT NULL, date TEXT NOT NULL, account TEXT NOT NULL REFERENCES accounts(account), category TEXT NOT NULL REFERENCES categories(category), amount INTEGER NOT NULL, memo VARCHAR(60) NOT NULL)`

Declared operations:
- accounts: `list()`, `create(account, name)`, `get(account)`, `update(account, name)`, `delete(account)`
- categories: `list()`, `get(category)`
- transactions: `list()`, `create(txn_id, date, account, category, amount, memo)`, `get(txn_id)`, `update(txn_id, amount)`, `delete(txn_id)`

Schema creation is idempotent via generated `schema.sql`; application startup must not create or alter schema. Application code must not import database drivers, use floating point for amounts, or bypass repositories.
</reusable-compact>

RESULT: SUCCESS

FILES CHANGED:
- cli.py
- cli/__init__.py
- cli/__main__.py
- cli/commands.py
- cli/parser.py
- cli/testing.py
- ledger_app/services.py
- tests/test_cli_foundation.py
- tests/test_persistence_contract.py

SUMMARY:
Implemented the importable `ledger` CLI package, command-family parsing, help, usage validation, dispatch boundary, and persistence round-trip tests. Project tests pass: 9 passed.

BLOCKERS:
- Full `sources/run.sh` remains incomplete for later ledger workflow blocks: 4 passed, 39 failed. No current-block acceptance checks failed.
