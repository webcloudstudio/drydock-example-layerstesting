# Evidence: Block 2 · Foundational (block-2)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 17118
- execution id: 20261020.135003.768Z-6e2ba9f1

## Stories built
- Generate the persistence package and schema.sql from DATABASE.md through the shipped Rigging library. (database-step) [story]
- Stand up the cli package, its main entry, the cli_runner fixture, and the ledger launcher. (cli-foundation) [story]

## Reusable compacts
- DATABASE_compact.md
- ARCHITECTURE_compact.md

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1145)
- implements: DATABASE.md (SP 3112)
- stack: persistence.md (SP 3689)
- stack: sqlite.md (SP 2778)
- implements: FEATURE-CLI-Platform.md (SP 898)
- context: ARCHITECTURE.md (SP 1663)
- context: DATABASE.md (SP 3112)
- stack: cli.md (SP 2689)

## Build directory changes
- cli/__init__.py
- cli/__main__.py
- cli/commands.py
- cli/parser.py
- cli/testing.py
- conftest.py
- data/logs/lint_2026-10-20_095032.log
- data/logs/lint_2026-10-20_095145.log
- data/logs/lint_2026-10-20_095147.log
- data/logs/lint_2026-10-20_095201.log
- data/logs/lint_2026-10-20_095202.log
- data/logs/test_2026-10-20_095029.log
- data/logs/test_2026-10-20_095142.log
- data/logs/test_2026-10-20_095158.log
- ledger
- pyproject.toml
- tests/test_cli_platform.py
- tests/test_database_step.py
- tests/test_foundation.py

## Pre-build acceptance observation
- RED: cli-main-callable (FEATURE-CLI-Platform.md)
  intent: The cli package exposes main with the single parameter argv.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: cli-runner-shape (FEATURE-CLI-Platform.md)
  intent: cli_runner returns a three-element tuple of an integer exit code and two text streams.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: cli-launcher-executable (FEATURE-CLI-Platform.md)
  intent: The ledger launcher is an executable file at the application root.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      launcher = PosixPath('ledger')
    --- drydock: end values ---
    Traceback (most recent call last):
      File "cli-launcher-executable.py", line 5, in <module>
        assert launcher.is_file()
               ^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: cli-launcher-shebang (FEATURE-CLI-Platform.md)
  intent: The ledger launcher begins with an interpreter line.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      self = PosixPath('ledger')
      mode = 'r'
      buffering = -1
      encoding = 'utf-8'
      errors = None
      newline = None
    --- drydock: end values ---
    Traceback (most recent call last):
      File "cli-launcher-shebang.py", line 3, in <module>
        first_line = Path("ledger").read_text(encoding="utf-8").splitlines()[0]
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/home/barlo/.drydock/claude-home/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/pathlib.py", line 1027, in read_text
        with self.open(mode='r', encoding=encoding, errors=errors) as f:
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/home/barlo/.drydock/claude-home/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/pathlib.py", line 1013, in open
        return io.open(self, mode, buffering, encoding, errors, newline)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    FileNotFoundError: [Errno 2] No such file or directory: 'ledger'

## Post-build programmatic acceptance
- PASS: cli-main-callable (FEATURE-CLI-Platform.md)
  intent: The cli package exposes main with the single parameter argv.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.132808/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-runner-shape (FEATURE-CLI-Platform.md)
  intent: cli_runner returns a three-element tuple of an integer exit code and two text streams.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.132808/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-launcher-executable (FEATURE-CLI-Platform.md)
  intent: The ledger launcher is an executable file at the application root.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.132808/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-launcher-shebang (FEATURE-CLI-Platform.md)
  intent: The ledger launcher begins with an interpreter line.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.132808/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
I'll start by checking what block 1 left in the build directory and whether the shipped persistence library is available.Block 1 left a `persistence/` directory and `schema.sql` untracked. I'll look at those, the shipped library, and the templates before changing anything.The `persistence/` package and `schema.sql` already exist on disk, untracked. I'll check whether they match the shipped library and the DATABASE.md declaration, and read the remaining generated files.The shipped engines match Rigging exactly, and `schema.sql` matches DATABASE.md. The generated package is Drydock's output, and the guardrails say not to hand-edit it, so I'll leave it alone. What's missing is the `cli` package and the `ledger` launcher. First I'll confirm the existing suite runs and that the persistence package imports and round-trips.Two findings before I write anything:

