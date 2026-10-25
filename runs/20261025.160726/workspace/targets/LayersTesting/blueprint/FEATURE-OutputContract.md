# FEATURE: Output Contract

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Successful commands write unquoted CSV with LF endings, init writes nothing, and failures write nothing to standard output. |
| Depends On | FEATURE-CliEntry.md, FEATURE-AccountAdd.md, FEATURE-AccountGet.md, FEATURE-TxnPost.md, FEATURE-ReportBalances.md |
| Provides | output contract |
| Consumes | cli.main, ledger account add, ledger account get, ledger txn post, ledger report balances |

## Purpose

Fixes what each command may put on each stream so the grader's byte-for-byte comparison of
standard output is stable.

## Behavior

- Every successful command except `init` writes one header row then data rows, comma-separated,
  with no quoting, no trailing spaces, and `\n` line endings, ending with a final `\n`.
- `init` writes nothing to standard output.
- A failing command (exit `1`, `2`, `3`, or `4`) writes nothing to standard output and exactly one
  diagnostic line to standard error.
- Money is written with exactly two decimals, a leading `-` when negative, and no thousands
  separator.
- The account row is `account,name,transactions,balance`; the transaction row is
  `txn_id,date,account,category,amount,memo`.

## Database Interface

- None — persistence is owned by FEATURE-AccountAdd.md.

## Programmatic Acceptance

=== AC output-account-row-is-plain-csv ===
Intent: account add writes a header and one unquoted LF-terminated CSV row carrying the supplied values.

import csv
import io
from cli.testing import cli_runner

code_value = "OUTC1"
name_value = "Output Check"
code, out, err = cli_runner("account", "add", code_value, name_value)
print(out)
print(err)
assert code == 0
assert "\r" not in out
assert out.endswith("\n")
assert '"' not in out
rows = list(csv.reader(io.StringIO(out)))
assert len(rows) == 2
assert rows[0] == ["account", "name", "transactions", "balance"]
assert rows[1][0] == code_value
assert rows[1][1] == name_value
assert rows[1][2] == "0"
assert rows[1][3] == "0.00"
=== END AC output-account-row-is-plain-csv ===

=== AC output-init-writes-nothing ===
Intent: init succeeds with nothing on standard output.

from cli.testing import cli_runner

code, out, err = cli_runner("init")
print(err)
assert code == 0
assert out == ""
=== END AC output-init-writes-nothing ===

=== AC output-failures-keep-stdout-empty ===
Intent: A rejected, a not-found, and a usage failure each write nothing to stdout and one line to stderr.

from cli.testing import cli_runner

code_value = "OUTF1"
absent = "OUTF2"
name_value = "Failure Check"
code, out, err = cli_runner("account", "add", code_value, name_value)
assert code == 0

code, out, err = cli_runner("account", "add", code_value, name_value)
print(out, err)
assert code == 3
assert out == ""
assert len(err.strip().splitlines()) == 1

code, out, err = cli_runner("account", "get", absent)
print(out, err)
assert code == 4
assert out == ""
assert len(err.strip().splitlines()) == 1

code, out, err = cli_runner("frobnicate")
print(out, err)
assert code == 2
assert out == ""
assert len(err.strip().splitlines()) == 1
=== END AC output-failures-keep-stdout-empty ===

=== AC output-transaction-row-two-decimals ===
Intent: txn post prints the transaction row with the amount rendered from integer cents with two decimals.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "OUTT1"
cat = "OUTTC1"
cents = 1234
amount_text = f"{cents // 100}.{cents % 100:02d}"
day = "2026-06-01"
memo = "output row"
with db_session() as db:
    db.accounts.create(account=acct, name="Output Txn")
    db.categories.create(category=cat, description="Output Category")
    code, out, err = cli_runner("txn", "post", acct, cat, amount_text, day, memo)
    print(out)
    print(err)
    assert code == 0
    assert "\r" not in out
    rows = list(csv.reader(io.StringIO(out)))
    assert len(rows) == 2
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert rows[1][1:] == [day, acct, cat, amount_text, memo]
    stored = db.transactions.get(txn_id=int(rows[1][0]))
    assert stored is not None
    assert stored.amount == cents
=== END AC output-transaction-row-two-decimals ===

=== AC output-report-has-header-and-total ===
Intent: report balances prints a header, one row per created account with two-decimal balance, and a final TOTAL row.

import csv
import io
from cli.testing import cli_runner

code_value = "OUTR1"
name_value = "Report Check"
code, out, err = cli_runner("account", "add", code_value, name_value)
assert code == 0

code, out, err = cli_runner("report", "balances")
print(out)
print(err)
assert code == 0
assert "\r" not in out
assert out.endswith("\n")
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["account", "name", "transactions", "balance"]
assert rows[-1][0] == "TOTAL"
mine = [r for r in rows[1:-1] if r[0] == code_value]
assert len(mine) == 1
assert mine[0][1] == name_value
assert mine[0][2] == "0"
assert mine[0][3] == "0.00"
codes = [r[0] for r in rows[1:-1]]
assert codes == sorted(codes)
=== END AC output-report-has-header-and-total ===

## User Acceptance

- None.

## Guardrails

- Standard output never carries diagnostics.
- Output never uses quoting, thousands separators, or `\r\n` endings.
- Money is never formatted from a floating-point value.
