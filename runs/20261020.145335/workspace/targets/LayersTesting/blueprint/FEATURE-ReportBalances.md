# FEATURE: Report Balances

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | `ledger report balances` writes one row per account and a TOTAL row, computed from the database. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md, FEATURE-LoadTransactions.md, FEATURE-AccountRename.md, FEATURE-AccountDelete.md, FEATURE-TxnAmend.md, FEATURE-TxnDelete.md, FEATURE-Transfer.md |
| Provides    | ledger report balances |
| Consumes    | accounts.list, accounts.get, transactions.list |

## Purpose

Report the balance of every account. The balance of an account is the sum of its transaction
amounts, in integer cents. Output is produced only from rows read from the database.

## Trigger

`ledger report balances` with no further arguments.

## Behavior

- Read every account through `accounts.list`, ordered by `account` ascending.
- For each account, compute `transactions` (the count of its transactions) and `balance` (the sum
  of its transaction amounts) from `transactions.list`, never from a stored value.
- Write the header `account,name,transactions,balance`, then one row per account in code order.
- Write `TOTAL,,<count>,<sum>` as the final row, where `<count>` is the total transaction count and
  `<sum>` is the sum of all transaction amounts.
- Amounts are written with exactly two decimals, a leading `-` when negative, and no thousands
  separator.
- With no accounts, write the header and `TOTAL,,0,0.00`.
- Exit 0 on success.
- A database that cannot be read exits 1 with nothing on standard output.

## Output

```text
account,name,transactions,balance
DRAWER1,Front Drawer,39,2299.38
...
TOTAL,,120,4233.95
```

## Programmatic Acceptance

=== AC RPT-001-empty-balances ===
Intent: On an empty accounts table, report balances writes the header and TOTAL,,0,0.00.
Suite: scoped
Requires: executable=python3; scope=test

import subprocess
import sys

from persistence.testing import db_session

with db_session() as db:
    expected_header = "account,name,transactions,balance"
    expected_total = "TOTAL,,0,0.00"
    result = subprocess.run(
        [sys.executable, "-m", "cli", "report", "balances"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr, file=sys.stderr)
    lines = [line for line in result.stdout.splitlines() if line]
    assert result.returncode == 0
    assert lines[0] == expected_header
    assert lines[-1] == expected_total
=== END AC RPT-001-empty-balances ===

=== AC RPT-001-total-row-from-database ===
Intent: The TOTAL row is produced by a query, with one row per account, after loading seeded accounts.
Suite: scoped
Requires: executable=python3; scope=test

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.accounts.create(account="DRAWER1", name="Front Drawer")
    db.accounts.create(account="SAFE", name="Store Safe")
    code, out, err = cli_runner("report", "balances")
    rows = [line for line in out.splitlines() if line]
    assert code == 0
    assert len(rows) == 1 + 2 + 1
    assert rows[-1].startswith("TOTAL,,")
    assert rows[1].split(",")[0] == "DRAWER1"
    assert rows[2].split(",")[0] == "SAFE"
=== END AC RPT-001-total-row-from-database ===

## User Acceptance

- None.

## Guardrails

- No balance, count, or total is embedded as a literal; each value is computed by a query.
- Application code does not read `sources/run.sh` or any seed file.