1. **Lint is red, and the cause is in the generated `persistence/schema.py`.** It annotates with `VARCHAR(12)` and `INTEGER`, which are undefined names. `testing.py` and `postgres.py` also trip ruff. Those files are Drydock output and shipped code, and the guardrails forbid editing them. The fix that stays inside my authority is to exclude `persistence/` from ruff in `pyproject.toml`, which is consistent with the stack's rule to exclude generated code from scans. I'll flag it in the summary.
2. The `-I` smoke test failed only because `-I` drops the working directory from `sys.path`. That's a harness artifact, not a defect.

Now I'll write the `cli` package, the root `conftest.py` that provides `cli_runner` (as `stack/cli.md` specifies), and the `ledger` launcher.Next: exclude the generated `persistence/` from ruff, make the launcher executable, and write the tests. The Edit tool needs a Read first, so I'll read `pyproject.toml`.The launcher delegates correctly, returns usage code 2 from any working directory, and `--help` returns 0. Now the ruff exclusion and the tests.Two of those tests are weaker than they should be. The `python -m cli` test uses a bare `python3` with a stripped environment, which is fragile; I'll switch it to `sys.executable`. I'll also tighten one assertion that compared `out` to itself.Now the full project gate: the test suite, then lint.The suite is at 60 passing with one failure, and that failure is the lint gate. Its complaints are my new test code plus one line in block 1's `tests/test_foundation.py`. I'll fix all of them, with the behavior unchanged: an explicit `check=False` on each subprocess call, a literal in place of `dict()`, and combined `with` statements.Both stories are built. `sh bin/test.sh` passes 61 of 61 and `sh bin/lint.sh` is clean. I did not run `sources/run.sh`, since it's the terminal story and not part of this block.

- **database-step:** Drydock had already placed `persistence/` and `schema.sql` in the build. I checked them: the three engine files match the shipped Rigging library byte for byte, and `schema.sql` matches DATABASE.md. I left the generated files untouched and added `tests/test_database_step.py`, which exercises every declared operation, FK refusal, duplicate-key refusal, idempotent DDL, and persistence across reopen.
- **cli-foundation:** `cli/` (`main`, `testing.cli_runner`, `__main__`, parser, and a placeholder dispatch), a root `conftest.py` providing the `cli_runner` fixture, and the `ledger` launcher. `tests/test_cli_platform.py` covers the FEATURE-CLI-Platform acceptance assertions and the launcher's exit codes.

Choices I made that you may want to change:
1. **Ruff excludes `persistence/`** (`pyproject.toml`). The lint gate was already red before I touched anything: Drydock's generated `schema.py` annotates with `VARCHAR(12)` and `INTEGER`, which are undefined names, and the shipped `postgres.py` and `testing.py` trip ruff too. Those files can't be edited here, so I excluded the package from lint. The better long-term fix is for the generator to emit lint-clean output.
2. **One line of block 1's `tests/test_foundation.py` changed**: `check=False` added to the lint subprocess call, to satisfy ruff's PLW1510. Behavior is identical.
3. **`main` returns argparse's exit code** rather than letting `SystemExit` escape, so `main` never exits in-process.
4. **`commands.dispatch` returns 2 for every command.** Routing belongs to cli-dispatch; this block registers no commands.

<reusable-compact filename="DATABASE.md">
Tables (SQLite DDL, schema.sql, CREATE IF NOT EXISTS):
- accounts(account VARCHAR(12) PK NOT NULL, name VARCHAR(40) NOT NULL)
- categories(category VARCHAR(12) PK NOT NULL, description VARCHAR(40) NOT NULL)
- transactions(txn_id INTEGER PK NOT NULL, date VARCHAR(10) NOT NULL, account VARCHAR(12) NOT NULL REFERENCES accounts(account), category VARCHAR(12) NOT NULL REFERENCES categories(category), amount INTEGER NOT NULL [integer cents], memo VARCHAR(60) NOT NULL)
- Indexes: transactions_account_idx, transactions_category_idx

