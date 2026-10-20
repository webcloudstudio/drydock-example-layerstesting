# Scorecard: LayersTesting

## Specification

> **NOT YET RUN**
> drydock score spec LayersTesting

## Acceptance

> **PASSED**
> drydock score ac LayersTesting · 2026-10-20T19:58:16.366+00:00

PASS 21   FAIL 0   UNVERIFIED 0   PREPASSED 21   (42 AC total)

## Build

> **RECORDED**
> drydock score build LayersTesting

Blocks: 16   Repaired: 4   Failed: 0
Tokens: 8,330,671 (cached 7,501,952, output 98,328)   Cache hit rate: 91.1%

## Release

> **RELEASED**
> drydock score release LayersTesting · 2026-10-20T20:00:10.860+00:00

- Verdict: PASSED

LayersTesting: PASSED — 9 of 9

  st-001  MET       ["sh", "sources/run.sh"] exited 0; sh sources/run.sh returned 0; LayersTesting: 43 passed, 0 failed (of 43)
  st-002  MET       bin/test.sh returned 0; pytest reported 46 passed
  st-003  MET       sources/run.sh output passed A1/A2 and Z1/Z2
  st-004  MET       sources/run.sh output passed B1 through B4
  st-005  MET       sources/run.sh output passed C1 through C3 and H1 through H3
  st-006  MET       sources/run.sh output passed E1 through E8 and F1 through F10
  st-007  MET       sources/run.sh output passed D1 through D3, F5 through F7, and G2 through G6
  st-008  MET       sources/run.sh output passed G2, G3, G4, and G5
  st-009  MET       cli/__init__.py uses open_database(database_dsn()); configuration.py resolves DATABASE_URL before DATABASE_PATH; schema.sql declares transactions.amount INTEGER; persistence/db.py selects the SQLite or PostgreSQL driver from the DSN

## Project acceptance

| ID | Type | Criterion | Verdict | Observed |
|---|---|---|---|---|
| st-001 | technical | The completed ledger shall make sh sources/run.sh exit zero; that script's exit status is the sole acceptance verdict. | MET | ["sh", "sources/run.sh"] exited 0; sh sources/run.sh returned 0; LayersTesting: 43 passed, 0 failed (of 43) |
| st-002 | technical | The application shall provide a POSIX-compatible bin/test.sh that exits zero when every automated test passes. | MET | bin/test.sh returned 0; pytest reported 46 passed |
| st-003 | behavioral | When ledger init runs, the application shall drop and recreate the accounts, categories, and transactions tables so that ledger count reports zero rows in each. | MET | sources/run.sh output passed A1/A2 and Z1/Z2 |
| st-004 | behavioral | When the three seed files are loaded into an initialized database, the application shall report 4 accounts, 7 categories, and 120 transactions. | MET | sources/run.sh output passed B1 through B4 |
| st-005 | behavioral | The application shall compute the balances, categories, and monthly reports from the database, matching the known answers in sources/run.sh byte for byte. | MET | sources/run.sh output passed C1 through C3 and H1 through H3 |
| st-006 | behavioral | The application shall add, get, rename, and delete accounts and post, get, amend, and delete transactions, reporting an absent record with exit code 4. | MET | sources/run.sh output passed E1 through E8 and F1 through F10 |
| st-007 | behavioral | If a load, post, amend, delete, or transfer is rejected, then the application shall exit 3 and leave every table exactly as it was. | MET | sources/run.sh output passed D1 through D3, F5 through F7, and G2 through G6 |
| st-008 | behavioral | If a command would leave any account balance below zero, then the application shall reject it with exit code 3. | MET | sources/run.sh output passed G2, G3, G4, and G5 |
| st-009 | technical | The application shall reach the database only through the shipped persistence library, selected by DATABASE_URL, with amounts stored as integer cents. | MET | cli/__init__.py uses open_database(database_dsn()); configuration.py resolves DATABASE_URL before DATABASE_PATH; schema.sql declares transactions.amount INTEGER; persistence/db.py selects the SQLite or PostgreSQL driver from the DSN |

**Material decisions:**

- Zero-balance deletion — 
