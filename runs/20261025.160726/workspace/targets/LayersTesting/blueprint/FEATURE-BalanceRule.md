# FEATURE: Balance Rule

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Assembles and verifies that post, amend, delete, transfer, and load each reject any change that would leave an account balance below zero. |
| Depends On | FEATURE-TxnPost.md, FEATURE-TxnAmend.md, FEATURE-TxnDelete.md, FEATURE-TransferOverdraw.md, FEATURE-LoadRejection.md, FEATURE-LedgerCore.md, DATABASE.md |
| Provides | non-negative balance rule |

## Purpose

An account's balance is the sum of its transaction amounts in integer cents. No command may leave
any account balance below zero. This assembly story confirms that every mutating command applies the
shared projected-balance guard from the ledger core before its first write, and wires the guard into
any command that lacks it. A rejection exits `3`, prints nothing to standard output, and leaves every
table unchanged.

## Behavior

- `txn post` rejects a withdrawal larger than the account balance.
- `txn amend` rejects an amount that makes the resulting balance negative.
- `txn delete` rejects deleting a deposit that the remaining transactions depend on.
- `transfer` rejects an amount larger than the source balance.
- `load transactions` rejects a file whose rows, taken together, leave any balance negative, and
  stores none of its rows.
- Each command also allows a change that brings a balance to exactly zero.

## Database Interface

- `FEATURE-TXN-002` — read: list an account's transactions to compute balances - supplies: `account` - returns: `account`, `amount`

## Programmatic Acceptance

=== AC balance-rule-post ===
Intent: txn post rejects a withdrawal exceeding the balance and accepts one that brings it to zero.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "ACPTBP1"
    cat = "ACPTBPC"
    db.accounts.create(account=acct, name="Post Rule")
    db.categories.create(category=cat, description="Post Rule Category")
    tid = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=tid, date="2026-06-01", account=acct, category=cat, amount=5000, memo="")
    before = len(db.transactions.list())
    code, out, err = cli_runner("txn", "post", acct, cat, "-50.01", "2026-06-02")
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert len(db.transactions.list()) == before
    assert sum(t.amount for t in db.transactions.list(account=acct)) == 5000
    code, out, err = cli_runner("txn", "post", acct, cat, "-50.00", "2026-06-02")
    print(out)
    print(err)
    assert code == 0
    assert len(db.transactions.list()) == before + 1
    assert sum(t.amount for t in db.transactions.list(account=acct)) == 0
=== END AC balance-rule-post ===

=== AC balance-rule-amend ===
Intent: txn amend rejects an amount that would leave the balance negative and leaves the row unchanged.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "ACPTBA1"
    cat = "ACPTBAC"
    db.accounts.create(account=acct, name="Amend Rule")
    db.categories.create(category=cat, description="Amend Rule Category")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    deposit_id = base + 1
    withdraw_id = base + 2
    db.transactions.create(txn_id=deposit_id, date="2026-06-01", account=acct, category=cat, amount=5000, memo="")
    db.transactions.create(txn_id=withdraw_id, date="2026-06-02", account=acct, category=cat, amount=-3000, memo="")
    code, out, err = cli_runner("txn", "amend", str(deposit_id), "29.99")
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    row = db.transactions.get(txn_id=deposit_id)
    assert row is not None
    assert row.amount == 5000
    assert sum(t.amount for t in db.transactions.list(account=acct)) == 2000
    code, out, err = cli_runner("txn", "amend", str(deposit_id), "30.00")
    print(out)
    print(err)
    assert code == 0
    row = db.transactions.get(txn_id=deposit_id)
    assert row is not None
    assert row.amount == 3000
    assert sum(t.amount for t in db.transactions.list(account=acct)) == 0
=== END AC balance-rule-amend ===

=== AC balance-rule-delete ===
Intent: txn delete rejects removing a deposit that later withdrawals depend on and keeps the row.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "ACPTBD1"
    cat = "ACPTBDC"
    db.accounts.create(account=acct, name="Delete Rule")
    db.categories.create(category=cat, description="Delete Rule Category")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    deposit_id = base + 1
    withdraw_id = base + 2
    db.transactions.create(txn_id=deposit_id, date="2026-06-01", account=acct, category=cat, amount=5000, memo="")
    db.transactions.create(txn_id=withdraw_id, date="2026-06-02", account=acct, category=cat, amount=-3000, memo="")
    before = len(db.transactions.list())
    code, out, err = cli_runner("txn", "delete", str(deposit_id))
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert db.transactions.get(txn_id=deposit_id) is not None
    assert len(db.transactions.list()) == before
    code, out, err = cli_runner("txn", "delete", str(withdraw_id))
    print(out)
    print(err)
    assert code == 0
    assert db.transactions.get(txn_id=withdraw_id) is None
=== END AC balance-rule-delete ===

=== AC balance-rule-transfer ===
Intent: transfer rejects an amount above the source balance and writes neither row.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    src = "ACPTBT1"
    dst = "ACPTBT2"
    cat = "ACPTBTC"
    db.accounts.create(account=src, name="Transfer Rule Source")
    db.accounts.create(account=dst, name="Transfer Rule Target")
    db.categories.create(category=cat, description="Transfer Rule Category")
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    tid = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=tid, date="2026-06-01", account=src, category=cat, amount=2500, memo="")
    before = len(db.transactions.list())
    code, out, err = cli_runner("transfer", src, dst, "25.01", "2026-06-02")
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert len(db.transactions.list()) == before
    assert db.transactions.list(account=dst) == []
=== END AC balance-rule-transfer ===

=== AC balance-rule-load ===
Intent: load transactions rejects a file whose rows leave a balance negative and stores none of its rows.

import csv
import os
import tempfile
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "ACPTBL1"
    cat = "ACPTBLC"
    db.accounts.create(account=acct, name="Load Rule")
    db.categories.create(category=cat, description="Load Rule Category")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    first_id = base + 1
    second_id = base + 2
    before = len(db.transactions.list())
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "rows.csv")
        with open(path, "w", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
            writer.writerow([first_id, "2026-06-01", acct, cat, "10.00", "deposit"])
            writer.writerow([second_id, "2026-06-02", acct, cat, "-10.01", "overdraw"])
        code, out, err = cli_runner("load", "transactions", path)
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert len(db.transactions.list()) == before
    assert db.transactions.get(txn_id=first_id) is None
    assert db.transactions.get(txn_id=second_id) is None
=== END AC balance-rule-load ===

## User Acceptance

- None.

## Guardrails

- Every check happens before the command's first write; a rejected command changes no table.
- Balances are computed from stored transactions in integer cents; no floating point is used.
- A rejected command writes nothing to standard output and one diagnostic line to standard error.
