# Evidence: Block 2 · Foundational (block-2)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 16275
- execution id: 20261020.151321.830Z-2f591404

## Stories built
- Declare the three-table schema in DATABASE.md and generate the persistence package. (PERSIST-002) [story]
- Provide the ledger executable at the application root. (CLI-003) [story]

## Reusable compacts
- DATABASE_compact.md

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1145)
- implements: DATABASE.md (SP 3620)
- stack: persistence.md (SP 3689)
- stack: sqlite.md (SP 2787)
- implements: FEATURE-CliEntry.md (SP 803)
- context: ARCHITECTURE_compact.md (SP 427)
- context: DATABASE.md (SP 3620)
- stack: cli.md (SP 2689)

## Build directory changes
- cli/__init__.py
- cli/__main__.py
- cli/commands.py
- cli/parser.py
- cli/testing.py
- ledger
- pyproject.toml
- tests/test_cli.py

## Pre-build acceptance observation
- RED: cli-entry-executable (FEATURE-CliEntry.md)
  intent: The ledger executable is a file at the application root with its execute bit set.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      ledger_path = PosixPath('ledger')
    --- drydock: end values ---
    Traceback (most recent call last):
      File "cli-entry-executable.py", line 5, in <module>
        assert ledger_path.is_file()
               ^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: cli-entry-main-contract (FEATURE-CliEntry.md)
  intent: cli_runner returns an integer status and two strings, and the ledger executable exits with the same status for the same argv.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.

## Post-build programmatic acceptance
- PASS: cli-entry-executable (FEATURE-CliEntry.md)
  intent: The ledger executable is a file at the application root with its execute bit set.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-entry-main-contract (FEATURE-CliEntry.md)
  intent: cli_runner returns an integer status and two strings, and the ledger executable exits with the same status for the same argv.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    usage: ledger [-h] <command> ...
    ledger: error: argument <command>: invalid choice: 'no-such-command' (choose from )

## Build summary
I'll start by inspecting the build directory and the untracked `persistence/` and `schema.sql` already present.The `persistence/` package and `schema.sql` are already generated, and the `cli/` package and `ledger` launcher are missing. Next I'll check the project scaffolding, launchers, tests, and the blueprint architecture.The `.venv`, `pyproject.toml`, and `tests/test_foundation.py` are in place. I'll read the existing test for style and check that the venv imports the generated persistence package.The existing suite passes (8 tests), and the venv imports the generated `persistence` package. The step's remaining work is the `cli` package, the `ledger` launcher, and tests for both. I'm following the `FEATURE-CliEntry` launcher contract and `cli.md` structure. The generated persistence files are left untouched, since they are shipped or generated.Next I'll set the execute bit on the launcher, write the CLI tests, and run the two declared acceptance checks.The launcher, `cli_runner`, and `python -m cli` all return the same status (2) for an unknown command. Now the test file, which covers the declared contract and the launcher.The suite fails at collection because pytest does not put the project root on `sys.path`, so `import cli` fails. I'll add `pythonpath = ["."]` to the existing pytest config in `pyproject.toml`. That is the standard fix, and it does not affect the lock file.All 17 tests pass. The DATABASE step has no programmatic acceptance criteria of its own, so I'll do one read-back check that the generated schema applies and round-trips through the declared operations, using a temporary store.The `update` call returned an `int` rather than a `TransactionRow`, even though `DATABASE.md` declares `TransactionRow` as its output. I'll check what the generated declaration says and what `update` actually returns before deciding whether it matters.The `ledger` launcher and `cli` package are built, and both declared acceptance checks pass. The generated persistence layer round-trips correctly. One thing I noticed in that layer is reported under SUMMARY.

<reusable-compact filename="DATABASE.md">
Database: `persistence.open_database(dsn) -> Database`; `persistence.testing.db_session()` yields a fresh store with `schema.sql` applied. Engines: SQLite (stdlib) and PostgreSQL (`postgres://` / `postgresql://` DSN).
Tables (all amounts INTEGER cents):
- `accounts(account VARCHAR(12) PK, name VARCHAR(40))`
- `categories(category VARCHAR(12) PK, description VARCHAR(40))`
- `transactions(txn_id INTEGER PK, date VARCHAR(10), account VARCHAR(12) -> accounts, category VARCHAR(12) -> categories, amount INTEGER, memo VARCHAR(60) DEFAULT '')`
Operations: `accounts.{list,get,create,update,delete}`, `categories.{list,get,create}`, `transactions.{list,get,create,update,delete}`. Keyword args are the declared input fields (for example `transactions.update(txn_id=, amount=)`). Rows are frozen dataclasses `AccountRow`, `CategoryRow`, `TransactionRow`.
Foreign keys are enforced. Deleting an account with transactions is refused by the command layer, not by the store.
</reusable-compact>

RESULT: SUCCESS

FILES CHANGED:
- cli/__init__.py
- cli/__main__.py
- cli/parser.py
- cli/commands.py
- cli/testing.py
- ledger
- tests/test_cli.py
- pyproject.toml

SUMMARY:
- **CLI-003:** `ledger` is a POSIX launcher at the application root with the exec bit set. It follows the `FEATURE-CliEntry` launcher contract exactly. `cli.main(argv) -> int` and `cli.testing.cli_runner(*args)` are implemented. `python -m cli` also works.
- **Acceptance checks:** I ran both declared checks by hand and they pass.
  - `cli-entry-executable`: `ledger` is a file and is executable.
  - `cli-entry-main-contract`: `cli_runner` returns `(int, str, str)`, and the launcher's exit status matches it (both 2 for `no-such-command`).
- **Tests:** `sh bin/test.sh` gives 17 passed (8 existing foundation tests, 9 new in `tests/test_cli.py`). The new tests cover unknown and empty argv, `--help` (exit 0), the `cli_runner` return shape, and launcher/in-process status agreement.
- **PERSIST-002:** The `persistence/` package and `schema.sql` were already on disk before this step, and I did not modify them. I checked them with a temporary store: create, get, update, and list all round-trip, and a transaction naming a missing account is refused.
- **Choices I made:**
  - `main` catches the `SystemExit` that argparse raises for usage errors and `--help`, and returns its code. Without this, `cli_runner` would raise instead of returning a status.
  - No commands are registered yet, so every command currently exits 2 with a message on stderr. Real commands arrive in later blocks.
  - I added `pythonpath = ["."]` to `[tool.pytest.ini_options]` in `pyproject.toml`. Without it, pytest cannot import `cli`. This does not change `uv.lock`.
- **Observation for Drydock (not a blocker here):** `DATABASE.md` declares `TransactionRow` as the output of `transactions.update` and `AccountRow` for `accounts.update`. The generated `persistence/schema.py` sets `row=None` for both, and `update` returns a row count (`1`) rather than a row. The write does take effect. Any caller that expects a row back from `update` will need this fixed in the generator or the declaration, not in `persistence/`, which I left alone.
- Not verified: the POSIX `sh` launcher run by `bin/test.sh`, and `ledger` via WSL's `/mnt/c` mount beyond the calls above. Both passed here.
