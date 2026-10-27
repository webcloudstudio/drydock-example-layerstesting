# FEATURE: CLI Entry

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | The `ledger` executable, command registry, dispatch rules, and stdout/stderr/exit-code contract. |
| Depends On | ARCHITECTURE.md, DATABASE.md |
| Provides | ledger, cli.registry |
| Consumes | persistence.accounts, persistence.categories, persistence.transactions |

## Purpose

Provide the single entry point through which every command runs. It resolves the command words, checks the argument count, opens the database, calls the handler, and turns the result into CSV on stdout or one diagnostic line on stderr with the contract exit code.

## Interface

- `ledger` at the application root: a POSIX launcher that activates `.venv` and calls `cli.main(sys.argv[1:])`, exiting with its return value.
- `cli.main(argv: list[str] | None = None) -> int`.
- `cli.testing.cli_runner(*args) -> (exit_code, stdout, stderr)`, running `main` in process.
- `cli.registry`:
  - `Command(handler, min_args, max_args)`, a named tuple. `max_args` is `None` when unbounded.
  - `COMMANDS: dict[tuple[str, ...], Command]`, keyed by command words such as `("account", "add")`.
  - `load()`, idempotent: imports every module in `cli/commands/` and adds the entries of each module's `COMMANDS` mapping. It never removes entries.
- Handler signature: `handler(db, args: list[str]) -> list[list[str]]`, where `db` is the opened database and `args` are the words after the command words. It returns every output row, header first, as lists of text.

## Dispatch Rules

1. Call `registry.load()`.
2. Match the longest command-word prefix of `argv` in `COMMANDS`. No match, an empty `argv`, or a known group word with an unknown sub-word (unknown table or report) is a usage error.
3. An argument count outside `min_args..max_args` is a usage error.
4. A usage error exits `2`, writes one diagnostic line to stderr, and writes nothing to stdout.
5. Open the database with `persistence.open_database(ledger_core.config.database_path())`. A failure to open exits `1`.
6. Call the handler. On success, write the rows to stdout as CSV: comma-separated, no quoting, no trailing spaces, `\n` line endings. Nothing is written to stdout before the handler returns.
7. A `LedgerError` exits with its `exit_code` and one stderr line. Any other exception exits `1` with one stderr line. Stdout stays empty in both cases.

Handlers validate every input and rule before their first write. Check order inside a handler: input validation (exit 3), then existence lookups (exit 4), then business rules (exit 3).

## Database Interface

- None — persistence is owned by DATABASE.md; this entry point only opens the database and passes it to handlers.

## Programmatic Acceptance

=== AC cli-registry-load ===
Intent: Registry loading is idempotent and every key is a tuple of words.

from cli import registry

registry.load()
count = len(registry.COMMANDS)
registry.load()
assert len(registry.COMMANDS) == count
for words in registry.COMMANDS:
    assert isinstance(words, tuple)
    assert all(isinstance(w, str) for w in words)
=== END AC cli-registry-load ===

=== AC cli-unknown-command ===
Intent: An unknown command, or no command at all, exits 2 with an empty stdout and exactly one stderr line.

from cli.testing import cli_runner

for args in [("zzfrobnicate",), ()]:
    code, out, err = cli_runner(*args)
    print(code, repr(out), repr(err))
    assert code == 2
    assert out == ""
    assert len(err.strip().splitlines()) == 1
=== END AC cli-unknown-command ===

=== AC cli-dispatch-success ===
Intent: A registered command receives its arguments and its rows print as unquoted CSV with newline endings.

import csv
import io
from cli import registry
from cli.testing import cli_runner

arg = "alpha"
words = ("zzgrp", "ok")

def handler(db, args):
    return [["h1", "h2"], [args[0], "v"]]

registry.load()
registry.COMMANDS[words] = registry.Command(handler, 1, 1)
try:
    code, out, err = cli_runner(*words, arg)
    print(code, repr(out), repr(err))
    assert code == 0
    assert list(csv.reader(io.StringIO(out))) == [["h1", "h2"], [arg, "v"]]
    assert "\r" not in out
    assert out.endswith("\n")
finally:
    registry.COMMANDS.pop(words, None)
=== END AC cli-dispatch-success ===

=== AC cli-usage-errors ===
Intent: A wrong argument count, a bare group word, and a group word with an unknown sub-word each exit 2 with empty stdout.

from cli import registry
from cli.testing import cli_runner

words = ("zzgrp2", "ok")

def handler(db, args):
    return [["h"], [args[0]]]

registry.load()
registry.COMMANDS[words] = registry.Command(handler, 1, 1)
try:
    cases = [words, words + ("a", "b"), ("zzgrp2",), ("zzgrp2", "nosuch")]
    for args in cases:
        code, out, err = cli_runner(*args)
        print(args, code, repr(out), repr(err))
        assert code == 2
        assert out == ""
        assert err.strip() != ""
finally:
    registry.COMMANDS.pop(words, None)
=== END AC cli-usage-errors ===

=== AC cli-domain-error-codes ===
Intent: Handlers raising Rejected, NotFound, or Operational exit 3, 4, or 1 and print nothing to stdout.

from cli import registry
from cli.testing import cli_runner
from ledger_core.errors import Rejected, NotFound, Operational

cases = {"rej": (Rejected, 3), "nf": (NotFound, 4), "op": (Operational, 1)}
registry.load()
added = []
try:
    for word, (cls, expected) in cases.items():
        def handler(db, args, cls=cls):
            raise cls("probe failure")
        key = ("zzerr", word)
        registry.COMMANDS[key] = registry.Command(handler, 0, 0)
        added.append(key)
        code, out, err = cli_runner(*key)
        print(word, code, repr(out), repr(err))
        assert code == expected
        assert out == ""
        assert len(err.strip().splitlines()) == 1
finally:
    for key in added:
        registry.COMMANDS.pop(key, None)
=== END AC cli-domain-error-codes ===

=== AC cli-unopenable-database ===
Intent: A database location that cannot be opened exits 1 with empty stdout.

from drydock_acceptance import database_environment
from cli import registry
from cli.testing import cli_runner

words = ("zzopen", "ok")

def handler(db, args):
    return [["h"]]

registry.load()
registry.COMMANDS[words] = registry.Command(handler, 0, 0)
try:
    with database_environment(url="missing/app.db"):
        code, out, err = cli_runner(*words)
        print(code, repr(out), repr(err))
        assert code == 1
        assert out == ""
finally:
    registry.COMMANDS.pop(words, None)
=== END AC cli-unopenable-database ===

=== AC cli-launcher ===
Intent: The ledger launcher at the application root is executable and exits 2 for an unknown command with empty stdout.

import os
import subprocess

assert os.access("ledger", os.X_OK)
result = subprocess.run(["./ledger", "zzfrobnicate"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
assert result.returncode == 2
assert result.stdout == ""
=== END AC cli-launcher ===

## User Acceptance

- None.

## Guardrails

- A failing command writes nothing to stdout and exactly one diagnostic line to stderr.
- Stdout is written only after the handler has returned successfully.
- Output uses `\n` line endings, no quoting, and no trailing spaces.
- Only `cli` dispatch produces exit code 2.
