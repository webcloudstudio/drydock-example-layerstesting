# FEATURE: Cli Foundation

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | The executable `ledger`, its command registry and dispatcher, and database location resolution. |
| Depends On | ARCHITECTURE.md, DATABASE.md |
| Provides | ledger, ledger.register_command, ledger_config.database_dsn |
| Consumes | persistence.open_database |

## Purpose

Give every later command a place to register and a single way to resolve and open the database.

## Executable

`ledger` sits at the application root with its executable bit set. It is a POSIX sh script that resolves its own directory, chooses `.venv/bin/python` when present and `python3` otherwise, and runs `PYTHONPATH=<root> exec <python> -m cli "$@"`. It does not change the working directory, so `data/app.db` is relative to the caller.

## Interface

- `cli.main(argv: list[str] | None = None) -> int` uses `sys.argv[1:]` when `argv` is `None`.
- `cli.register_command(name: str, handler)` registers a handler under `name`, either one word (`init`) or two words (`account add`).
- Dispatch: when at least two arguments are given and `args[0] + " " + args[1]` is registered, that handler receives `args[2:]`; otherwise when `args[0]` is registered its handler receives `args[1:]`. An empty argument list or an unregistered command writes one line to standard error and returns `2`, with nothing on standard output.
- A handler that returns normally yields exit `0`. Before the error-contract story lands, any exception from a handler writes one generic line to standard error and returns `1`.
- `cli/testing.py` provides `cli_runner(*args) -> (exit_code, stdout, stderr)` as in the CLI foundation contract.

## Database Location

`ledger_config.database_dsn(env=None) -> str` reads `env` (default `os.environ`): `DATABASE_URL` when set and non-empty, else `DATABASE_PATH` when set and non-empty, else `data/app.db`. The value is returned unchanged. `ledger_config.open_db()` returns `persistence.open_database(database_dsn())`. The DSN is never printed.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC cli-executable-present ===
Intent: The ledger launcher exists at the application root, is executable and starts with a shebang.

import os

assert os.path.isfile("ledger")
assert os.access("ledger", os.X_OK)
with open("ledger", "r", encoding="ascii") as handle:
    first = handle.read(2)
assert first == "#!"
=== END AC cli-executable-present ===

=== AC cli-no-arguments-usage ===
Intent: Calling main with no arguments exits 2 and writes nothing to standard output.

from cli.testing import cli_runner

code, out, err = cli_runner()
print(err)
assert code == 2
assert out == ""
=== END AC cli-no-arguments-usage ===

=== AC cli-unknown-command ===
Intent: An unregistered command exits 2 with nothing on standard output.

from cli.testing import cli_runner

code, out, err = cli_runner("zzunknowncmd")
assert code == 2
assert out == ""
=== END AC cli-unknown-command ===

=== AC cli-register-one-word ===
Intent: A registered one-word command receives the remaining arguments and exits 0.

import cli
from cli.testing import cli_runner

name = "zzecho"
seen = []
cli.register_command(name, lambda args: seen.append(list(args)))
given = ["alpha", "beta"]
code, out, err = cli_runner(name, *given)
assert code == 0
assert seen == [given]
=== END AC cli-register-one-word ===

=== AC cli-register-two-word ===
Intent: A registered two-word command is selected over the one-word group and receives the remaining arguments.

import cli
from cli.testing import cli_runner

group = "zzgroup"
verb = "sub"
seen = []
cli.register_command(group + " " + verb, lambda args: seen.append(list(args)))
given = ["x"]
code, out, err = cli_runner(group, verb, *given)
assert code == 0
assert seen == [given]
=== END AC cli-register-two-word ===

=== AC cli-dsn-resolution-order ===
Intent: The database location resolves DATABASE_URL, then DATABASE_PATH, then data/app.db, treating empty values as unset.

import ledger_config

url = "sqlite:///tmp/from_url.db"
path = "from_path.db"
default = "data/app.db"
assert ledger_config.database_dsn({"DATABASE_URL": url, "DATABASE_PATH": path}) == url
assert ledger_config.database_dsn({"DATABASE_PATH": path}) == path
assert ledger_config.database_dsn({"DATABASE_URL": "", "DATABASE_PATH": path}) == path
assert ledger_config.database_dsn({"DATABASE_URL": ""}) == default
assert ledger_config.database_dsn({}) == default
=== END AC cli-dsn-resolution-order ===

=== AC cli-open-db ===
Intent: open_db returns a persistence database exposing the declared tables.

import ledger_config

db = ledger_config.open_db()
assert hasattr(db, "accounts")
assert isinstance(db.accounts.list(), list)
=== END AC cli-open-db ===

=== AC cli-launcher-no-arguments ===
Intent: Running the ledger launcher itself with no arguments exits 2 with an empty standard output.

import os
import subprocess

result = subprocess.run(
    ["./ledger"], capture_output=True, text=True, env={**os.environ}
)
print(result.stdout)
print(result.stderr)
assert result.returncode == 2
assert result.stdout == ""
=== END AC cli-launcher-no-arguments ===

## User Acceptance

- None.

## Guardrails

- The DSN, any path credential and any password are never written to standard output or standard error.
- The database is opened only through `persistence.open_database`; no driver is imported.
- A dispatch failure writes nothing to standard output and nothing to the database.
