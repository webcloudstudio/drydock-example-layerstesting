# Scorecard: LayersTesting

## Specification

> **NOT YET RUN**
> drydock score spec LayersTesting

## Acceptance

> **PASSED**
> drydock score ac LayersTesting · 2026-10-25T17:04:35.470+00:00

PASS 126   FAIL 0   UNVERIFIED 0   PREPASSED 34   (160 AC total)

## Build

> **RECORDED**
> drydock score build LayersTesting

Blocks: 7   Repaired: 1   Failed: 0
Tokens: 7,020,857 (cached 6,858,283, output 162,386)   Cache hit rate: 100.0%

## Release

> **FAILED**
> drydock score release LayersTesting · 2026-10-25T17:07:01.349+00:00

- Verdict: FAILED

LayersTesting: FAILED — 8 of 9

  st-001  MET       ["sh", "sources/run.sh"] exited 0; governed_gate full: return_code 0, stdout 'LayersTesting: 43 passed, 0 failed (of 43)'
  st-002  MET       bin/test.sh:1-35 is a POSIX sh script (`set -eu`, `$(...)`, `.` to source the venv) that runs `pytest -q` and exits with its status; observed: `sh bin/test.sh` exit 0; '348 passed in 13.26s'
  st-003  NOT MET   probe: after `ALTER TABLE accounts ADD COLUMN probe_marker`, `ledger init` exited 0 and PRAGMA table_info(accounts) still listed ['account', 'name', 'probe_marker']; probe: `ledger count` after init returned accounts,0 / categories,0 / transactions,0; cli/commands/init.py:16-18 calls db.transactions.clear, db.accounts.clear, db.categories.clear; no DROP appears anywhere in the source; cli/commands/init.py:21-28 runs the schema script only when a list() call raises, so existing tables are kept
  st-004  MET       governed_gate stdout: 'PASS B1: ledger load accounts …', 'PASS B2: ledger load categories …', 'PASS B3: ledger load transactions …'; governed_gate stdout: 'PASS B4: ledger count' compared against accounts,4 / categories,7 / transactions,120
  st-005  MET       governed_gate stdout: PASS C1, C2, C3 (initial reports) and PASS H1, H2, H3 (post-change reports); sources/run.sh:check() compares stdout with `cmp -s` against the expected text, so a PASS means byte equality
  st-006  MET       governed_gate stdout: PASS E1–E8 (add, duplicate add, get, rename, get NOSUCH, delete with transactions, delete, get after delete); governed_gate stdout: PASS F1–F10 (post, get, amend, get 999, post rejections, delete, get after delete, post negative); run.sh expects exit 4 for E5, E8, F4, F9, and the gate passed those checks
  st-007  MET       probe: load transactions (bad file) rc=3 unchanged=True, stderr 'unknown account NOSUCH'; probe: load accounts (duplicate) rc=3 unchanged=True; probe: txn post overdraw rc=3 unchanged=True; txn amend overdraw rc=3 unchanged=True; txn delete overdraw rc=3 unchanged=True; probe: transfer overdraw rc=3 unchanged=True; account add duplicate rc=3 unchanged=True; account delete with transactions rc=3 unchanged=True; probe control: a valid txn post returned rc=0 and changed the snapshot, so the snapshot does detect change
  st-008  MET       cli/core.py:84 balance_guard raises Rejected when the resulting balance is below zero; cli/commands/load.py:74, transfer.py:27, txn.py:23, txn.py:48, txn.py:61 call balance_guard on every write path; probe: 'account PETTY would be -693.75; balance may not go negative' (post), SAFE -4749.00 (amend), SAFE -4750.00 (delete), SAFE -749.99 (transfer), each rc=3; governed_gate stdout: PASS G2–G5 (transfer, post, amend, delete all rejected with exit 3)
  st-009  MET       cli/context.py:19 `return open_database(dsn)` is the only place cli opens a store; a grep of cli/ and tests/ finds no sqlite3, psycopg, cursor, or execute calls; persistence/db.py:580-598 open_driver selects PostgresDriver or SqliteDriver from the DSN scheme; cli/core.py:21-31 parse_amount returns int cents, and cli/core.py:84 applies the guard in cents; schema.sql:4 declares "amount" INTEGER NOT NULL; git status is clean, so persistence/ matches the shipped commit

## Project acceptance