Python surface: persistence.open_database(dsn) -> Database; persistence.testing.db_session(dsn=None) context manager applies schema.sql to a fresh store.
Exports: Database, PersistenceError, UnknownOperation, SCHEMA, open_database.
Operations (db.<table>.<verb>(**kwargs)):
- accounts.create(account, name) -> identity; accounts.get(account) -> AccountRow|None; accounts.list() -> list[AccountRow]; accounts.update(account, name) -> rowcount; accounts.delete(account) -> rowcount
- categories.create(category, description); categories.get(category); categories.list()
- transactions.create(txn_id, date, account, category, amount, memo); transactions.get(txn_id); transactions.list(); transactions.update(txn_id, amount) -> rowcount; transactions.delete(txn_id) -> rowcount
Undeclared verb -> UnknownOperation. Unknown kwarg, FK violation, duplicate key, or driver failure -> PersistenceError.
DSN: bare path or sqlite:// selects SQLite (foreign keys ON); postgres:// selects PostgreSQL (needs psycopg, not in dependencies).
SQLite does not enforce VARCHAR length.
</reusable-compact>

<reusable-compact filename="ARCHITECTURE.md">
Executable: ./ledger (root, sh launcher) -> python -m cli -> cli.main(argv) -> int. main never calls sys.exit; exit codes 0 success, 1 operational failure, 2 usage.
cli package: main(argv: list[str] | None = None) -> int; cli.testing.cli_runner(*args) -> (exit_code, stdout, stderr) in process; root conftest.py provides fixture cli_runner.
Database location: DATABASE_URL, then DATABASE_PATH, then data/app.db. Only database_location reads these.
Persistence: only via persistence package (open_database(dsn), db.<table>.<verb>(...)); no module imports a driver.
Money: integer cents everywhere; no floats.
Each command runs in one transaction; balance check before commit.
Network: none, except to a PostgreSQL DSN (this build rejects it with exit 1).
Config reads: only database_location reads env vars.
</reusable-compact>

<blueprint-decisions>
[{"spec":"DATABASE.md","severity":"Material","subject":"Lint scope for Drydock-generated persistence/","decision":"The generated persistence/schema.py annotates rows with VARCHAR(n)/INTEGER, which are undefined names, and the shipped postgres.py/testing.py fail ruff. I excluded persistence/ from ruff in pyproject.toml (extend-exclude) rather than editing generated or shipped code. Is that acceptable, or should the generator emit lint-clean output?"},{"spec":"FEATURE-CLI-Platform.md","severity":"Low","subject":"main() on argparse exits","decision":"main catches the SystemExit argparse raises for usage errors and --help and returns its code, so main never exits in-process. The launcher and python -m cli still exit with that code."},{"spec":"FEATURE-CLI-Platform.md","severity":"Low","subject":"Placeholder command dispatch","decision":"commands.dispatch returns 2 with an unknown-command diagnostic for every command, because no handlers exist until cli-dispatch. This is intentional and will be replaced by routing."}]
</blueprint-decisions>

RESULT: SUCCESS

FILES CHANGED:
- cli/__init__.py
- cli/__main__.py
- cli/parser.py
- cli/commands.py
- cli/testing.py
- conftest.py
- ledger
- pyproject.toml
- tests/test_cli_platform.py
- tests/test_database_step.py
- tests/test_foundation.py

SUMMARY:
- database-step: persistence/ and schema.sql were already generated by Drydock and match DATABASE.md and the shipped Rigging library. I did not modify them. tests/test_database_step.py covers the declared operations, FK and duplicate refusal, idempotent DDL, and persistence across reopen.
- cli-foundation: cli package (main, cli_runner, __main__, parser, placeholder dispatch), root conftest.py providing the cli_runner fixture, and the executable ledger launcher. tests/test_cli_platform.py covers the FEATURE-CLI-Platform acceptance assertions and the launcher exit codes.
- Lint: pyproject.toml excludes generated persistence/ from ruff. One line of block 1's tests/test_foundation.py gained check=False (behavior unchanged).
- Test invocations run: `sh bin/test.sh` → 61 passed, 0 failed. `sh bin/lint.sh` → clean. `sources/run.sh` not run (terminal story, outside this block).

BLOCKERS:
- None.
