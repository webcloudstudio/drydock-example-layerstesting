# FEATURE: CLI Help

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Print usage and arguments for every command and sub-verb on `--help`, exiting 0. |
| Depends On  | FEATURE-USAGE-ERRORS.md, FEATURE-SCHEMA-COUNT.md, FEATURE-ACCOUNT-DELETE.md, FEATURE-TXN-DELETE.md, FEATURE-TRANSFER-REJECTION.md, FEATURE-LOAD-HEADER.md, FEATURE-REPORT-MONTHLY.md |
| Provides    | `ledger <command> --help`, `ledger <command> <sub-verb> --help` |

## Purpose

Every command and sub-verb of the `ledger` executable prints its usage and arguments when `--help`
is given. The help output is written to standard output and the process exits 0. Help output is
exempt from the CSV output rule in FEATURE-CSV-OUTPUT.md.

## Behavior

- `--help` may follow any command or sub-verb in the Commands table of `sources/INSTRUCTIONS.md`.
- Help is printed before any argument validation. A command invoked with `--help` does not open the
  database and does not change any row.
- Help text is written to standard output only. Standard error stays empty.
- The exit status is 0.

## Commands and sub-verbs covered

| Command | Sub-verbs |
|---|---|
| `init`, `count`, `load`, `transfer` | none |
| `account` | `add`, `get`, `rename`, `delete` |
| `txn` | `post`, `get`, `amend`, `delete` |
| `report` | `balances`, `categories`, `monthly` |

## Programmatic Acceptance

=== AC cli-help-commands ===
Intent: Every top-level command and command group prints usage on stdout and exits 0 for --help.

from cli.testing import cli_runner

for argv in [["init"], ["count"], ["load"], ["transfer"], ["account"], ["txn"], ["report"]]:
    code, out, err = cli_runner(*argv, "--help")
    assert code == 0, argv
    assert out.strip() != "", argv
    assert err == "", argv
=== END AC cli-help-commands ===

=== AC cli-help-account ===
Intent: Every account sub-verb prints usage on stdout and exits 0 for --help.

from cli.testing import cli_runner

for argv in [["account", "add"], ["account", "get"], ["account", "rename"], ["account", "delete"]]:
    code, out, err = cli_runner(*argv, "--help")
    assert code == 0, argv
    assert out.strip() != "", argv
    assert err == "", argv
=== END AC cli-help-account ===

=== AC cli-help-txn ===
Intent: Every txn sub-verb prints usage on stdout and exits 0 for --help.

from cli.testing import cli_runner

for argv in [["txn", "post"], ["txn", "get"], ["txn", "amend"], ["txn", "delete"]]:
    code, out, err = cli_runner(*argv, "--help")
    assert code == 0, argv
    assert out.strip() != "", argv
    assert err == "", argv
=== END AC cli-help-txn ===

=== AC cli-help-report ===
Intent: Every report sub-verb prints usage on stdout and exits 0 for --help.

from cli.testing import cli_runner

for argv in [["report", "balances"], ["report", "categories"], ["report", "monthly"]]:
    code, out, err = cli_runner(*argv, "--help")
    assert code == 0, argv
    assert out.strip() != "", argv
    assert err == "", argv
=== END AC cli-help-report ===

## User Acceptance

- None.

## Guardrails

- `--help` never opens the database, never writes a row, and never drops or creates a table, including for `init`.
- Help output is never written to standard error.
- Help output does not follow the CSV output rule.
