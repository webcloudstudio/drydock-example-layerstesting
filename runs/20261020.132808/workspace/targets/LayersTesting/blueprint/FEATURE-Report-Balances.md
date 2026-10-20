# Feature: Report Balances

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Print one balance row per account, ordered by code, then a TOTAL row, all computed from the database. |
| Depends On  | DATABASE.md, FEATURE-Amount-Format.md, FEATURE-Command-Transaction.md, FEATURE-CLI-Output.md, FEATURE-CLI-Dispatch.md |
| Provides    | ledger report balances |
| Consumes    | accounts.list, transactions.list |

## Purpose

`ledger report balances` reports each account's transaction count and balance, followed by a
TOTAL row across all accounts.

## Trigger

The user runs `ledger report balances`.

## Behavior

1. Within the command transaction, read every account through `accounts.list`, ordered by
   `account` ascending.
2. For each account, compute its transaction count and balance by query. The balance is the sum
   of its transaction amounts in integer cents, formatted per FEATURE-Amount-Format.md.
3. Print the header and one row per account:

```text
account,name,transactions,balance
```

4. Print the TOTAL row. Its count is the total number of transactions, and its balance is the sum
   of every transaction amount:

```text
TOTAL,,<count>,<sum>
```

5. With no accounts, print only `TOTAL,,0,0.00` after the header.

No value is embedded as a constant. Every count and sum is derived from a query.

## Routes and Interfaces

| Interface | Kind | Notes |
|---|---|---|
| `ledger report balances` | CLI command | Exit 0 on success. |

## Reads and Writes

| Operation | Access | Repository operation | Notes |
|---|---|---|---|
| List accounts | read | `accounts.list` | Ordered by code. |
| List transactions | read | `transactions.list` | Aggregated per account and in total. |

## Programmatic Acceptance

=== AC report-balances-header ===
Intent: The balances report begins with the account header line.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="RBA1", name="Report Balance A")
    code, out, err = cli_runner("report", "balances")
    assert code == 0
    assert out.splitlines()[0] == "account,name,transactions,balance"
=== END AC report-balances-header ===

=== AC report-balances-empty ===
Intent: With no accounts the report prints only the TOTAL row of zeros.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code, out, err = cli_runner("report", "balances")
    assert code == 0
    assert out.splitlines()[1:] == ["TOTAL,,0,0.00"]
=== END AC report-balances-empty ===

=== AC report-balances-row-values ===
Intent: Each account row carries its name, transaction count, and balance computed from its transactions.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="RBB1", name="Report Balance B")
    db.categories.create(category="RBC1", description="Report Category")
    db.transactions.create(txn_id=7001, date="2026-05-01", account="RBB1",
                           category="RBC1", amount=1250, memo="a")
    db.transactions.create(txn_id=7002, date="2026-05-02", account="RBB1",
                           category="RBC1", amount=-250, memo="b")
    code, out, err = cli_runner("report", "balances")
    assert code == 0
    rows = out.splitlines()
    assert rows[1] == "RBB1,Report Balance B,2,10.00"
=== END AC report-balances-row-values ===

=== AC report-balances-ordered-by-code ===
Intent: Account rows are ordered by account code ascending.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="RBZ1", name="Report Zed")
    db.accounts.create(account="RBY1", name="Report Yankee")
    code, out, err = cli_runner("report", "balances")
    assert code == 0
    rows = out.splitlines()
    assert rows[1].startswith("RBY1,")
    assert rows[2].startswith("RBZ1,")
=== END AC report-balances-ordered-by-code ===

=== AC report-balances-total-row ===
Intent: The TOTAL row sums every account's transaction count and balance.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="RBT1", name="Report Total One")
    db.accounts.create(account="RBT2", name="Report Total Two")
    db.categories.create(category="RBTC", description="Report Total Category")
    db.transactions.create(txn_id=7101, date="2026-05-01", account="RBT1",
                           category="RBTC", amount=300, memo="one")
    db.transactions.create(txn_id=7102, date="2026-05-01", account="RBT2",
                           category="RBTC", amount=-100, memo="two")
    code, out, err = cli_runner("report", "balances")
    assert code == 0
    assert out.splitlines()[-1] == "TOTAL,,2,2.00"
=== END AC report-balances-total-row ===

## User Acceptance

- None.

## Guardrails

- No count, sum, or total is hardcoded; every value comes from a query.
- Amounts are formatted with two decimals, never floating point, and a zero total prints `0.00`,
  never `-0.00`.
