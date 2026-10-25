# FEATURE: Count

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | The `ledger count` command that reports the row count of each ledger table. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-CliEntry.md, FEATURE-Init.md |
| Provides | ledger count |
| Consumes | cli.registry.register, cli.context.open_store |

## Purpose

`ledger count` prints the number of rows in `accounts`, `categories`, and `transactions`, in that order.

Output is CSV: the header `table,rows`, then one row per table. The counts are read from the database on every call. `count` takes no arguments; the surfaced criterion that `count` with arguments beyond `count` is a usage error means any extra argument exits 2 with nothing on standard output. Tables missing from the database exit 1.

The registration is `register(("count",), handler, (0, 0))` in `cli/commands/count.py`. The handler computes each count as the length of the table's `list` result.

## Database Interface


- None — persistence is owned by DATABASE.md, FEATURE-AccountAdd.md, FEATURE-AccountDelete.md, FEATURE-AccountGet.md, FEATURE-AccountRename.md, FEATURE-Init.md, FEATURE-TxnAmend.md, FEATURE-TxnDelete.md, FEATURE-TxnGet.md, FEATURE-TxnPost.md.

## Programmatic Acceptance

=== AC count-reports-tables ===
Intent: ledger count lists the three tables in order with counts that grow by the rows the criterion adds.

import csv
import io

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    before = [
        len(db.accounts.list()),
        len(db.categories.list()),
        len(db.transactions.list()),
    ]
    acct_a = "ACPTCN1"
    acct_b = "ACPTCN2"
    cat = "ACPTCNC"
    db.accounts.create(account=acct_a, name="Count A")
    db.accounts.create(account=acct_b, name="Count B")
    db.categories.create(category=cat, description="Count Category")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    for offset in (1, 2, 3):
        db.transactions.create(
            txn_id=base + offset, date="2026-06-03", account=acct_a, category=cat,
            amount=100, memo=""
        )
    code, out, err = cli_runner("count")
    print(out, err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out, newline="")))
    assert rows[0] == ["table", "rows"]
    assert [r[0] for r in rows[1:]] == ["accounts", "categories", "transactions"]
    counts = [int(r[1]) for r in rows[1:]]
    assert counts == [before[0] + 2, before[1] + 1, before[2] + 3]
    assert "\r" not in out
=== END AC count-reports-tables ===

=== AC count-after-init ===
Intent: ledger count reports zero rows in every table after ledger init.

import csv
import io

from cli.testing import cli_runner

code, out, err = cli_runner("init")
assert code == 0
code, out, err = cli_runner("count")
assert code == 0
rows = list(csv.reader(io.StringIO(out, newline="")))
assert rows[0] == ["table", "rows"]
assert [r[0] for r in rows[1:]] == ["accounts", "categories", "transactions"]
assert [int(r[1]) for r in rows[1:]] == [0, 0, 0]
=== END AC count-after-init ===

=== AC count-usage-error ===
Intent: ledger count with an extra argument is exit 2 with nothing on standard output.

from cli.testing import cli_runner

code, out, err = cli_runner("count", "extra")
assert code == 2
assert out == ""
assert len(err.strip().splitlines()) == 1
=== END AC count-usage-error ===

## User Acceptance

- None.

## Guardrails

- Counts are always computed from database reads; no count is stored or embedded.
- `count` never writes to the database.
