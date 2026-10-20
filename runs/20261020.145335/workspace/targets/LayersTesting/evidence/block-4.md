# Evidence: Block 4 · Service (block-4)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 6905
- execution id: 20261020.151716.470Z-75ad6461

## Stories built
- Dispatch commands and reject usage errors with exit 2. (CLI-001) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1145)
- implements: FEATURE-CliDispatch.md (SP 1180)
- context: ARCHITECTURE_compact.md (SP 427)
- context: DATABASE_compact.md (SP 427)
- stack: cli.md (SP 2689)

## Build directory changes
- cli/__init__.py
- cli/commands.py
- cli/parser.py
- tests/test_dispatch.py

## Pre-build acceptance observation
- RED: dispatch-help (FEATURE-CliDispatch.md)
  intent: ledger --help and the --help of each recognized command print usage to standard output and exit 0.
  return code: 1
  stdout:
    ['--help'] 0 
    ['init', '--help'] 2 usage: ledger [-h] <command> ...
    ledger: error: argument <command>: invalid choice: 'init' (choose from )
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "dispatch-help.py", line 16, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: dispatch-unknown-command (FEATURE-CliDispatch.md)
  intent: An unknown command exits 2 and writes one diagnostic line to standard error and nothing to standard output.
  return code: 1
  stdout:
    usage: ledger [-h] <command> ...
    ledger: error: argument <command>: invalid choice: 'frobnicate' (choose from )
  stderr:
    --- drydock: values at failure ---
      err = "usage: ledger [-h] <command> ...\nledger: error: argument <command>: invalid choice: 'frobnicate' (choose from )\n"
    --- drydock: end values ---
    Traceback (most recent call last):
      File "dispatch-unknown-command.py", line 8, in <module>
        assert len([line for line in err.splitlines() if line.strip()]) == 1
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- GREEN (prepassed): dispatch-usage-errors (FEATURE-CliDispatch.md)
  intent: An unknown table, an unknown report, and wrong argument counts each exit 2 with nothing on standard output.
  return code: 0
  stdout:
    ['load', 'nosuch', 'bogus.csv'] 2 usage: ledger [-h] <command> ...
    ledger: error: argument <command>: invalid choice: 'load' (choose from )
    
    ['report', 'nosuch'] 2 usage: ledger [-h] <command> ...
    ledger: error: argument <command>: invalid choice: 'report' (choose from )
    
    ['txn', 'get'] 2 usage: ledger [-h] <command> ...
    ledger: error: argument <command>: invalid choice: 'txn' (choose from )
    
    ['init', 'extra'] 2 usage: ledger [-h] <command> ...
    ledger: error: argument <command>: invalid choice: 'init' (choose from )
- RED: dispatch-no-arguments (FEATURE-CliDispatch.md)
  intent: Invoking ledger with no arguments writes one usage line to standard error and exits 2.
  return code: 1
  stdout:
    usage: ledger [-h] <command> ...
    ledger: error: the following arguments are required: <command>
  stderr:
    --- drydock: values at failure ---
      err = 'usage: ledger [-h] <command> ...\nledger: error: the following arguments are required: <command>\n'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "dispatch-no-arguments.py", line 7, in <module>
        assert len([line for line in err.splitlines() if line.strip()]) == 1
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError

## Post-build programmatic acceptance
- PASS: dispatch-help (FEATURE-CliDispatch.md)
  intent: ledger --help and the --help of each recognized command print usage to standard output and exit 0.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ['--help'] 0 
    ['init', '--help'] 0 
    ['count', '--help'] 0 
    ['load', '--help'] 0 
    ['account', 'add', '--help'] 0 
    ['txn', 'post', '--help'] 0 
    ['transfer', '--help'] 0 
    ['report', 'balances', '--help'] 0
- PASS: dispatch-unknown-command (FEATURE-CliDispatch.md)
  intent: An unknown command exits 2 and writes one diagnostic line to standard error and nothing to standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: argument <command>: invalid choice: 'frobnicate' (choose from init, count, load, account, txn, transfer, report)
