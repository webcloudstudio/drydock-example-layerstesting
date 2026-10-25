# FEATURE: Transfer Overdraw Rejection

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | A transfer larger than the source account balance is rejected with exit 3 and writes neither row. |
| Depends On | FEATURE-Transfer.md, FEATURE-LoadTransactions.md, FEATURE-LedgerCore.md, DATABASE.md |
| Provides | transfer overdraw rejection |

## Purpose

`ledger transfer <from> <to> <amount> <date>` must never leave the source account below zero. This
story proves that the projected balance of the source, computed from its stored transactions minus
the transfer amount, is checked before the first write. A rejected transfer exits `3`, writes nothing
to standard output, and leaves the transactions table exactly as it was. A transfer that brings the
source to exactly zero is allowed.

## Behavior

- The source balance is the sum, in integer cents, of the source account's transactions, read from
  the database at command time.
- If the balance minus the transfer amount is below zero, the command exits `3` before writing either
  the outgoing or the incoming row.
- If the source has no transactions its balance is zero and any positive transfer is rejected.
- A transfer equal to the whole balance succeeds and leaves the source at zero.
- No floating point is used at any step.

## Database Interface

- `FEATURE-TXN-002` — read: list the source account's transactions to compute its balance - supplies: `account` - returns: `account`, `amount`

## Programmatic Acceptance

=== AC transfer-overdraw-rejected ===
Intent: A transfer exceeding the source balance exits 3, prints nothing, and writes no rows.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    src = "ACPTOD1"
    dst = "ACPTOD2"
    cat = "ACPTODC"
    db.accounts.create(account=src, name="Overdraw Source")
    db.accounts.create(account=dst, name="Overdraw Target")
    db.categories.create(category=cat, description="Overdraw Funding")
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    tid = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=tid, date="2026-06-01", account=src, category=cat, amount=10000, memo="")
    before = len(db.transactions.list())
    code, out, err = cli_runner("transfer", src, dst, "100.01", "2026-06-02")
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    after = len(db.transactions.list())
    assert after == before
    assert db.transactions.list(account=dst) == []
    assert sum(t.amount for t in db.transactions.list(account=src)) == 10000
=== END AC transfer-overdraw-rejected ===

=== AC transfer-overdraw-exact-balance ===
Intent: A transfer equal to the whole source balance succeeds and leaves the source at zero.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    src = "ACPTOE1"
    dst = "ACPTOE2"
    cat = "ACPTOEC"
    db.accounts.create(account=src, name="Exact Source")
    db.accounts.create(account=dst, name="Exact Target")
    db.categories.create(category=cat, description="Exact Funding")
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    tid = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=tid, date="2026-06-01", account=src, category=cat, amount=10000, memo="")
    before = len(db.transactions.list())
    code, out, err = cli_runner("transfer", src, dst, "100.00", "2026-06-02")
    print(out)
    print(err)
    assert code == 0
    assert len(db.transactions.list()) == before + 2
    assert sum(t.amount for t in db.transactions.list(account=src)) == 0
    assert sum(t.amount for t in db.transactions.list(account=dst)) == 10000
=== END AC transfer-overdraw-exact-balance ===

=== AC transfer-overdraw-empty-source ===
Intent: A source account with no transactions cannot be the source of any positive transfer.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    src = "ACPTOM1"
    dst = "ACPTOM2"
    db.accounts.create(account=src, name="Empty Source")
    db.accounts.create(account=dst, name="Empty Target")
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    before = len(db.transactions.list())
    code, out, err = cli_runner("transfer", src, dst, "0.01", "2026-06-02")
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert len(db.transactions.list()) == before
    assert db.transactions.list(account=src) == []
    assert db.transactions.list(account=dst) == []
=== END AC transfer-overdraw-empty-source ===

## User Acceptance

- None.

## Guardrails

- A rejected transfer writes neither the outgoing nor the incoming row.
- The balance check runs before the first write and uses integer cents only.
- A rejected command writes nothing to standard output and one diagnostic line to standard error.
