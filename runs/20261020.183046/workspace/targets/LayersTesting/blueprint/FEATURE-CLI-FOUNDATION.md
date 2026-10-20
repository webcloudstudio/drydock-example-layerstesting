# FEATURE: CLI Foundation

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provide the executable ledger command, dispatch documented commands, and reject invalid usage. |
| Depends On  | ARCHITECTURE.md, DATABASE.md |
| Provides    | `./ledger`, CLI command dispatch, usage validation |
| Consumes    | accounts repository, categories repository, transactions repository |

## Purpose

The application root contains an executable named `ledger`. It dispatches the documented command families:

- `init`
- `count`
- `load`
- `account`
- `txn`
- `transfer`
- `report`

Unknown commands, unknown subcommands, unknown tables or reports, and incorrect argument counts return exit code `2`, write no standard output, and emit a diagnostic on standard error. Help or usage guidance is available for every command family and subcommand.

The CLI delegates database work and business rules to application services and the shipped persistence package.

## Command Surface

| Command family | Supported operations |
|---|---|
| Root | `init`, `count`, `load`, `transfer` |
| Account | `add`, `get`, `rename`, `delete` |
| Transaction | `post`, `get`, `amend`, `delete` |
| Report | `balances`, `categories`, `monthly` |

## Database Interface

- None — persistence is owned by the command feature services.

## Programmatic Acceptance

=== AC cli-help ===
Intent: The executable command surface provides successful help or usage entry points.

from cli.testing import cli_runner

for args in (("--help",), ("account", "--help"), ("txn", "--help"), ("report", "--help")):
    code, stdout, stderr = cli_runner(*args)
    assert code == 0
=== END AC cli-help ===

=== AC cli-unknown-command ===
Intent: An unknown root command is rejected with the documented usage exit code.

from cli.testing import cli_runner

code, stdout, stderr = cli_runner("frobnicate")
assert code == 2
assert stdout == ""
=== END AC cli-unknown-command ===

=== AC cli-unknown-report ===
Intent: An unknown report name is rejected with the documented usage exit code.

from cli.testing import cli_runner

code, stdout, stderr = cli_runner("report", "nosuch")
assert code == 2
assert stdout == ""
=== END AC cli-unknown-report ===

=== AC cli-argument-validation ===
Intent: Missing required command arguments are rejected without standard output.

from cli.testing import cli_runner

for args in (("account",), ("txn",), ("load",), ("transfer",), ("report",)):
    code, stdout, stderr = cli_runner(*args)
    assert code == 2
    assert stdout == ""
=== END AC cli-argument-validation ===

## User Acceptance

- None.

## Guardrails

- The root executable must be named exactly `ledger` and be executable.
- Diagnostics go to standard error and are not part of successful CSV output.
- The CLI must not bypass the service or persistence boundaries.
