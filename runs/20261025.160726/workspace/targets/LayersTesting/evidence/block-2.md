# Evidence: Block 2 · Foundational (block-2)

- block type: block
- date: 2026-10-25
- resulting state: closed/verified
- story points (combined assembled cost): 27694
- execution id: 20261025.162944.754Z-f06f99f9

## Stories built
- Declare accounts, categories, and transactions and every repository operation the ledger needs. (database) [story]
- Build the cli package entry point: dispatch, exit-code mapping, and diagnostic channel. (cli-entry) [story]

## Reusable compacts
- DATABASE_compact.md
- ARCHITECTURE_compact.md

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1156)
- implements: DATABASE.md (SP 8020)
- stack: persistence.md (SP 6132)
- stack: sqlite.md (SP 3364)
- implements: FEATURE-CliEntry.md (SP 2700)
- context: ARCHITECTURE.md (SP 2498)
- context: DATABASE.md (SP 8020)
- stack: cli.md (SP 2689)

## Build directory changes
- cli/__init__.py
- cli/commands/__init__.py
- cli/config.py
- cli/context.py
- cli/errors.py
- cli/registry.py
- cli/testing.py
- data/logs/test_2026-10-25_123052.log
- data/logs/test_2026-10-25_123110.log
- pyproject.toml
- tests/test_cli_entry.py

## Pre-build acceptance observation
- RED: accounts-create (DATABASE.md)
  intent: accounts.create stores an account that accounts.get reads back with the supplied name.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: accounts-get (DATABASE.md)
  intent: accounts.get returns the row for a present account and None for an absent one.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: accounts-list (DATABASE.md)
  intent: accounts.list returns created accounts in ascending code order.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: accounts-update (DATABASE.md)
  intent: accounts.update changes only the name and returns None for an absent account.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: accounts-delete (DATABASE.md)
  intent: accounts.delete removes the account so a later get finds nothing.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: accounts-clear (DATABASE.md)
  intent: accounts.clear removes every account once dependent transactions are cleared.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: categories-create (DATABASE.md)
  intent: categories.create stores a category that categories.get reads back with the supplied description.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: categories-get (DATABASE.md)
  intent: categories.get returns a present category and None for an absent one.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: categories-list (DATABASE.md)
  intent: categories.list returns created categories in ascending code order.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: categories-clear (DATABASE.md)
  intent: categories.clear removes every category once dependent transactions are cleared.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: transactions-create (DATABASE.md)
  intent: transactions.create stores a row that transactions.get reads back with every supplied value.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: transactions-get (DATABASE.md)
  intent: transactions.get returns a present row and None for an absent id.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: transactions-list (DATABASE.md)
  intent: transactions.list returns rows in ascending txn_id order and filters by account.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: transactions-update (DATABASE.md)
  intent: transactions.update changes only the amount and returns None for an absent id.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: transactions-delete (DATABASE.md)
  intent: transactions.delete removes the row so a later get finds nothing.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: transactions-clear (DATABASE.md)
  intent: transactions.clear removes every transaction row.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: cli-unknown-command (FEATURE-CliEntry.md)
  intent: An unknown command exits 2 with nothing on standard output and one diagnostic line.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: cli-no-arguments (FEATURE-CliEntry.md)
  intent: Running with no arguments is a usage error.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: cli-success-csv (FEATURE-CliEntry.md)
  intent: A registered handler's rows are written as unquoted CSV with LF endings and exit 0.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: cli-no-output-handler (FEATURE-CliEntry.md)
  intent: A handler returning None exits 0 and writes nothing to standard output.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: cli-error-codes (FEATURE-CliEntry.md)
  intent: Each LedgerError subclass maps to its exit code and an unexpected exception maps to 1, with empty standard output.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: cli-argument-count (FEATURE-CliEntry.md)
  intent: Too few or too many arguments is exit 2 and the handler runs only for a count within range.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: cli-multiword-command (FEATURE-CliEntry.md)
  intent: A two-word command dispatches on both words; the first word alone or an unknown second word is exit 2.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: cli-resolve-dsn (FEATURE-CliEntry.md)
  intent: The database location resolves from DATABASE_URL, then DATABASE_PATH, then data/app.db.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.

