# FEATURE: Persistence Lifecycle

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provides schema initialization and deterministic table-count commands. |
| Depends On  | ARCHITECTURE.md, DATABASE.md |
| Provides    | ledger init, ledger count |
| Consumes    | relational ledger schema, persistence operations |

## Purpose

The lifecycle commands establish a known empty ledger and expose row counts for all three tables.

## Workflows

### Initialize

`ledger init` drops and recreates `accounts`, `categories`, and `transactions`. It writes no standard output on success.

### Count

`ledger count` reports:

- `table,rows`
- `accounts`
- `categories`
- `transactions`

Rows always appear in that order.

## Programmatic Acceptance

=== AC persistence-init-clears-state ===
Intent: Initialization succeeds and the subsequent count observes the empty ledger state.
from cli.testing import cli_runner

init_code, init_out, init_err = cli_runner("init")
assert init_code == 0
assert init_out == ""

count_code, count_out, count_err = cli_runner("count")
assert count_code == 0
assert count_out
assert isinstance(count_err, str)
=== END AC persistence-init-clears-state ===

=== AC persistence-count-contract ===
Intent: Count returns a successful structured result for the three declared tables.
from cli.testing import cli_runner

code, output, err = cli_runner("count")
assert code == 0
lines = output.splitlines()
expected_line_count = 4
assert len(lines) == expected_line_count
assert lines[0].split(",") == ["table", "rows"]
assert [line.split(",")[0] for line in lines[1:]] == ["accounts", "categories", "transactions"]
assert isinstance(err, str)
=== END AC persistence-count-contract ===

=== AC persistence-reinitialization ===
Intent: Reinitialization removes previously persisted rows.
from cli.testing import cli_runner

init_code, _, _ = cli_runner("init")
assert init_code == 0

account_code, _, _ = cli_runner("account", "add", "TEMP1", "Temporary")
assert account_code == 0

reset_code, reset_out, reset_err = cli_runner("init")
assert reset_code == 0
assert reset_out == ""

count_code, count_out, count_err = cli_runner("count")
assert count_code == 0
assert "TEMP1" not in count_out
assert isinstance(reset_err, str)
assert isinstance(count_err, str)
=== END AC persistence-reinitialization ===

## User Acceptance

- None.

## Guardrails

- `init` emits no standard output.
- `count` uses the exact header and table order.
- Initialization recreates all three tables.
- A failed lifecycle command emits no standard output.
