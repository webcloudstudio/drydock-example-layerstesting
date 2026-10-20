# FEATURE: CLI Validation

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Validate command names, subcommands, reports, tables, and argument counts. |
| Depends On  | FEATURE-CLI-Dispatcher.md |
| Provides    | command usage validation, command help |
| Consumes    | command dispatch |

## Validation Rules

The CLI rejects unknown commands, unknown tables, unknown reports, and incorrect argument counts with exit code `2`. Every documented command and sub-verb has discoverable help text. Validation occurs before database mutation.

Documented command families and subcommands include:

- `init`
- `count`
- `load`
- `account add`, `account get`, `account rename`, `account delete`
- `txn post`, `txn get`, `txn amend`, `txn delete`
- `transfer`
- `report balances`, `report categories`, `report monthly`

## Programmatic Acceptance

=== AC cli-validation-unknown-command ===
Intent: An unknown command is rejected as a usage error.
from cli.testing import cli_runner

code, stdout, stderr = cli_runner("frobnicate")
assert code == 2
assert stdout == ""
assert stderr != ""
=== END AC cli-validation-unknown-command ===

=== AC cli-validation-unknown-report ===
Intent: An unknown report is rejected as a usage error.
from cli.testing import cli_runner

code, stdout, stderr = cli_runner("report", "nosuch")
assert code == 2
assert stdout == ""
assert stderr != ""
=== END AC cli-validation-unknown-report ===

=== AC cli-validation-argument-count ===
Intent: A documented command with an incorrect argument count is rejected as a usage error.
from cli.testing import cli_runner

code, stdout, stderr = cli_runner("account", "add")
assert code == 2
assert stdout == ""
assert stderr != ""
=== END AC cli-validation-argument-count ===

=== AC cli-validation-help ===
Intent: Help is available for the command dispatcher and documented command families.
from cli.testing import cli_runner

for arguments in (("--help",), ("account", "--help"), ("txn", "--help"), ("report", "--help")):
    code, stdout, stderr = cli_runner(*arguments)
    assert code == 0
    assert stdout != ""
=== END AC cli-validation-help ===

## User Acceptance

- None.

## Guardrails

- Usage errors must return exit code `2`.
- Argument validation must happen before writes.
- Help must cover every documented command family and sub-verb.
