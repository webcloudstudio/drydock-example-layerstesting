# Build Instructions: A Cash Ledger

## Objective

Build a command-line cash ledger for a small shop. The shop keeps cash in a few places (drawers,
a safe, petty cash), records every receipt and payment against one of those places, and asks for
three reports: balances by account, totals by category, and totals by month.

The product is an executable named `ledger` at the application root. It stores everything in a
relational database through the shipped persistence library, and every command either completes
in full or changes nothing.

## Stack

Implement in Go 1.22 or newer over SQLite, through the shipped Go persistence package. Tests
run under `go test`. The contract below is the same for every language and database: the same
commands, the same output, and the same exit codes.

## Run Harness

`sources/run.sh` is the scoring entry point. It is supplied, not authored, and is staged verbatim
into the application root with the seed files. `drydock uat` runs `sh sources/run.sh` from the
completed application root and takes its exit code and output as the score.

The harness creates a fresh database, runs `./ledger init`, loads the seed files, and then runs a
fixed sequence of 43 checks. Each check compares one command's exit code and standard output
with a known answer. Standard error is never compared. The harness prints `PASS` or `FAIL` per
check and ends with:

```text
LayersTesting: NN passed, NN failed (of 43)
```

## Read-only scoring assets

These files are the exam. Do not modify, rewrite, regenerate, or substitute them:

- `sources/run.sh` — the scoring entry point and its known answers
- `sources/seed_accounts.csv` — 4 accounts
- `sources/seed_categories.csv` — 7 categories
- `sources/seed_transactions.csv` — 120 transactions, January to March 2026
- `sources/seed_transactions_bad.csv` — 11 transactions; row 11 names an unknown account

Application code never reads `sources/run.sh` and never embeds a report answer. Every report is
computed from the database.

## Database

`DATABASE_URL` names the database. A value beginning `postgres://` or `postgresql://` is a
PostgreSQL DSN. Any other value is a SQLite file path, optionally prefixed `sqlite://`. When
`DATABASE_URL` is unset, `DATABASE_PATH` is used, then `data/app.db`.

Three tables. Amounts are stored as integer cents and never as floating point.

| Table | Columns | Keys |
|---|---|---|
| `accounts` | `account` text, `name` text | primary key `account` |
| `categories` | `category` text, `description` text | primary key `category` |
| `transactions` | `txn_id` integer, `date` text `YYYY-MM-DD`, `account` text, `category` text, `amount` integer cents, `memo` text | primary key `txn_id`; `account` references `accounts`; `category` references `categories` |

All database access goes through the shipped persistence library and the relational layer
generated from `DATABASE.md`. Application code never opens a database driver directly.

## Rules

1. **Every command is one database transaction.** A command that fails for any reason leaves
   every table exactly as it was. A load that rejects row 11 stores none of rows 1 to 10. A
   transfer stores both of its rows or neither.
2. **No command leaves an account balance below zero.** An account's balance is the sum of its
   transaction amounts. Posting, amending, deleting, transferring, and loading are all subject to
   this rule, checked after the command's changes and before it commits.
3. **Codes** (`account`, `category`) are 1 to 12 characters from `A-Z` and `0-9`.
4. **Names and descriptions** are 1 to 40 characters. **Memos** are 0 to 60 characters. None of
   them contains a comma or a newline.
5. **Amounts** on input match `-?DIGITS[.D[D]]`: at most two decimal places, never zero. On output
   an amount is written with exactly two decimal places, a leading `-` when negative, and no
   thousands separator: `-12.50`, `0.00`, `5000.00`.
6. **Dates** are real calendar dates written `YYYY-MM-DD`. `2026-02-30` is rejected.
7. **Transaction ids.** A loaded transaction keeps the `txn_id` from its file. A posted
   transaction receives one more than the largest `txn_id` present, or `1` in an empty table. A
   transfer's outgoing row takes that id and its incoming row the next.

## Output

Every successful command except `init` writes CSV to standard output: one header row, then data
rows, comma-separated, no quoting, no trailing spaces, `\n` line endings. `init` writes nothing.
A failing command writes nothing to standard output and one diagnostic line to standard error.

The account row is `account,name,transactions,balance`, where `transactions` counts the account's
transactions. The transaction row is `txn_id,date,account,category,amount,memo`.

## Commands

| Command | Output on success |
|---|---|
| `ledger init` | Drops all three tables if present and creates them empty. Nothing written. |
| `ledger count` | `table,rows`, then `accounts`, `categories`, `transactions` rows in that order. |
| `ledger load <table> <csv>` | Loads `accounts`, `categories`, or `transactions` from a file whose header matches the table's columns in the order above. Writes `table,loaded` and `<table>,<rows>`. |
| `ledger account add <code> <name>` | The new account row. |
| `ledger account get <code>` | The account row. |
| `ledger account rename <code> <name>` | The updated account row. |
| `ledger account delete <code>` | `deleted` and the code. Refused while the account has transactions. |
| `ledger txn post <account> <category> <amount> <date> [<memo>]` | The new transaction row. |
| `ledger txn get <id>` | The transaction row. |
| `ledger txn amend <id> <amount>` | The updated transaction row. Only the amount changes. |
| `ledger txn delete <id>` | `deleted` and the id. |
| `ledger transfer <from> <to> <amount> <date>` | Two transaction rows in category `TRANSFER`: `-amount` on `<from>` with memo `transfer to <to>`, then `+amount` on `<to>` with memo `transfer from <from>`. The amount is positive and the accounts differ. |
| `ledger report balances` | `account,name,transactions,balance` per account ordered by code, then `TOTAL,,<count>,<sum>`. |
| `ledger report categories` | `category,description,transactions,inflow,outflow,net` per category ordered by code, including categories with no transactions, then `TOTAL,,<count>,<inflow>,<outflow>,<net>`. |
| `ledger report monthly` | `month,transactions,inflow,outflow,net` per `YYYY-MM` that has transactions, ascending, then `TOTAL,<count>,<inflow>,<outflow>,<net>`. |

`inflow` is the sum of positive amounts. `outflow` is the sum of the absolute values of negative
amounts, written as a positive number. `net` is `inflow - outflow`.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success. |
| `1` | Operational failure: database unreachable, tables missing, file unreadable. |
| `2` | Usage error: unknown command, unknown table or report, wrong argument count. |
| `3` | Rejected: invalid code, name, amount, date, or file row; duplicate key; unknown account or category; account in use; any change that would leave a negative balance. |
| `4` | Not found: `account get/rename/delete` of an absent account, `txn get/amend/delete` of an absent id. |

## Tests

The completed application provides a POSIX-compatible `bin/test.sh` that runs its own automated
test suite from the application root and exits zero only when every test passes. The suite
covers each command, each exit code, and each rule above against a real temporary database.
