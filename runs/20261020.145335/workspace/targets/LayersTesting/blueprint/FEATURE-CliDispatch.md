# FEATURE: CLI Dispatch

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Routes command words to handlers, rejects usage errors with exit 2, and provides help for every command. |
| Depends On  | ARCHITECTURE.md, FEATURE-CliEntry.md |
| Provides    | command dispatch, ledger --help, ledger <command> --help |

## Purpose

`cli.main` reads the first argument as the command word and dispatches it. Unknown commands,
unknown tables, unknown reports, and wrong argument counts are usage errors: they exit 2, write
nothing to standard output, and write one diagnostic line to standard error. Every command has
help text. `--help` and `<command> --help` write usage to standard output and exit 0. With no
arguments, `main` writes one usage line to standard error and exits 2.

## Commands Recognized

`init`, `count`, `load`, `account` (`add`, `get`, `rename`, `delete`), `txn` (`post`, `get`,
`amend`, `delete`), `transfer`, `report` (`balances`, `categories`, `monthly`).

## Programmatic Acceptance

=== AC dispatch-help ===
Intent: ledger --help and the --help of each recognized command print usage to standard output and exit 0.

from cli.testing import cli_runner

help_cases = [
    ["--help"],
    ["init", "--help"],
    ["count", "--help"],
    ["load", "--help"],
    ["account", "add", "--help"],
    ["txn", "post", "--help"],
    ["transfer", "--help"],
    ["report", "balances", "--help"],
]
for argv in help_cases:
    code, out, err = cli_runner(*argv)
    print(argv, code, err)
    assert code == 0
    assert out.strip() != ""
=== END AC dispatch-help ===

=== AC dispatch-unknown-command ===
Intent: An unknown command exits 2 and writes one diagnostic line to standard error and nothing to standard output.

from cli.testing import cli_runner

unknown = "frobnicate"
code, out, err = cli_runner(unknown)
print(err)
assert code == 2
assert out == ""
assert len([line for line in err.splitlines() if line.strip()]) == 1
=== END AC dispatch-unknown-command ===

=== AC dispatch-usage-errors ===
Intent: An unknown table, an unknown report, and wrong argument counts each exit 2 with nothing on standard output.

from cli.testing import cli_runner

usage_cases = [
    ["load", "nosuch", "bogus.csv"],
    ["report", "nosuch"],
    ["txn", "get"],
    ["init", "extra"],
]
for argv in usage_cases:
    code, out, err = cli_runner(*argv)
    print(argv, code, err)
    assert code == 2
    assert out == ""
=== END AC dispatch-usage-errors ===

=== AC dispatch-no-arguments ===
Intent: Invoking ledger with no arguments writes one usage line to standard error and exits 2.

from cli.testing import cli_runner

code, out, err = cli_runner()
print(err)
assert code == 2
assert out == ""
assert len([line for line in err.splitlines() if line.strip()]) == 1
=== END AC dispatch-no-arguments ===

## User Acceptance

- None.

## Guardrails

- A usage error never opens the database.
- Help text is written only to standard output, never to standard error.
- Standard error is diagnostic only and is never the success path.
