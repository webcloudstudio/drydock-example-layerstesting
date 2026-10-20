# drydock Layers Testing Uat Case

Drydock uat - LayersTesting exercises the language and persistence layers. The source is an original brief for a command-line cash ledger with three tables (accounts, categories, transactions) reached only through the shipped persistence library. The supplied grader, sources/run.sh, initializes a fresh database, loads 131 known rows, and runs 43 checks of exit code and output: row counts, three reports with known totals, create/read/update/delete on accounts and transactions, atomic rejected loads and transfers, the non-negative balance rule, and a final drop and recreate. This build is in Python over SQLite. Run with drydock uat LayersTesting. Source Repo: none, the brief is original to this kit.

## Intent

Build a command-line cash ledger, an executable named `ledger` at the application root, as
described in `sources/INSTRUCTIONS.md`. It keeps accounts, categories, and cash transactions in a
relational database reached only through the shipped persistence library, rejects a failing command
before it writes, enforces non-negative balances, and reports balances, category totals, and monthly totals.

Correctness is measured by `sources/run.sh`: 43 checks of exit code and standard output against
known answers computed from the seed files. The goal is every check passing.

## What It Does

`ledger load accounts <csv>` and `ledger load categories <csv>` import validated master data. Files must be readable, have the exact table header, contain valid codes and text, and contain no duplicate keys. Validation completes before any row is written.

Manage account master records while reporting transaction counts and integer-cent balances.

Every posting, amendment, deletion, transfer, and transaction load computes the affected account balances before writing. Any negative result rejects the complete command with no table changes.

The supplied harness is the authoritative final verification for the executable ledger. It exercises schema lifecycle, loading, reports, account and transaction mutations, transfers, rejection atomicity, usage errors, and re-initialization without modifying the supplied harness or fixtures.

Provide a POSIX-compatible `bin/test.sh` that runs the complete pytest suite from the application root and returns success only when every project test passes.

The balances report lists every account ordered by account code, with its transaction count and integer-cent balance, followed by a computed total row.

The category report includes every category, including categories without transactions, and reports transaction count, inflow, outflow, and net totals.

The monthly report groups transactions by their `YYYY-MM` calendar month, orders months ascending, and appends a computed total row.

`ledger load transactions <csv>` validates every transaction before writing any row, including headers, fields, references, duplicate identifiers, dates, amounts, and prospective account balances.

Manage transaction rows with generated identifiers, exact cent formatting, validated dates and amounts, and atomic balance checks.

A transfer moves a positive amount from one existing account to another by creating two consecutive transactions in category `TRANSFER`.

## Stack

Python

## Setup and Running

**Before first run:**

- Confirm the repository has the expected remote with `git remote -v`; add `origin` if the startup guard requires it.
- Run `git status --short` and commit or intentionally stash local changes before deployment-oriented runs.

**Install dependencies:**

```bash
uv sync
```

## Verification

```bash
bash bin/test.sh
```

## Next Steps

- Complete the first-run checks above.
- Run `bash bin/test.sh` before making release or deployment changes.