| ID | Type | Criterion | Verdict | Observed |
|---|---|---|---|---|
| st-001 | technical | The completed ledger shall make sh sources/run.sh exit zero; that script's exit status is the sole acceptance verdict. | MET | ["sh", "sources/run.sh"] exited 0; governed_gate full: return_code 0, stdout 'LayersTesting: 43 passed, 0 failed (of 43)' |
| st-002 | technical | The application shall provide a POSIX-compatible bin/test.sh that exits zero when every automated test passes. | MET | bin/test.sh:1-35 is a POSIX sh script (`set -eu`, `$(...)`, `.` to source the venv) that runs `pytest -q` and exits with its status; observed: `sh bin/test.sh` exit 0; '348 passed in 13.26s' |
| st-003 | behavioral | When ledger init runs, the application shall drop and recreate the accounts, categories, and transactions tables so that ledger count reports zero rows in each. | NOT MET | probe: after `ALTER TABLE accounts ADD COLUMN probe_marker`, `ledger init` exited 0 and PRAGMA table_info(accounts) still listed ['account', 'name', 'probe_marker']; probe: `ledger count` after init returned accounts,0 / categories,0 / transactions,0; cli/commands/init.py:16-18 calls db.transactions.clear, db.accounts.clear, db.categories.clear; no DROP appears anywhere in the source; cli/commands/init.py:21-28 runs the schema script only when a list() call raises, so existing tables are kept |
| st-004 | behavioral | When the three seed files are loaded into an initialized database, the application shall report 4 accounts, 7 categories, and 120 transactions. | MET | governed_gate stdout: 'PASS B1: ledger load accounts …', 'PASS B2: ledger load categories …', 'PASS B3: ledger load transactions …'; governed_gate stdout: 'PASS B4: ledger count' compared against accounts,4 / categories,7 / transactions,120 |
| st-005 | behavioral | The application shall compute the balances, categories, and monthly reports from the database, matching the known answers in sources/run.sh byte for byte. | MET | governed_gate stdout: PASS C1, C2, C3 (initial reports) and PASS H1, H2, H3 (post-change reports); sources/run.sh:check() compares stdout with `cmp -s` against the expected text, so a PASS means byte equality |
| st-006 | behavioral | The application shall add, get, rename, and delete accounts and post, get, amend, and delete transactions, reporting an absent record with exit code 4. | MET | governed_gate stdout: PASS E1–E8 (add, duplicate add, get, rename, get NOSUCH, delete with transactions, delete, get after delete); governed_gate stdout: PASS F1–F10 (post, get, amend, get 999, post rejections, delete, get after delete, post negative); run.sh expects exit 4 for E5, E8, F4, F9, and the gate passed those checks |
| st-007 | behavioral | If a load, post, amend, delete, or transfer is rejected, then the application shall exit 3 and leave every table exactly as it was. | MET | probe: load transactions (bad file) rc=3 unchanged=True, stderr 'unknown account NOSUCH'; probe: load accounts (duplicate) rc=3 unchanged=True; probe: txn post overdraw rc=3 unchanged=True; txn amend overdraw rc=3 unchanged=True; txn delete overdraw rc=3 unchanged=True; probe: transfer overdraw rc=3 unchanged=True; account add duplicate rc=3 unchanged=True; account delete with transactions rc=3 unchanged=True; probe control: a valid txn post returned rc=0 and changed the snapshot, so the snapshot does detect change |
| st-008 | behavioral | If a command would leave any account balance below zero, then the application shall reject it with exit code 3. | MET | cli/core.py:84 balance_guard raises Rejected when the resulting balance is below zero; cli/commands/load.py:74, transfer.py:27, txn.py:23, txn.py:48, txn.py:61 call balance_guard on every write path; probe: 'account PETTY would be -693.75; balance may not go negative' (post), SAFE -4749.00 (amend), SAFE -4750.00 (delete), SAFE -749.99 (transfer), each rc=3; governed_gate stdout: PASS G2–G5 (transfer, post, amend, delete all rejected with exit 3) |
| st-009 | technical | The application shall reach the database only through the shipped persistence library, selected by DATABASE_URL, with amounts stored as integer cents. | MET | cli/context.py:19 `return open_database(dsn)` is the only place cli opens a store; a grep of cli/ and tests/ finds no sqlite3, psycopg, cursor, or execute calls; persistence/db.py:580-598 open_driver selects PostgresDriver or SqliteDriver from the DSN scheme; cli/core.py:21-31 parse_amount returns int cents, and cli/core.py:84 applies the guard in cents; schema.sql:4 declares "amount" INTEGER NOT NULL; git status is clean, so persistence/ matches the shipped commit |

**Failures:**
- st-003 is NOT MET: When ledger init runs, the application shall drop and recreate the accounts, categories, and transactions tables so that ledger count reports zero rows in each.

**Ranked improvements:**
1. Resolve st-003 (NOT MET): When ledger init runs, the application shall drop and recreate the accounts, categories, and transactions tables so that ledger count reports zero rows in each.
2. Resolve st-003 one way or the other. Either change `ledger init` to drop and recreate the three tables as the criterion says, or reword st-003 to 'empties the three tables and leaves the schema in place', which matches cli/commands/init.py:16-18 and the observed behavior.
3. Have the grader compare the full contents of accounts, categories, and transactions after each rejected command, not just row counts. Today st-007 is supported by the D-section counts and the H-section reports, while a snapshot check would be direct.
4. Give st-004 through st-008 a command or a named probe so they are not inferred from a single grader run.

**Material decisions:**

- Two resolvers, one default each — 
- Init empties tables rather than dropping them — 
- All-or-nothing writes — 
- All-or-nothing writes — 
- All-or-nothing writes — 
- Two-row atomicity — 
