# FEATURE: Bulk Reference Loading

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Loads account and category CSV files atomically after complete validation. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-Persistence-Lifecycle.md, FEATURE-Validation.md |
| Provides    | ledger load accounts, ledger load categories |
| Consumes    | domain validation, relational ledger schema, persistence operations |

## Purpose

The reference loaders import accounts and categories from CSV files whose headers exactly match the declared column order.

## Workflows

`ledger load accounts <csv>` expects `account,name`. `ledger load categories <csv>` expects `category,description`. The entire file is parsed and validated before any row is inserted.

Successful loading emits:

```text
table,loaded
<table>,<rows>
```

Duplicate keys, malformed rows, invalid text, unreadable files, or mismatched headers reject the command without partial writes.

## Programmatic Acceptance

=== AC reference-load-accounts ===
Intent: The account fixture loads through the public command and reports a successful result.
from cli.testing import cli_runner
from pathlib import Path

init_code, _, _ = cli_runner("init")
assert init_code == 0

path = str(Path("sources/seed_accounts.csv"))
code, output, err = cli_runner("load", "accounts", path)
assert code == 0
assert output
assert isinstance(err, str)

count_code, count_output, _ = cli_runner("count")
assert count_code == 0
assert count_output.splitlines()[1].split(",")[1] == "4"
=== END AC reference-load-accounts ===

=== AC reference-load-categories ===
Intent: The category fixture loads through the public command and produces seven persisted categories.
from cli.testing import cli_runner
from pathlib import Path

init_code, _, _ = cli_runner("init")
assert init_code == 0

path = str(Path("sources/seed_categories.csv"))
code, output, err = cli_runner("load", "categories", path)
assert code == 0
assert output
assert isinstance(err, str)

count_code, count_output, _ = cli_runner("count")
assert count_code == 0
assert count_output.splitlines()[2].split(",")[1] == "7"
=== END AC reference-load-categories ===

=== AC reference-load-rejects-duplicate ===
Intent: A duplicate reference load is rejected without changing the existing account count.
from cli.testing import cli_runner
from pathlib import Path

init_code, _, _ = cli_runner("init")
assert init_code == 0

path = str(Path("sources/seed_accounts.csv"))
first_code, _, _ = cli_runner("load", "accounts", path)
assert first_code == 0

second_code, second_out, second_err = cli_runner("load", "accounts", path)
expected_code = 3
assert second_code == expected_code
assert second_out == ""
assert isinstance(second_err, str)

count_code, count_output, _ = cli_runner("count")
assert count_code == 0
assert count_output.splitlines()[1].split(",")[1] == "4"
=== END AC reference-load-rejects-duplicate ===

=== AC reference-load-header-validation ===
Intent: A missing or unreadable reference file is rejected without standard output.
from cli.testing import cli_runner

code, output, err = cli_runner("load", "accounts", "sources/does-not-exist.csv")
expected_code = 1
assert code == expected_code
assert output == ""
assert isinstance(err, str)
=== END AC reference-load-header-validation ===

## User Acceptance

- None.

## Guardrails

- Only the declared reference-table headers and columns are accepted.
- The complete file is validated before the first write.
- Duplicate or invalid rows reject the entire batch.
- The application does not read seed files except when explicitly invoked through `ledger load`.
- Diagnostics go to standard error and are excluded from CSV comparisons.