## Post-build programmatic acceptance
- PASS: accounts-create (DATABASE.md)
  intent: accounts.create stores an account that accounts.get reads back with the supplied name.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: accounts-get (DATABASE.md)
  intent: accounts.get returns the row for a present account and None for an absent one.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: accounts-list (DATABASE.md)
  intent: accounts.list returns created accounts in ascending code order.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: accounts-update (DATABASE.md)
  intent: accounts.update changes only the name and returns None for an absent account.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: accounts-delete (DATABASE.md)
  intent: accounts.delete removes the account so a later get finds nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: accounts-clear (DATABASE.md)
  intent: accounts.clear removes every account once dependent transactions are cleared.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: categories-create (DATABASE.md)
  intent: categories.create stores a category that categories.get reads back with the supplied description.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: categories-get (DATABASE.md)
  intent: categories.get returns a present category and None for an absent one.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: categories-list (DATABASE.md)
  intent: categories.list returns created categories in ascending code order.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: categories-clear (DATABASE.md)
  intent: categories.clear removes every category once dependent transactions are cleared.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transactions-create (DATABASE.md)
  intent: transactions.create stores a row that transactions.get reads back with every supplied value.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transactions-get (DATABASE.md)
  intent: transactions.get returns a present row and None for an absent id.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transactions-list (DATABASE.md)
  intent: transactions.list returns rows in ascending txn_id order and filters by account.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transactions-update (DATABASE.md)
  intent: transactions.update changes only the amount and returns None for an absent id.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transactions-delete (DATABASE.md)
  intent: transactions.delete removes the row so a later get finds nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transactions-clear (DATABASE.md)
  intent: transactions.clear removes every transaction row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-unknown-command (FEATURE-CliEntry.md)
  intent: An unknown command exits 2 with nothing on standard output and one diagnostic line.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: unknown command: zz-no-such-command
- PASS: cli-no-arguments (FEATURE-CliEntry.md)
  intent: Running with no arguments is a usage error.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-success-csv (FEATURE-CliEntry.md)
  intent: A registered handler's rows are written as unquoted CSV with LF endings and exit 0.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-no-output-handler (FEATURE-CliEntry.md)
  intent: A handler returning None exits 0 and writes nothing to standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-error-codes (FEATURE-CliEntry.md)
  intent: Each LedgerError subclass maps to its exit code and an unexpected exception maps to 1, with empty standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    zz-rej 3 error: diagnostic
    
    zz-nf 4 error: diagnostic
    
    zz-op 1 error: diagnostic
    
    zz-us 2 error: diagnostic
- PASS: cli-argument-count (FEATURE-CliEntry.md)
  intent: Too few or too many arguments is exit 2 and the handler runs only for a count within range.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-multiword-command (FEATURE-CliEntry.md)
  intent: A two-word command dispatches on both words; the first word alone or an unknown second word is exit 2.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-resolve-dsn (FEATURE-CliEntry.md)
  intent: The database location resolves from DATABASE_URL, then DATABASE_PATH, then data/app.db.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.160726/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