- PASS: dispatch-usage-errors (FEATURE-CliDispatch.md)
  intent: An unknown table, an unknown report, and wrong argument counts each exit 2 with nothing on standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ['load', 'nosuch', 'bogus.csv'] 2 error: argument table: invalid choice: 'nosuch' (choose from accounts, categories, transactions)
    
    ['report', 'nosuch'] 2 error: argument <report>: invalid choice: 'nosuch' (choose from balances, categories, monthly)
    
    ['txn', 'get'] 2 error: the following arguments are required: txn_id
    
    ['init', 'extra'] 2 error: unrecognized arguments: extra
- PASS: dispatch-no-arguments (FEATURE-CliDispatch.md)
  intent: Invoking ledger with no arguments writes one usage line to standard error and exits 2.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: the following arguments are required: <command>

## Build summary
The existing `cli/` package has a stub dispatcher and no subcommands, so the work is in the parser (subcommands, help, one-line usage errors) and the dispatch routing. I'll write the parser first.Next, the dispatcher routes on the leaf command name and reports recognized commands whose handlers aren't built yet, instead of pretending they succeeded.Now the tests, one behavior per test, covering the four declared acceptance checks plus the per-command help and usage boundaries.The instructions forbid asserting on substrings of stdout/stderr, so I'm removing those text checks and keeping only exit codes, stream emptiness, and line counts.Running the project suite, plus the four declared acceptance checks from `FEATURE-CliDispatch.md` replayed verbatim outside the repo.All 96 tests pass and the four acceptance checks pass. Checking that only the intended files changed:RESULT: SUCCESS

FILES CHANGED:
- cli/parser.py
- cli/commands.py
- cli/__init__.py
- tests/test_dispatch.py

SUMMARY:
- Dispatch now recognizes every command word in FEATURE-CliDispatch.md: `init`, `count`, `load`, `account` (`add`, `get`, `rename`, `delete`), `txn` (`post`, `get`, `amend`, `delete`), `transfer`, and `report` (`balances`, `categories`, `monthly`). Each has help text.
- Usage errors are one stderr line with exit 2 and empty stdout. The parser's `error()` now raises `UsageError`, and `main` prints it as a single line. Argparse's default output was two lines, which would have failed the one-line check.
- `--help` and `<command> --help` print to stdout and exit 0.
- No arguments exits 2 with one stderr line.
- Declared acceptance checks: all four (`dispatch-help`, `dispatch-unknown-command`, `dispatch-usage-errors`, `dispatch-no-arguments`) pass when run verbatim outside the repo.
- Project suite: `sh bin/test.sh` gives 96 passed, including 73 new tests in `tests/test_dispatch.py` and the existing CLI and foundation tests.
- No staged suite was run; this block's criteria don't invoke `sources/run.sh`.
- No database is opened by any path in this block.

Choices I made:
- A recognized command whose handler isn't built yet (all of them in this block) exits 1 with a stderr diagnostic. I didn't make it succeed silently or exit 2.
- The argument shapes I declared are the minimum needed: `load <table> <file>` with table choices from the DATABASE.md table names, `txn get <txn_id>` with an integer id, and `report <name>` with the three report names. Other verbs take no positionals for now, so extra arguments are rejected until their blocks define them.
- The help strings for `count` and the verbs are my wording, since the spec gives no descriptions.

<blueprint-decisions>
[{"spec":"FEATURE-CliDispatch.md","severity":"Low","subject":"Recognized command with no handler yet","decision":"Options were to exit 0 silently, exit 2, or exit 1 with a stderr diagnostic. I chose exit 1 with a diagnostic so unbuilt commands are not mistaken for success or for usage errors. Later blocks replace this by registering handlers in commands.HANDLERS. Is that acceptable?"},{"spec":"FEATURE-CliDispatch.md","severity":"Low","subject":"Argument shapes for commands not yet specified in this block","decision":"Declared load <table> <file>, txn get <txn_id> (int), and report <name> with choices, because the usage-error checks need them. Other verbs take no positionals for now. Should these shapes change when their owning blocks are built?"}]
</blueprint-decisions>
