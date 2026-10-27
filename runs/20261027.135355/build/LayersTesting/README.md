# drydock Layers Testing Uat Case

Drydock uat - LayersTesting exercises the language and persistence layers. The source is an original brief for a command-line cash ledger with three tables (accounts, categories, transactions) reached only through the shipped persistence library. The supplied grader, sources/run.sh, initializes a fresh database, loads 131 known rows, and runs 43 checks of exit code and output: row counts, three reports with known totals, create/read/update/delete on accounts and transactions, atomic rejected loads and transfers, the non-negative balance rule, and a final ledger reset. This build is in Python over SQLite. Run with drydock uat LayersTesting. Source Repo: none, the brief is original to this kit.

## Intent

Build a command-line cash ledger, an executable named `ledger` at the application root, as
described in `sources/INSTRUCTIONS.md`. It keeps accounts, categories, and cash transactions in a
relational database reached only through the shipped persistence library, rejects a failing command
before it writes, enforces non-negative balances, and reports balances, category totals, and monthly totals.

Correctness is measured by `sources/run.sh`: 43 checks of exit code and standard output against
known answers computed from the seed files. The goal is every check passing.

## What It Does

Create one account and print its row. The module `ledger_core.accounts` also exports the helper the
other account commands use to build an account row from live data.

`ledger account delete <code>` removes an account and prints `deleted` then the code, one per line. An account that still has transactions is refused.

`ledger account get <code>` prints the account's header row and data row `account,name,transactions,balance`. The transaction count and balance are computed from the account's stored transactions using the `account_row` helper exported by `ledger_core.accounts`. The balance is the sum of integer cents, formatted with exactly two decimals.

`ledger account rename <code> <name>` validates the new name, updates only the name column, and prints the header row and the updated account row `account,name,transactions,balance`.

An account's balance is the sum of its transaction amounts in integer cents. Load, post, amend, delete, and transfer call this module before their first write. It only reads and never writes.

Provide the single entry point through which every command runs. It resolves the command words, checks the argument count, opens the database, calls the handler, and turns the result into CSV on stdout or one diagnostic line on stderr with the contract exit code.

Assembly and intent only. Verify across the delivered commands that:

- successful output is CSV with the specified headers, `\n` endings, two-decimal amounts, no quoting, and no trailing spaces;
- a failing command writes nothing to standard output and one diagnostic line to standard error;
- exit 2 results from unknown commands, tables, reports, and wrong argument counts;
- exit 1 results from an unreadable file, 3 from rejection, 4 from not found;
- every rejected writing command leaves the table counts unchanged.

Any seam defect is fixed in the owning module; this story adds no new behavior.

`init` prepares an empty ledger for loading and use. `count` reports how many rows each table holds. Both are registered in `cli/commands/maintenance.py` through its `COMMANDS` mapping, with keys `("init",)` and `("count",)`, each taking no arguments.

Load accounts from a CSV file whose header is `account,name`. Every row is validated before the
first write; the rows are then written together or not at all.

Load categories from a CSV file whose header is `category,description`, applying the same
validate-everything-then-write rule as the accounts load.

The three `ledger load <table> <csv>` commands share one reader so that file handling, header
checking, and the exit codes for unreadable files and malformed rows are identical. The reader
only reads: it never touches the database and never writes.

Load transactions from a CSV file whose header is `txn_id,date,account,category,amount,memo`.
Each row keeps the `txn_id` from the file. The file is accepted entirely or not at all.

Assembly and intent only. An account's balance is the sum of its transaction amounts and must never
be below zero. For each of load, post, amend, delete, and transfer, a case that would leave a
balance below zero exits 3 and leaves balances and row counts unchanged. A load file whose later
rows make an earlier-valid balance negative is rejected whole.

Report each account's transaction count and balance. Every value is computed from queries over stored rows; none is embedded. Persistence is reached only through the generated `persistence` package via `ledger_core`.

Report totals by category, including categories with no transactions. Every value is computed from queries over stored rows. Persistence is reached only through the generated `persistence` package via `ledger_core`.

Give the shop a report of cash movement by calendar month. Every value is computed from the
database at call time; no total is embedded.

Move cash between two accounts as two transaction rows that are stored together or not at all. Persistence is reached only through `ledger_core.transactions`, which calls the generated `persistence` package.

Amend the amount of an existing transaction. Only the amount changes; date, account, category, and memo are untouched. Persistence is reached only through `ledger_core.transactions`, which calls the generated `persistence` package.

Delete one transaction by id. Persistence is reached only through `ledger_core.transactions`, which calls the generated `persistence` package.

`ledger txn get <id>` prints the header row `txn_id,date,account,category,amount,memo` and the stored transaction, formatted with `txn_row` from `ledger_core.transactions`, with the amount shown in two decimals.

`ledger txn post <account> <category> <amount> <date> [<memo>]` records one transaction and prints the header row `txn_id,date,account,category,amount,memo` followed by the new row. `ledger_core.transactions` exports `txn_row` (formats a stored transaction as an output row) and `next_txn_id` (largest stored `txn_id` plus one, or 1 in an empty table), used by the other transaction commands and by transfer.

Every command validates its inputs with these functions before it writes. They touch no storage and print nothing. Every violation raises `ledger_core.errors.Rejected` (exit code 3).

Terminal story. After every other story has closed, run `sh sources/run.sh` and `sh bin/test.sh`,
each of which must exit zero. Nothing under `sources/` is modified. Failures are fixed in the
owning module, never by editing the grader or its seed files.

The grader creates its own temporary SQLite database and runs `ledger init`, which empties the
database. The criterion therefore removes `DATABASE_URL` and `DATABASE_PATH` from the otherwise
inherited environment so the managed store is never touched by a child process.

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