Persistence is already generated and the venv runs on Python 3.12. The DATABASE step is satisfied by the existing declaration and generated package, so this block's work is the `cli` package. Writing it now.Moving the row write inside the `try` so an unexpected write failure maps to exit 1 instead of a traceback, then adding tests.Now running the project suite and the FEATURE-CliEntry acceptance assertions.Two problems: `-I` in my AC runner ignores `PYTHONPATH`, which is my harness's fault. The pytest import failure is real: `tests/` has no path to the project root. I'll add `pythonpath = ["."]` to the existing pytest config, which is additive and leaves the foundation tests' checks intact.All 42 tests pass and the eight FEATURE-CliEntry checks I can run here pass. Last, a check of the real launcher and the architecture import-boundary check.<reusable-compact filename="DATABASE.md">
Tables: accounts(account VARCHAR(12) PK, name VARCHAR(40) NOT NULL); categories(category VARCHAR(12) PK, description VARCHAR(40) NOT NULL); transactions(txn_id INTEGER PK, date VARCHAR(10) NOT NULL, account FK accounts, category FK categories, amount INTEGER NOT NULL signed cents, memo VARCHAR(60) NOT NULL DEFAULT '').
Operations (db.<table>.<name>): accounts.get/list(order account asc)/create/update(match account)/delete(match account)/clear(first_code, delete where account >= first_code); categories.get/list(order category asc)/create/clear(first_code); transactions.get/list(order txn_id asc; optional account, category)/create/update(txn_id; sets amount)/delete(txn_id)/clear(min_id, delete where txn_id >= min_id).
Output rows are frozen dataclasses named <Table><Op>Output. No aggregate operation exists; counts, balances and totals come from list results.
Config: DATABASE_URL (PostgreSQL DSN or sqlite path/sqlite://), else DATABASE_PATH, else data/app.db.
Schema is applied once at the DATABASE step, never at startup.
</reusable-compact>

<reusable-compact filename="ARCHITECTURE.md">
Executable `ledger` at application root calls cli.main(argv) and exits with its return value.
cli: main(argv) -> int; registry.register(words, handler, nargs); errors LedgerError(code) with OperationalError=1, UsageError=2, Rejected=3, NotFound=4; config.resolve_dsn(environ); context.open_store(); testing.cli_runner(*args) -> (code, stdout, stderr).
Exit codes: 0 success, 1 operational or unexpected, 2 usage, 3 rejected, 4 not found.
Output: successful commands write unquoted CSV, LF endings, two-decimal amounts; failures write nothing to stdout and one stderr line.
Persistence only through persistence.open_database; no driver import outside persistence/.
Money is integer cents at every layer.
</reusable-compact>

RESULT: SUCCESS

FILES CHANGED:
- cli/__init__.py
- cli/errors.py
- cli/registry.py
- cli/config.py
- cli/context.py
- cli/testing.py
- cli/commands/__init__.py
- tests/test_cli_entry.py
- pyproject.toml

SUMMARY:
Block 2 covers two stories. Both are done, with one caveat on the database story.

- **database:** The declaration is `blueprint/DATABASE.md`, which is protected and already contains the three tables and every operation. I wrote no persistence code. The generated `persistence/` package and `schema.sql` are already in the build and match the declaration (the `clear` operations are present). Nothing needed writing here.
- **cli-entry:** I built the `cli` package to FEATURE-CliEntry.md:
  - `main(argv) -> int` finds the longest registered word prefix, checks the argument count, runs the handler, then writes its rows as unquoted CSV with LF endings.
  - A `LedgerError` returns its code, and a `PersistenceError` or any other exception returns 1. Each writes one diagnostic line to stderr and nothing to stdout.
  - `main` imports every module in `cli.commands` before dispatching, so later commands register without editing `main`.
  - `resolve_dsn` and `open_store` follow the spec. `open_store` creates the SQLite parent directory and does not apply schema.

Choices I made, for you to redirect:
- `register` raises `ValueError` on a duplicate command name, an empty word tuple, or an inverted argument range.
- I did not create `cli/core.py`. ARCHITECTURE lists it for shared amount, text, date and balance rules, but FEATURE-CliEntry does not provide it, so it belongs to a later story.
- I added `pythonpath = ["."]` to the existing `[tool.pytest.ini_options]` in `pyproject.toml`. Without it, pytest could not import `cli`. This is the only change to a foundation file, and the foundation tests still pass.

Checks run:
- `sh bin/test.sh`: 42 passed, exit 0. That is the 10 foundation tests plus 32 new tests in `tests/test_cli_entry.py`.
- I ran the eight FEATURE-CliEntry acceptance bodies (`cli-unknown-command`, `cli-no-arguments`, `cli-success-csv`, `cli-no-output-handler`, `cli-error-codes`, `cli-argument-count`, `cli-multiword-command`, `cli-resolve-dsn`). All passed.
- The `ledger` launcher returns 2 for no arguments and for an unknown command, and writes one diagnostic line each time.
- A grep found no `sqlite3` or `psycopg` import under `cli/`.

Not run: `sources/run.sh`. It needs `init`, `load`, `count` and the rest of the commands, which later blocks add, so it is not expected to pass yet. The `arch-*` acceptance checks in ARCHITECTURE.md were not run through the harness; I checked the driver-import rule by grep only.

<blueprint-decisions>
[{"spec":"FEATURE-CliEntry.md","severity":"Low","subject":"Duplicate command registration and pytest import path","decision":"register() raises ValueError on a duplicate word tuple rather than silently replacing the handler, so two command modules cannot shadow each other. I also added pythonpath = [\".\"] to pyproject.toml's pytest options so tests can import cli. Is that acceptable, or should the import path come from a conftest.py instead?"}]
</blueprint-decisions>
