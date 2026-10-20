# FEATURE: CLI Entry

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provides the ledger executable at the application root and the cli.main entry point with its test client. |
| Depends On  | ARCHITECTURE.md |
| Provides    | ledger, cli.main, cli.testing.cli_runner |

## Purpose

`ledger` is the only command-line entry point. It is a POSIX launcher at the application root.
It changes into the application root and runs `cli.main(argv)` under the `.venv` interpreter,
then exits with the returned status. `cli.main` takes an argument list and returns an integer
status. `cli.testing.cli_runner(*args)` calls `main` in-process and returns `(exit_code, stdout,
stderr)`.

## Launcher Contract

```
#!/bin/sh
HERE=$(cd "$(dirname "$0")" && pwd)
cd "$HERE" && exec "$HERE/.venv/bin/python" -c 'import sys; from cli import main; sys.exit(main(sys.argv[1:]))' "$@"
```

## Programmatic Acceptance

=== AC cli-entry-executable ===
Intent: The ledger executable is a file at the application root with its execute bit set.

import os
from pathlib import Path

ledger_path = Path("ledger")
assert ledger_path.is_file()
assert os.access(ledger_path, os.X_OK)
=== END AC cli-entry-executable ===

=== AC cli-entry-main-contract ===
Intent: cli_runner returns an integer status and two strings, and the ledger executable exits with the same status for the same argv.

import subprocess
from pathlib import Path
from cli.testing import cli_runner

args = ["no-such-command"]
code, out, err = cli_runner(*args)
assert isinstance(code, int)
assert isinstance(out, str)
assert isinstance(err, str)
proc = subprocess.run([str(Path("ledger").resolve()), *args], capture_output=True, text=True)
print(proc.stdout)
print(proc.stderr)
assert proc.returncode == code
=== END AC cli-entry-main-contract ===

## User Acceptance

- None.

## Guardrails

- The `ledger` launcher never invokes a system Python for command execution; it always uses `.venv`.
- The cli package never opens a database connection.
- The launcher writes nothing to standard output of its own.
