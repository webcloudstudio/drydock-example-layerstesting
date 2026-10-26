# Evidence: Block 2 · Foundational (block-2)

- block type: block
- date: 2026-10-25
- resulting state: closed/verified
- story points (combined assembled cost): 27512
- execution id: 20261025.181628.984Z-1b304a4d

## Stories built
- Declare the accounts, categories, and transactions store and its repository operations. (database) [story]
- Provide the ledger executable, command dispatch, exit codes, CSV output, and input validators. (cli-foundation) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1156)
- implements: DATABASE.md (SP 7219)
- context: ARCHITECTURE_compact.md (SP 475)
- stack: common_compact.md (SP 1653)
- stack: persistence.md (SP 6132)
- stack: sqlite.md (SP 3364)
- implements: FEATURE-CliFoundation.md (SP 3554)
- context: DATABASE.md (SP 7219)
- stack: cli.md (SP 2689)

## Build directory changes
- cli/__init__.py
- cli/__main__.py
- cli/commands/__init__.py
- cli/database.py
- cli/errors.py
- cli/money.py
- cli/output.py
- cli/registry.py
- cli/testing.py
- cli/validate.py
- data/logs/test_2026-10-25_141824.log
- data/logs/test_2026-10-25_141839.log
- ledger
- pyproject.toml
- tests/test_cli_foundation.py

## Pre-build acceptance observation
- RED: accounts-create (DATABASE.md)
  intent: accounts.create stores an account that accounts.get reads back with the supplied values.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: accounts-get (DATABASE.md)
  intent: accounts.get returns the stored row for a present code and None for an absent code.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: accounts-list (DATABASE.md)
  intent: accounts.list returns created accounts in ascending code order and honors the account filter.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: accounts-update (DATABASE.md)
  intent: accounts.update changes the name, returns the updated row, and persists it for a later read.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: accounts-delete (DATABASE.md)
  intent: accounts.delete removes the account so a later get finds nothing.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: categories-create (DATABASE.md)
  intent: categories.create stores a category that categories.get reads back with the supplied values.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: categories-get (DATABASE.md)
  intent: categories.get returns the stored row for a present code and None for an absent code.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: categories-list (DATABASE.md)
  intent: categories.list returns created categories in ascending code order and honors the category filter.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: categories-delete (DATABASE.md)
  intent: categories.delete removes the category so a later get finds nothing.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: transactions-create (DATABASE.md)
  intent: transactions.create stores a row with integer-cent amount that transactions.get reads back unchanged.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: transactions-get (DATABASE.md)
  intent: transactions.get returns the stored row for a present id and None for an absent id.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: transactions-list (DATABASE.md)
  intent: transactions.list filtered by account returns that account's rows in ascending txn_id order.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: transactions-update (DATABASE.md)
  intent: transactions.update changes only the amount and persists it for a later read.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: transactions-delete (DATABASE.md)
  intent: transactions.delete removes the row so a later get finds nothing.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: clifoundation-executable (FEATURE-CliFoundation.md)
  intent: The ledger executable exists at the application root and is executable.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "clifoundation-executable.py", line 3, in <module>
        assert os.path.isfile("ledger")
    AssertionError
