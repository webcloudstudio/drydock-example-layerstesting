# FEATURE: Command Contract

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Assembly story verifying the CSV output contract and exit codes across every delivered ledger command. |
| Depends On | FEATURE-InitCount.md, FEATURE-LoadAccounts.md, FEATURE-LoadCategories.md, FEATURE-LoadTransactions.md, FEATURE-AccountAdd.md, FEATURE-AccountGet.md, FEATURE-AccountRename.md, FEATURE-AccountDelete.md, FEATURE-TxnPost.md, FEATURE-TxnGet.md, FEATURE-TxnAmend.md, FEATURE-TxnDelete.md, FEATURE-Transfer.md, FEATURE-ReportBalances.md, FEATURE-ReportCategories.md, FEATURE-ReportMonthly.md |
| Provides | — |
| Consumes | ledger init, ledger count, ledger load accounts, ledger load categories, ledger load transactions, ledger account add, ledger account get, ledger account rename, ledger account delete, ledger txn post, ledger txn get, ledger txn amend, ledger txn delete, ledger transfer, ledger report balances, ledger report categories, ledger report monthly |

## Purpose

Assembly and intent only. Verify across the delivered commands that:

- successful output is CSV with the specified headers, `\n` endings, two-decimal amounts, no quoting, and no trailing spaces;
- a failing command writes nothing to standard output and one diagnostic line to standard error;
- exit 2 results from unknown commands, tables, reports, and wrong argument counts;
- exit 1 results from an unreadable file, 3 from rejection, 4 from not found;
- every rejected writing command leaves the table counts unchanged.

Any seam defect is fixed in the owning module; this story adds no new behavior.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC contract-usage-errors ===
Intent: Unknown commands, unknown tables or reports, and wrong argument counts all exit 2 with empty standard output.

from cli.testing import cli_runner

cases = [
    ("frobnicate",),
    ("report", "nosuch"),
    ("report",),
    ("load", "nosuch", "x.csv"),
    ("account",),
    ("account", "get"),
    ("txn", "post", "A"),
    ("transfer", "A", "B"),
    ("count", "extra"),
]
for args in cases:
    code, out, err = cli_runner(*args)
    print(args, code, err)
    assert code == 2, args
    assert out == "", args
=== END AC contract-usage-errors ===

=== AC contract-csv-format ===
Intent: Successful commands emit the declared headers, newline-only endings, no trailing spaces, and amounts with exactly two decimals.

import csv
import io
import re
from cli.testing import cli_runner
from persistence.testing import db_session

def parse(out):
    return list(csv.reader(io.StringIO(out)))

def clean(out):
    assert out.endswith("\n")
    assert "\r" not in out
    for line in out.split("\n"):
        assert line == line.rstrip(" ")

acct = "ZZCF1"
cat = "ZZCFC"
with db_session() as db:
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Format Probe")
code, out, err = cli_runner("account", "add", acct, "Format Probe")
assert code == 0
clean(out)
assert parse(out)[0] == ["account", "name", "transactions", "balance"]

code, out, err = cli_runner("txn", "post", acct, cat, "7.5", "2099-05-05", "fmt")
print(out, err)
assert code == 0
clean(out)
table = parse(out)
assert table[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
assert re.fullmatch(r"-?\d+\.\d{2}", table[1][4])

code, out, err = cli_runner("count")
assert code == 0
clean(out)
table = parse(out)
assert table[0] == ["table", "rows"]
assert [r[0] for r in table[1:]] == ["accounts", "categories", "transactions"]

code, out, err = cli_runner("report", "balances")
assert code == 0
clean(out)
assert parse(out)[0] == ["account", "name", "transactions", "balance"]
code, out, err = cli_runner("report", "categories")
assert code == 0
clean(out)
assert parse(out)[0] == ["category", "description", "transactions", "inflow", "outflow", "net"]
code, out, err = cli_runner("report", "monthly")
assert code == 0
clean(out)
assert parse(out)[0] == ["month", "transactions", "inflow", "outflow", "net"]
=== END AC contract-csv-format ===

=== AC contract-failures-silent-stdout ===
Intent: Failing commands write nothing to standard output and exactly one diagnostic line to standard error, with the documented exit code for each failure class.

from cli.testing import cli_runner

cases = [
    (("account", "get", "ZZNOSUCH9"), 4),
    (("account", "add", "lower", "Bad Code"), 3),
    (("txn", "get", "999999999"), 4),
    (("txn", "post", "ZZNOSUCH9", "ZZNOCAT9", "1.00", "2099-01-01"), 3),
    (("load", "accounts", "/nonexistent-dir/zz-missing.csv"), 1),
]
for args, want in cases:
    code, out, err = cli_runner(*args)
    print(args, code, err)
    assert code == want, args
    assert out == "", args
    assert len(err.strip().splitlines()) == 1, args
=== END AC contract-failures-silent-stdout ===

=== AC contract-rejected-writes-change-nothing ===
Intent: Rejected writing commands exit 3 and leave the counts of all three tables unchanged.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

def counts():
    code, out, err = cli_runner("count")
    assert code == 0
    return {r[0]: int(r[1]) for r in list(csv.reader(io.StringIO(out)))[1:]}

acct = "ZZCR1"
other = "ZZCR2"
cat = "ZZCRC"
with db_session() as db:
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Reject Probe")
for a in (acct, other):
    code, out, err = cli_runner("account", "add", a, "Reject " + a)
    assert code == 0
code, out, err = cli_runner("txn", "post", acct, cat, "5.00", "2099-02-02", "seed")
assert code == 0

before = counts()
rejected = [
    ("account", "add", acct, "Duplicate"),
    ("account", "add", "bad code", "Name"),
    ("account", "delete", acct),
    ("txn", "post", acct, cat, "1.234", "2099-02-03"),
    ("txn", "post", acct, cat, "1.00", "2026-02-30"),
    ("txn", "post", acct, "ZZNOCAT9", "1.00", "2099-02-03"),
    ("txn", "post", acct, cat, "0", "2099-02-03"),
    ("transfer", acct, acct, "1.00", "2099-02-03"),
    ("transfer", acct, other, "0.50", "2099-02-30"),
]
for args in rejected:
    code, out, err = cli_runner(*args)
    print(args, code, err)
    assert code == 3, args
    assert out == "", args
assert counts() == before
=== END AC contract-rejected-writes-change-nothing ===

## User Acceptance

- None.

## Guardrails

- This story adds no new command behavior; defects are fixed in the owning module.
- Acceptance reads state by parsing CSV output and exit codes, never message wording.
