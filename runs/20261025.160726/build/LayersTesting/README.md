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

Add a new place where the shop keeps cash. A new account has no transactions and a zero balance.

Delete an account. An account that still has transactions is refused so that no transaction is orphaned.

An account code is a primary key. Adding an existing code is a rejected command: it exits 3, writes
nothing to stdout, and neither the existing row nor any other row changes.

Read one account by code and print it as CSV. The transaction count and balance are computed from the
database on every call and are never stored.

Rename an existing account. Only the name changes; the code, transactions, and balance are untouched.

An account's balance is the sum of its transaction amounts in integer cents. No command may leave
any account balance below zero. This assembly story confirms that every mutating command applies the
shared projected-balance guard from the ledger core before its first write, and wires the guard into
any command that lacks it. A rejection exits `3`, prints nothing to standard output, and leaves every
table unchanged.

Every command in the ledger plugs into one dispatcher. This story builds the dispatcher and registers no command. Later stories add modules under `cli/commands/` that call `register`. `main` imports every module in the `cli.commands` package (for example with `pkgutil.iter_modules`) before dispatching, so adding a command never edits `main`.

`ledger count` prints the number of rows in `accounts`, `categories`, and `transactions`, in that order.

Output is CSV: the header `table,rows`, then one row per table. The counts are read from the database on every call. `count` takes no arguments; the surfaced criterion that `count` with arguments beyond `count` is a usage error means any extra argument exits 2 with nothing on standard output. Tables missing from the database exit 1.

The registration is `register(("count",), handler, (0, 0))` in `cli/commands/count.py`. The handler computes each count as the length of the table's `list` result.

Every command opens the store through the shipped persistence library using one DSN chosen by a
single pure resolver. No driver is opened anywhere else and amounts stay integer cents.

`ledger init` drops all three tables if present and recreates them empty, writing nothing to standard output. It takes no arguments; any argument is a usage error (exit 2) and changes nothing. This is the contract surfaced in the commands table of the source instructions.

Every command shares the same input rules. They live in `cli/core.py` so that no command repeats or contradicts them. All validators raise `cli.errors.Rejected` (exit 3) and perform no database write.

Bulk-load account rows from a CSV file so the shop's drawers, safe, and petty cash exist before
transactions are loaded. The command either stores every row or stores nothing.

Bulk-load category rows so transactions can be classified. The command either stores every row or
stores nothing.

Prove and enforce the all-or-nothing rule for loads: a file with one invalid row stores none of
its rows. A file of ten valid rows followed by an eleventh naming an unknown account stores none
of the eleven.

Bulk-load transaction rows. Each loaded transaction keeps the `txn_id` written in its file. The
command either stores every row or stores nothing.

Fixes what each command may put on each stream so the grader's byte-for-byte comparison of
standard output is stable.

`ledger report balances` prints one row per account with its transaction count and balance, ordered
by account code, followed by a TOTAL row. Every value is computed from the database at run time;
nothing is stored or hard-coded.

`ledger report categories` prints, for every category ordered by code, how many transactions it has
and its inflow, outflow, and net, followed by a TOTAL row. Categories without transactions are
included. Every value is computed from the database at run time.

`ledger report monthly` prints one row per `YYYY-MM` that has at least one transaction, in ascending
order, with that month's transaction count, inflow, outflow, and net, followed by a TOTAL row. Every
value is computed from the database at run time.

`bin/test.sh` is the project's own regression gate. It runs from the application root, activates
the `.venv` environment, and runs `pytest -q`, propagating pytest's exit status.

Move cash between two accounts as a pair of transactions in category `TRANSFER`. Both rows are stored or neither is.

`ledger transfer <from> <to> <amount> <date>` must never leave the source account below zero. This
story proves that the projected balance of the source, computed from its stored transactions minus
the transfer amount, is checked before the first write. A rejected transfer exits `3`, writes nothing
to standard output, and leaves the transactions table exactly as it was. A transfer that brings the
source to exactly zero is allowed.

Correct the amount of an existing transaction. Date, account, category, and memo never change. The change is rejected before any write if it would leave the owning account's balance below zero.

Remove an existing transaction. The delete is rejected before any write if removing the row would leave the owning account's balance below zero.

Read a single transaction by id and print it in the transaction CSV shape. The command never writes.

Post a single transaction. Every input and the non-negative balance rule are checked before the first
write, so a rejected post changes nothing.

Guarantee that an invalid category, amount, or date given to `ledger txn post` is rejected with exit 3 before the first write, and that valid boundary inputs are accepted. Wiring lives in the post command; this specification owns the rules and their proof.

`ledger` distinguishes a malformed invocation (exit `2`) from a rejected one (exit `3`). A usage
error is detected from the argument vector alone, before the database is opened and before any
file is read, so it can never touch the store.

## Stack

Python

## Setup and Running

**Before first run:**

- Copy `.env.example` to `.env` and fill in local values before starting.
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