- RED: clifoundation-usage-process (FEATURE-CliFoundation.md)
  intent: Running the executable with an unknown command exits 2 and writes nothing to standard output.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      errno_num = 2
      err_msg = 'No such file or directory'
      err_filename = './ledger'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "clifoundation-usage-process.py", line 4, in <module>
        result = subprocess.run(
                 ^^^^^^^^^^^^^^^
      File "/usr/lib/python3.11/subprocess.py", line 546, in run
        with Popen(*popenargs, **kwargs) as process:
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/lib/python3.11/subprocess.py", line 1022, in __init__
        self._execute_child(args, executable, preexec_fn, close_fds,
      File "/usr/lib/python3.11/subprocess.py", line 1899, in _execute_child
        raise child_exception_type(errno_num, err_msg, err_filename)
    FileNotFoundError: [Errno 2] No such file or directory: './ledger'
- RED: clifoundation-usage-unknown-report (FEATURE-CliFoundation.md)
  intent: An unknown report exits 2 with no standard output.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: clifoundation-usage-unknown-table (FEATURE-CliFoundation.md)
  intent: Loading an unknown table exits 2 with no standard output.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: clifoundation-usage-argcount (FEATURE-CliFoundation.md)
  intent: A wrong argument count exits 2 with no standard output.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: clifoundation-usage-no-command (FEATURE-CliFoundation.md)
  intent: Running with no command at all is a usage error.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: clifoundation-error-exit-codes (FEATURE-CliFoundation.md)
  intent: The error classes carry the exit codes 1, 2, 3, and 4.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: clifoundation-amount-roundtrip (FEATURE-CliFoundation.md)
  intent: Amounts parse to integer cents and format back to the same two-decimal text.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: clifoundation-amount-short-forms (FEATURE-CliFoundation.md)
  intent: Amounts with fewer than two decimals parse to the same cents as their padded form.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: clifoundation-amount-rejections (FEATURE-CliFoundation.md)
  intent: Zero, three decimals, and non-numeric amounts are rejected with exit code 3.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: clifoundation-date-validation (FEATURE-CliFoundation.md)
  intent: A real calendar date is accepted unchanged and an impossible date is rejected.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: clifoundation-code-validation (FEATURE-CliFoundation.md)
  intent: Codes of 1 to 12 characters from A-Z and 0-9 are accepted; others are rejected.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: clifoundation-text-validation (FEATURE-CliFoundation.md)
  intent: Names are 1 to 40 characters and memos 0 to 60 characters, with no comma or newline.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: clifoundation-transaction-format (FEATURE-CliFoundation.md)
  intent: A transaction row formats to the declared six CSV fields with a two-decimal amount.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.

## Post-build programmatic acceptance
- PASS: accounts-create (DATABASE.md)
  intent: accounts.create stores an account that accounts.get reads back with the supplied values.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: accounts-get (DATABASE.md)
  intent: accounts.get returns the stored row for a present code and None for an absent code.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: accounts-list (DATABASE.md)
  intent: accounts.list returns created accounts in ascending code order and honors the account filter.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: accounts-update (DATABASE.md)
  intent: accounts.update changes the name, returns the updated row, and persists it for a later read.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: accounts-delete (DATABASE.md)
  intent: accounts.delete removes the account so a later get finds nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: categories-create (DATABASE.md)
  intent: categories.create stores a category that categories.get reads back with the supplied values.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: categories-get (DATABASE.md)
  intent: categories.get returns the stored row for a present code and None for an absent code.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: categories-list (DATABASE.md)
  intent: categories.list returns created categories in ascending code order and honors the category filter.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: categories-delete (DATABASE.md)
  intent: categories.delete removes the category so a later get finds nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transactions-create (DATABASE.md)
  intent: transactions.create stores a row with integer-cent amount that transactions.get reads back unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transactions-get (DATABASE.md)
  intent: transactions.get returns the stored row for a present id and None for an absent id.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transactions-list (DATABASE.md)
  intent: transactions.list filtered by account returns that account's rows in ascending txn_id order.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transactions-update (DATABASE.md)
  intent: transactions.update changes only the amount and persists it for a later read.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transactions-delete (DATABASE.md)
  intent: transactions.delete removes the row so a later get finds nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: clifoundation-executable (FEATURE-CliFoundation.md)
  intent: The ledger executable exists at the application root and is executable.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: clifoundation-usage-process (FEATURE-CliFoundation.md)
  intent: Running the executable with an unknown command exits 2 and writes nothing to standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: unknown command: frobnicate
- PASS: clifoundation-usage-unknown-report (FEATURE-CliFoundation.md)
  intent: An unknown report exits 2 with no standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: unknown command: report nosuchreport
- PASS: clifoundation-usage-unknown-table (FEATURE-CliFoundation.md)
  intent: Loading an unknown table exits 2 with no standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: unknown command: load nosuchtable missing.csv
- PASS: clifoundation-usage-argcount (FEATURE-CliFoundation.md)
  intent: A wrong argument count exits 2 with no standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: unknown command: account get
    
    error: unknown command: count extra
- PASS: clifoundation-usage-no-command (FEATURE-CliFoundation.md)
  intent: Running with no command at all is a usage error.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: unknown command: (none)
- PASS: clifoundation-error-exit-codes (FEATURE-CliFoundation.md)
  intent: The error classes carry the exit codes 1, 2, 3, and 4.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: clifoundation-amount-roundtrip (FEATURE-CliFoundation.md)
  intent: Amounts parse to integer cents and format back to the same two-decimal text.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: clifoundation-amount-short-forms (FEATURE-CliFoundation.md)
  intent: Amounts with fewer than two decimals parse to the same cents as their padded form.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: clifoundation-amount-rejections (FEATURE-CliFoundation.md)
  intent: Zero, three decimals, and non-numeric amounts are rejected with exit code 3.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: clifoundation-date-validation (FEATURE-CliFoundation.md)
  intent: A real calendar date is accepted unchanged and an impossible date is rejected.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: clifoundation-code-validation (FEATURE-CliFoundation.md)
  intent: Codes of 1 to 12 characters from A-Z and 0-9 are accepted; others are rejected.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: clifoundation-text-validation (FEATURE-CliFoundation.md)
  intent: Names are 1 to 40 characters and memos 0 to 60 characters, with no comma or newline.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: clifoundation-transaction-format (FEATURE-CliFoundation.md)
  intent: A transaction row formats to the declared six CSV fields with a two-decimal amount.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261025.175746/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
The database half of this block is already in place: `persistence/`, `schema.sql`, and the blueprint's `DATABASE.md` (protected, under the Target) all exist, so this step is the CLI foundation. Writing the modules now.Launcher and dispatch behave as specified. Now the test file: the declared acceptance assertions as pytest tests, plus finer tests for the validators, dispatch, and output.Two of my assertions compare stderr wording, which the test rules forbid. Fixing those before running.The test runner doesn't put the project root on `sys.path`, so `cli` and `persistence` don't import under `pytest -q`. I'll add `pythonpath` to the existing pytest config in `pyproject.toml`, which is in the build directory.All 73 tests pass. Checking the final file list against the git status.RESULT: SUCCESS

FILES CHANGED:
- ledger
- cli/__init__.py
- cli/__main__.py
- cli/database.py
- cli/errors.py
- cli/money.py
- cli/output.py
- cli/registry.py
- cli/testing.py
- cli/validate.py
- cli/commands/__init__.py
- tests/test_cli_foundation.py
- pyproject.toml

SUMMARY:
The cli-foundation story is built. The database story needed no writes in this step: `persistence/`, `schema.sql`, and `schema-verification.json` were already generated, and `DATABASE.md` lives in the protected Target blueprint, so I did not author it.

- **`ledger`**: a POSIX sh launcher. It uses `.venv/bin/python` when present, otherwise `python3`, and runs `python -m cli` with the build root on `PYTHONPATH`. It contains no logic and is executable.
- **Dispatch (`cli/__init__.py`, `cli/registry.py`)**: `main(argv) -> int` resolves the longest registered command path and checks argument count before opening the database. A `LedgerError` maps to its exit code. A `PersistenceError` maps to 1. Diagnostics go to stderr as one line. The handler runs to completion before any CSV is written.
- **Errors (`cli/errors.py`)**: `Operational` (1), `Usage` (2), `Rejected` (3), `NotFound` (4).
- **Output (`cli/output.py`)**: `write_rows` writes comma-separated lines with `\n` endings and no quoting. `TRANSACTION_HEADER` and `format_transaction` produce the six declared fields.
- **Money (`cli/money.py`)**: integer-cent parsing and two-decimal formatting. Zero, extra decimals, signs other than a leading `-`, and comma forms are rejected.
- **Validators (`cli/validate.py`)**: codes, names, memos, and dates, each returning its value or raising `Rejected`.
- **Store location (`cli/database.py`)**: `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`, opened via `persistence.open_database`.
- **In-process runner (`cli/testing.py`)**: `cli_runner(*args)` returns `(code, stdout, stderr)`.
- **Command loader (`cli/commands/__init__.py`)**: imports every module in the package at startup so command modules self-register.

Choices I made, for you to redirect:
1. No commands are registered yet. Every command currently exits 2 as an unknown command. The command stories will register their handlers.
2. Names and memos also reject `\r`, not only `\n`, because a carriage return would also break a CSV line.
3. I added `pythonpath = ["."]` to the existing `[tool.pytest.ini_options]` in `pyproject.toml`. Without it, `pytest -q` could not import `cli` or `persistence`.

Checks: `sh bin/test.sh` reports 73 passed, 0 failed. The file covers each declared FEATURE-CliFoundation assertion, plus boundary, dispatch, output and store-location tests. Tests assert on return values, exit codes, stdout and the stored state, not on stderr wording. I did not run `sources/run.sh`, because it is the terminal story and this block does not declare it.

BLOCKERS: none.

<blueprint-decisions>
[{"spec":"FEATURE-CliFoundation.md","severity":"Low","subject":"Forbidden characters in names and memos","decision":"Names and memos reject a carriage return as well as a comma or newline, since a carriage return also breaks a CSV line. Is that acceptable, or should only \\n be rejected?"},{"spec":"FEATURE-CliFoundation.md","severity":"Low","subject":"Command registration before command stories","decision":"No commands are registered in this block, so every command exits 2 as unknown until the command stories register their handlers. Those stories will add their handlers under cli/commands/."}]
</blueprint-decisions>
