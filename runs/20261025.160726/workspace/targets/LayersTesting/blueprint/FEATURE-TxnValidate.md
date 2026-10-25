# FEATURE: Txn Validate

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Specifies the input validation `ledger txn post` applies to category, amount, and date before it writes anything. |
| Depends On | FEATURE-TxnPost.md, FEATURE-LedgerCore.md, DATABASE.md |
| Provides | txn post validation |
| Consumes | ledger txn post, parse_amount, validate_date |

## Purpose

Guarantee that an invalid category, amount, or date given to `ledger txn post` is rejected with exit 3 before the first write, and that valid boundary inputs are accepted. Wiring lives in the post command; this specification owns the rules and their proof.

## Rules

| Input | Valid | Rejected with exit 3 |
|-------|-------|----------------------|
| Category | A code present in `categories` | An unknown category |
| Amount | `-?DIGITS[.D[D]]`, never zero, so `12`, `12.5`, `-12.50` | More than two decimals (`1.234`), `12.`, a leading `+`, non-numeric text, empty text, `0`, `0.00`, `-0.00` |
| Date | A real calendar date written `YYYY-MM-DD`, including a leap day in a leap year | `2026-02-30`, `2026-02-29`, `2026-2-3`, non-date text |

A rejected post writes no row, prints nothing to standard output, writes one diagnostic line to standard error, and consumes no transaction id: the next successful post receives one more than the largest id present.

## Database Interface

- `FEATURE-CATEGORY-001` — read: look up the category named on input - supplies: `category` - returns: `category`, `description`
- `FEATURE-ACCOUNT-002` — read: confirm the account exists - supplies: `account` - returns: `account`, `name`

## Programmatic Acceptance

=== AC txnvalidate-unknown-category ===
Intent: An unknown category exits 3 and writes no row.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TVACCT1"
    db.accounts.create(account=acct, name="Validate Account")
    before = len(db.transactions.list())
    code, out, err = cli_runner("txn", "post", acct, "NOSUCHCAT", "1.00", "2026-04-01")
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txnvalidate-unknown-category ===

=== AC txnvalidate-bad-amounts ===
Intent: Over-precise, malformed, and zero amounts exit 3 and write no row.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TVACCT2"
    cat = "TVCAT2"
    db.accounts.create(account=acct, name="Validate Amount")
    db.categories.create(category=cat, description="Validate Amount Category")
    before = len(db.transactions.list())
    for bad in ("1.234", "abc", "12.", "+5.00", "--1", "", "0", "0.00", "-0.00"):
        code, out, err = cli_runner("txn", "post", acct, cat, bad, "2026-04-01")
        print(repr(bad), code, out, err)
        assert code == 3
        assert out == ""
        assert len(db.transactions.list()) == before
=== END AC txnvalidate-bad-amounts ===

=== AC txnvalidate-bad-dates ===
Intent: Impossible and malformed dates exit 3 and write no row.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TVACCT3"
    cat = "TVCAT3"
    db.accounts.create(account=acct, name="Validate Date")
    db.categories.create(category=cat, description="Validate Date Category")
    before = len(db.transactions.list())
    for bad in ("2026-02-30", "2026-02-29", "2026-13-01", "2026-2-3", "notadate"):
        code, out, err = cli_runner("txn", "post", acct, cat, "1.00", bad)
        print(repr(bad), code, out, err)
        assert code == 3
        assert out == ""
        assert len(db.transactions.list()) == before
=== END AC txnvalidate-bad-dates ===

=== AC txnvalidate-valid-boundaries ===
Intent: A one-decimal amount and a leap-day date are accepted and stored as integer cents.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TVACCT4"
    cat = "TVCAT4"
    leap_day = "2028-02-29"
    db.accounts.create(account=acct, name="Validate Valid")
    db.categories.create(category=cat, description="Validate Valid Category")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    code, out, err = cli_runner("txn", "post", acct, cat, "12.5", leap_day)
    print(out)
    print(err)
    assert code == 0
    stored = db.transactions.get(txn_id=base + 1)
    assert stored is not None
    assert stored.amount == 1250
    assert stored.date == leap_day
=== END AC txnvalidate-valid-boundaries ===

=== AC txnvalidate-no-id-gap ===
Intent: A rejected post consumes no id, so the next successful post receives the next id.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TVACCT5"
    cat = "TVCAT5"
    db.accounts.create(account=acct, name="Validate Gap")
    db.categories.create(category=cat, description="Validate Gap Category")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    code, out, err = cli_runner("txn", "post", acct, cat, "1.234", "2026-04-01")
    assert code == 3
    code, out, err = cli_runner("txn", "post", acct, cat, "1.00", "2026-04-01")
    print(out)
    print(err)
    assert code == 0
    assert db.transactions.get(txn_id=base + 1) is not None
    assert db.transactions.get(txn_id=base + 2) is None
=== END AC txnvalidate-no-id-gap ===

## User Acceptance

- None.

## Guardrails

- Every check completes before the first write; a rejected post changes no table.
- Amounts are parsed to integer cents; no floating point at any layer.
- Rejections use exit 3, never exit 1 or 2.
