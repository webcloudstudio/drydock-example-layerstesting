# FEATURE: Cli Entry

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | The cli package entry point: command registry, dispatch, exit-code mapping, CSV output, diagnostics, and database location. |
| Depends On | ARCHITECTURE.md, DATABASE.md |
| Provides | cli.main, cli.testing.cli_runner, cli.registry.register, cli.errors, cli.config.resolve_dsn, cli.context.open_store |

## Purpose

Every command in the ledger plugs into one dispatcher. This story builds the dispatcher and registers no command. Later stories add modules under `cli/commands/` that call `register`. `main` imports every module in the `cli.commands` package (for example with `pkgutil.iter_modules`) before dispatching, so adding a command never edits `main`.

## Interface

| Symbol | Contract |
|--------|----------|
| `cli.main(argv=None) -> int` | Runs one command and returns its exit code. `None` means `sys.argv[1:]`. |
| `cli.registry.register(words, handler, nargs)` | `words` is a tuple such as `("account", "add")`. `handler(args: list[str])` returns a list of rows (each a list of strings) or `None`. `nargs` is `(min, max)` for the arguments after the words. |
| `cli.errors.LedgerError(message)` | Base class with an integer `code`. Subclasses: `OperationalError` 1, `UsageError` 2, `Rejected` 3, `NotFound` 4. |
| `cli.config.resolve_dsn(environ) -> str` | Returns `DATABASE_URL`, else `DATABASE_PATH`, else the absolute path of `data/app.db` under the application root. An empty value counts as unset. The value is returned as written; the persistence library selects the engine and strips an optional `sqlite://` prefix. |
| `cli.context.open_store()` | Calls `persistence.open_database(resolve_dsn(os.environ))`. For a SQLite file it creates a missing parent directory first. |
| `cli.testing.cli_runner(*args)` | Returns `(exit_code, stdout, stderr)` by calling `main` in process. |

## Dispatch Rules

- The longest registered word prefix of `argv` selects the handler. No match, or no arguments at all, is a usage error (exit 2).
- An argument count outside `nargs` is a usage error (exit 2) and the handler is not called.
- The handler runs to completion before anything is written to standard output. Rows are then written with `csv.writer` semantics but unquoted fields, `\n` line endings, and `sys.stdout` looked up at call time.
- A `LedgerError` becomes its `code`, one diagnostic line on standard error, and nothing on standard output.
- A `persistence.PersistenceError` and any other unexpected exception become exit 1 with one diagnostic line.
- Diagnostics are never part of any contract; only the exit code and standard output are.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC cli-unknown-command ===
Intent: An unknown command exits 2 with nothing on standard output and one diagnostic line.

from cli.testing import cli_runner

code, out, err = cli_runner("zz-no-such-command")
print(out, err)
assert code == 2
assert out == ""
assert len(err.strip().splitlines()) == 1
=== END AC cli-unknown-command ===

=== AC cli-no-arguments ===
Intent: Running with no arguments is a usage error.

from cli.testing import cli_runner

code, out, err = cli_runner()
assert code == 2
assert out == ""
=== END AC cli-no-arguments ===

=== AC cli-success-csv ===
Intent: A registered handler's rows are written as unquoted CSV with LF endings and exit 0.

import csv
import io

from cli.registry import register
from cli.testing import cli_runner

rows = [["h1", "h2"], ["v1", "v2"]]
register(("zz-accept-ok",), lambda args: rows, (0, 0))
code, out, err = cli_runner("zz-accept-ok")
assert code == 0
assert list(csv.reader(io.StringIO(out, newline=""))) == rows
assert "\r" not in out
assert out.endswith("\n")
=== END AC cli-success-csv ===

=== AC cli-no-output-handler ===
Intent: A handler returning None exits 0 and writes nothing to standard output.

from cli.registry import register
from cli.testing import cli_runner

register(("zz-accept-quiet",), lambda args: None, (0, 0))
code, out, err = cli_runner("zz-accept-quiet")
assert code == 0
assert out == ""
=== END AC cli-no-output-handler ===

=== AC cli-error-codes ===
Intent: Each LedgerError subclass maps to its exit code and an unexpected exception maps to 1, with empty standard output.

from cli.errors import NotFound, OperationalError, Rejected, UsageError
from cli.registry import register
from cli.testing import cli_runner

cases = {
    "zz-rej": (Rejected, 3),
    "zz-nf": (NotFound, 4),
    "zz-op": (OperationalError, 1),
    "zz-us": (UsageError, 2),
}
for name, (exc, want) in cases.items():
    def handler(args, exc=exc):
        raise exc("diagnostic")
    register((name,), handler, (0, 0))
    code, out, err = cli_runner(name)
    print(name, code, err)
    assert code == want
    assert out == ""
    assert len(err.strip().splitlines()) == 1

def boom(args):
    raise RuntimeError("unexpected")

register(("zz-boom",), boom, (0, 0))
code, out, err = cli_runner("zz-boom")
assert code == 1
assert out == ""
=== END AC cli-error-codes ===

=== AC cli-argument-count ===
Intent: Too few or too many arguments is exit 2 and the handler runs only for a count within range.

from cli.registry import register
from cli.testing import cli_runner

calls = []

def handler(args):
    calls.append(list(args))
    return [["x"]]

register(("zz-one",), handler, (1, 1))
code, out, err = cli_runner("zz-one")
assert code == 2
assert calls == []
code, out, err = cli_runner("zz-one", "a", "b")
assert code == 2
assert calls == []
code, out, err = cli_runner("zz-one", "a")
assert code == 0
assert calls == [["a"]]
=== END AC cli-argument-count ===

=== AC cli-multiword-command ===
Intent: A two-word command dispatches on both words; the first word alone or an unknown second word is exit 2.

from cli.registry import register
from cli.testing import cli_runner

register(("zz-grp", "sub"), lambda args: [["ok"]], (0, 0))
code, out, err = cli_runner("zz-grp", "sub")
assert code == 0
code, out, err = cli_runner("zz-grp")
assert code == 2
code, out, err = cli_runner("zz-grp", "nosuch")
assert code == 2
assert out == ""
=== END AC cli-multiword-command ===

=== AC cli-resolve-dsn ===
Intent: The database location resolves from DATABASE_URL, then DATABASE_PATH, then data/app.db.

from cli.config import resolve_dsn

url = "postgresql://example.invalid/ledger"
path = "custom/ledger.db"
assert resolve_dsn({"DATABASE_URL": url, "DATABASE_PATH": path}) == url
assert resolve_dsn({"DATABASE_PATH": path}) == path
assert resolve_dsn({"DATABASE_URL": "", "DATABASE_PATH": path}) == path
default = resolve_dsn({})
assert default.endswith("app.db")
=== END AC cli-resolve-dsn ===

## User Acceptance

- None.

## Guardrails

- Nothing is written to standard output until the handler has returned successfully.
- Diagnostics go to standard error and are never compared.
- This story registers no command.
- Application code never imports a database driver; it uses `persistence.open_database`.
