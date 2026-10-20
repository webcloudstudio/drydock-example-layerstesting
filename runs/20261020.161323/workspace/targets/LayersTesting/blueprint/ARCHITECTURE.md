# ARCHITECTURE: Ledger Application Boundaries

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Defines the command-line ledger boundaries, configuration flow, and persistence ownership. |
| Depends On  | — |
| Provides    | application module boundaries, configuration boundary, persistence boundary |
| Consumes    | — |

## Purpose

The application is a Python 3.11+ command-line executable named `ledger`. It accepts commands and arguments, validates complete operations before writing, and emits deterministic CSV on success. Diagnostics are written to standard error.

## Modules and Ownership

| Boundary | Owner | Responsibility |
|---|---|---|
| Executable | `ledger` | Application-root entry point and process exit status |
| CLI | `cli` | Argument parsing, command dispatch, output formatting, and error mapping |
| Configuration | CLI/application configuration module | Resolve `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db` |
| Validation | Domain validation module | Codes, text fields, amounts, dates, identifiers, references, and balance rules |
| Services | Ledger command services | Atomic preflight, mutations, account lifecycle, loading, transfers, and reports |
| Persistence | `persistence` | Exclusive database access through generated shipped operations |
| Test runner | `bin/test.sh` | Invoke the project pytest suite from the application root |

Application code must not import or open a database driver directly. Services call the shipped persistence package and keep database details behind that boundary.

## Command Groups

- Lifecycle: `ledger init`, `ledger count`
- Loading: `ledger load accounts`, `ledger load categories`, `ledger load transactions`
- Accounts: `ledger account add`, `get`, `rename`, `delete`
- Transactions: `ledger txn post`, `get`, `amend`, `delete`
- Transfer: `ledger transfer`
- Reports: `ledger report balances`, `categories`, `monthly`

## Error Contract

Exit status `0` indicates success, `1` operational failure, `2` usage error, `3` rejected input or business rule, and `4` absent account or transaction. Successful commands write CSV except `init`; failures write no standard output and one diagnostic line to standard error.

## Technology Stack

- Python 3.11 or newer implements the application and tests.
- SQLite is the local relational database.
- The shipped Python persistence library is the only database access boundary.
- The CLI is the root executable interface.
- pytest runs the automated suite.
- POSIX shell runs `bin/test.sh` and the supplied conformance harness.

## Programmatic Acceptance

=== AC architecture-cli-boundary ===
Intent: The built CLI exposes the declared lifecycle commands through its public runner.
from cli.testing import cli_runner

init_code, init_out, init_err = cli_runner("init")
assert init_code == 0
assert init_out == ""
assert isinstance(init_err, str)

count_code, count_out, count_err = cli_runner("count")
assert count_code == 0
assert count_out
assert isinstance(count_err, str)
=== END AC architecture-cli-boundary ===

=== AC architecture-usage-boundary ===
Intent: Unknown commands use the declared usage-error exit status and produce no standard output.
from cli.testing import cli_runner

expected_code = 2
code, out, err = cli_runner("unknown-command")
assert code == expected_code
assert out == ""
assert isinstance(err, str)
=== END AC architecture-usage-boundary ===

## User Acceptance

- None.

## Guardrails

- Application code never reads or modifies files under `sources/`.
- Application code never opens a database driver outside the shipped persistence library.
- Amounts remain integer cents throughout the application.
- A rejected command performs no write.
- Reports derive all values from persisted data.
