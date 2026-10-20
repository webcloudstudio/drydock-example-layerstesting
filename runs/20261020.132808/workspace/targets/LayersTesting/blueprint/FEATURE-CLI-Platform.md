# FEATURE: CLI Platform

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provide the cli package entry point, the cli_runner test fixture, and the ledger launcher at the application root. |
| Depends On  | ARCHITECTURE.md |
| Provides    | cli.main(argv), cli.testing.cli_runner, ./ledger |

## Purpose

The CLI platform is the package every command handler plugs into. It owns the entry point, the
test fixture that runs the entry point in process, and the `ledger` launcher that delegates to it.
It does not route commands; command routing belongs to `FEATURE-CLI-Dispatch.md`.

## Interface

- `cli.main(argv: list[str] | None = None) -> int` returns an exit code.
- `cli.testing.cli_runner(*args: str) -> tuple[int, str, str]` returns `(exit_code, stdout, stderr)`
  without spawning a process.
- `./ledger` is an executable file at the application root that delegates its arguments to `cli.main`.

## Programmatic Acceptance

=== AC cli-main-callable ===
Intent: The cli package exposes main with the single parameter argv.

import inspect

import cli

assert callable(cli.main)
assert list(inspect.signature(cli.main).parameters) == ["argv"]
=== END AC cli-main-callable ===

=== AC cli-runner-shape ===
Intent: cli_runner returns a three-element tuple of an integer exit code and two text streams.

from cli.testing import cli_runner

result = cli_runner()
assert isinstance(result, tuple)
code, out, err = result
assert isinstance(code, int)
assert isinstance(out, str)
assert isinstance(err, str)
=== END AC cli-runner-shape ===

=== AC cli-launcher-executable ===
Intent: The ledger launcher is an executable file at the application root.

import os
from pathlib import Path

launcher = Path("ledger")
assert launcher.is_file()
assert os.access(launcher, os.X_OK)
=== END AC cli-launcher-executable ===

=== AC cli-launcher-shebang ===
Intent: The ledger launcher begins with an interpreter line.

from pathlib import Path

first_line = Path("ledger").read_text(encoding="utf-8").splitlines()[0]
assert first_line.startswith("#!")
=== END AC cli-launcher-shebang ===

## User Acceptance

- None.

## Guardrails

- Do not spawn a subprocess in any criterion. Criteria call `cli_runner` or import the entry point.
- The launcher contains no command logic; it only delegates to `cli.main`.
