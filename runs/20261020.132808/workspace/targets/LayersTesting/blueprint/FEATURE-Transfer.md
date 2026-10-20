# Feature: Transfer

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Store a transfer as two TRANSFER rows, or neither, under the non-negative balance rule. |
| Depends On  | DATABASE.md, FEATURE-Transaction-Post.md, FEATURE-Balance-Rule.md, FEATURE-Amount-Format.md, FEATURE-Date-Validation.md, FEATURE-Code-Validation.md, FEATURE-CLI-Output.md, FEATURE-CLI-Dispatch.md |
| Provides    | ledger transfer <from> <to> <amount> <date> |
| Consumes    | accounts.get, transactions.create, transactions.list |

## Purpose

`ledger transfer <from> <to> <amount> <date>` moves cash between two accounts. It stores two rows
in category `TRANSFER`: `-amount` on `<from>` and `+amount` on `<to>`. Both rows are stored or
neither is.

## Trigger

The user runs `ledger transfer <from> <to> <amount> <date>`.

## Behavior

1. Validate syntax before any lookup: `<amount>` parses as a positive amount, and `<date>` is a
   real `YYYY-MM-DD` date. Either failure exits 3.
2. Require `<from>` and `<to>` to differ. Equal accounts exit 3.
3. Within the command transaction, confirm both accounts exist through `accounts.get`. A missing
   account exits 3, not 4.
4. Take the next two ids: `n` and `n+1`, where `n` is one more than the largest `txn_id` present
   (1 in an empty table), using the shared next-id function from FEATURE-Transaction-Post.md.
5. Create the row `n` on `<from>` with amount `-amount` and memo `transfer to <to>`, and the row
   `n+1` on `<to>` with amount `+amount` and memo `transfer from <from>`. Both use category
   `TRANSFER`.
6. Apply the balance rule to both touched accounts (FEATURE-Balance-Rule.md). A negative balance
   exits 3 and rolls back both rows.
7. Commit and print the two rows in CSV with the header:

```text
txn_id,date,account,category,amount,memo
<n>,<date>,<from>,TRANSFER,-<amount>,transfer to <to>
<n+1>,<date>,<to>,TRANSFER,<amount>,transfer from <from>
```

Amounts are written with exactly two decimal places (FEATURE-Amount-Format.md).

## Routes and Interfaces

| Interface | Kind | Notes |
|---|---|---|
| `ledger transfer <from> <to> <amount> <date>` | CLI command | Exit 0 on success, 3 on rejection. |

## Reads and Writes

| Operation | Access | Repository operation | Notes |
|---|---|---|---|
| Confirm accounts | read | `accounts.get` | Missing account exits 3. |
| Read largest id | read | `transactions.list` | Next id is derived from the rows, never stored. |
| Insert the two rows | write | `transactions.create` | Both inserts run inside one command transaction. |

## Programmatic Acceptance

=== AC transfer-stores-two-rows ===
Intent: A valid transfer stores two TRANSFER rows with the next two ids and the stated memos.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="XFA1", name="Transfer From")
    db.accounts.create(account="XFB1", name="Transfer To")
    db.categories.create(category="TRANSFER", description="Internal transfer")
    db.transactions.create(txn_id=8001, date="2026-05-01", account="XFA1",
                           category="TRANSFER", amount=5000, memo="seed")
    code, out, err = cli_runner("transfer", "XFA1", "XFB1", "100.00", "2026-05-02")
    assert code == 0
    assert db.transactions.get(txn_id=8002).account == "XFA1"
    assert db.transactions.get(txn_id=8002).amount == -10000
    assert db.transactions.get(txn_id=8002).memo == "transfer to XFB1"
    assert db.transactions.get(txn_id=8003).account == "XFB1"
    assert db.transactions.get(txn_id=8003).amount == 10000
    assert db.transactions.get(txn_id=8003).memo == "transfer from XFA1"
=== END AC transfer-stores-two-rows ===

=== AC transfer-output-rows ===
Intent: A valid transfer prints the header and the two stored rows in CSV.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="XFA2", name="Transfer From B")
    db.accounts.create(account="XFB2", name="Transfer To B")
    db.categories.create(category="TRANSFER", description="Internal transfer")
    db.transactions.create(txn_id=8011, date="2026-05-01", account="XFA2",
                           category="TRANSFER", amount=5000, memo="seed")
    code, out, err = cli_runner("transfer", "XFA2", "XFB2", "25.50", "2026-05-03")
    assert code == 0
    lines = out.splitlines()
    assert lines[0] == "txn_id,date,account,category,amount,memo"
    assert lines[1] == "8012,2026-05-03,XFA2,TRANSFER,-25.50,transfer to XFB2"
    assert lines[2] == "8013,2026-05-03,XFB2,TRANSFER,25.50,transfer from XFA2"
=== END AC transfer-output-rows ===

=== AC transfer-rejects-same-account ===
Intent: A transfer naming the same account for both sides exits 3 and stores nothing.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="XFA3", name="Transfer Same")
    db.categories.create(category="TRANSFER", description="Internal transfer")
    code, out, err = cli_runner("transfer", "XFA3", "XFA3", "10.00", "2026-05-04")
    assert code == 3
    assert out == ""
    assert db.transactions.list() == []
=== END AC transfer-rejects-same-account ===

=== AC transfer-rejects-zero-amount ===
Intent: A transfer with a zero amount exits 3 and stores nothing.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="XFA4", name="Transfer Zero A")
    db.accounts.create(account="XFB4", name="Transfer Zero B")
    db.categories.create(category="TRANSFER", description="Internal transfer")
    code, out, err = cli_runner("transfer", "XFA4", "XFB4", "0.00", "2026-05-04")
    assert code == 3
    assert db.transactions.list() == []
=== END AC transfer-rejects-zero-amount ===

=== AC transfer-rejects-unknown-account ===
Intent: A transfer naming an unknown account exits 3, not 4, and stores nothing.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="XFA5", name="Transfer Known")
    db.categories.create(category="TRANSFER", description="Internal transfer")
    code, out, err = cli_runner("transfer", "XFA5", "NOSUCH", "10.00", "2026-05-04")
    assert code == 3
    assert db.transactions.list() == []
=== END AC transfer-rejects-unknown-account ===

=== AC transfer-rejects-overdraft ===
Intent: A transfer that would leave the source account below zero exits 3 and stores neither row.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="XFA6", name="Transfer Poor")
    db.accounts.create(account="XFB6", name="Transfer Rich")
    db.categories.create(category="TRANSFER", description="Internal transfer")
    db.transactions.create(txn_id=8061, date="2026-05-01", account="XFA6",
                           category="TRANSFER", amount=1000, memo="seed")
    code, out, err = cli_runner("transfer", "XFA6", "XFB6", "10.01", "2026-05-04")
    assert code == 3
    assert [t.txn_id for t in db.transactions.list()] == [8061]
=== END AC transfer-rejects-overdraft ===

## User Acceptance

- None.

## Guardrails

- Both rows are stored or neither; no partial transfer is ever visible.
- Transfer ids come from the shared next-id function, never from a separately stored counter.
- A rejected transfer prints nothing to standard output.
