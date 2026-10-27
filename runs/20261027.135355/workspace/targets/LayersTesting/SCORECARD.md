# Scorecard: LayersTesting

## Specification

> **NOT YET RUN**
> drydock score spec LayersTesting

## Acceptance

> **PASSED**
> drydock score ac LayersTesting · 2026-10-27T15:10:00.090+00:00

PASS 119   FAIL 0   UNVERIFIED 0   PREPASSED 25   (144 AC total)

## Build

> **RECORDED**
> drydock score build LayersTesting

Blocks: 10   Repaired: 1   Failed: 0
Tokens: 7,997,462 (cached 7,811,953, output 185,237)   Cache hit rate: 100.0%

## Release

> **RELEASED**
> drydock score release LayersTesting · 2026-10-27T15:11:16.227+00:00

- Verdict: PASSED

LayersTesting: PASSED — 8 of 8

  st-001  MET       ["sh", "sources/run.sh"] exited 0; governed gate full: outcome PASS, return_code 0, 'LayersTesting: 43 passed, 0 failed (of 43)'; sources/run.sh:97-98 exits 0 only when FAILED is 0
  st-004  MET       sources/run.sh:B1-B3 expect 'accounts,4', 'categories,7', 'transactions,120' with exit 0; sources/run.sh:B4 checks counts 4/7/120 across a separate invocation, PASS; governed gate stdout: PASS B1, B2, B3, B4
  st-005  MET       sources/run.sh:45-47 uses cmp -s on stdout for C1-C3; sources/run.sh:H1-H3 repeat the comparison after the transfer and posting workflows; governed gate stdout: PASS C1, C2, C3, H1, H2, H3
  st-006  MET       sources/run.sh:E1-E4 add, get, and rename CASH9 with expected returned values, all PASS; sources/run.sh:E6 'account delete DRAWER1' exits 3 and PASS; sources/run.sh:E7-E8 delete CASH9, then get exits 4, PASS; sources/run.sh:F1-F3 post, get, and amend txn 121 with current values, PASS; sources/run.sh:F8-F9 delete txn 121, then get exits 4, PASS
  st-007  MET       sources/run.sh:D1-D2 rejected load of bad transactions and duplicate account load exit 3, PASS; sources/run.sh:D3 counts still 4/7/120, PASS; sources/run.sh:E2 duplicate account add exits 3, then E3 reads CASH9 unchanged, PASS; sources/run.sh:F5-F7 rejected postings exit 3; H1-H3 later show unchanged totals for the same accounts; probe st011: 'post bad account' and 'post bad date' rc=3, stdout empty
  st-008  MET       sources/run.sh:G2 transfer SAFE->PETTY 999.99 exits 3, PASS; sources/run.sh:G3 post PETTY -1000.00 exits 3, PASS; sources/run.sh:G4 amend txn 1 to 1.00 and G5 delete txn 1 each exit 3, PASS; sources/run.sh:H1 PETTY balance 293.91 and SAFE 750.00 show the rejected G-series commands changed nothing, PASS
  st-010  MET       sources/run.sh:G1 expects txn rows 122 (-500.00 DRAWER1) and 123 (+500.00 SAFE), category TRANSFER, PASS; sources/run.sh:H1 SAFE 250.00 -> 750.00 and DRAWER1 2299.38 -> 1799.38 after G1, PASS; sources/run.sh:H2 TRANSFER net 0.00 at inflow and outflow 5600.00, PASS
  st-011  MET       probe st011: 'frobnicate' rc=2, stdout 0 lines, stderr 1 line; probe st011: 'report nosuch' rc=2, stdout 0 lines, stderr 1 line; probe st011: 'account get' with no argument and with extra arguments rc=2, stdout empty, stderr 1 line; probe st011: 'count extra' and 'init extra' rc=2, stdout empty; probe st011: 'get absent acct' rc=4, stderr 'error: account NOSUCH does not exist'; sources/run.sh:U1-U2 expect exit 2 for unknown command and report, PASS; README.md:28-35 defines the exit-code and stderr contract that the probe checked

## Project acceptance

| ID | Type | Criterion | Verdict | Observed |
|---|---|---|---|---|
| st-001 | technical | The completed ledger shall pass every check in the supplied end-to-end workflow grader, sh sources/run.sh, with exit code zero. | MET | ["sh", "sources/run.sh"] exited 0; governed gate full: outcome PASS, return_code 0, 'LayersTesting: 43 passed, 0 failed (of 43)'; sources/run.sh:97-98 exits 0 only when FAILED is 0 |
| st-004 | behavioral | When the supplied accounts, categories, and transactions files are loaded in order into an empty ledger, the application shall accept all records, report the loaded counts, and retain 4 accounts, 7 categories, and 120 transactions across subsequent command invocations. | MET | sources/run.sh:B1-B3 expect 'accounts,4', 'categories,7', 'transactions,120' with exit 0; sources/run.sh:B4 checks counts 4/7/120 across a separate invocation, PASS; governed gate stdout: PASS B1, B2, B3, B4 |
| st-005 | behavioral | The application shall compute account balances, category totals, and monthly totals from stored ledger data, matching the known answers in sources/run.sh byte for byte both before and after the supplied transaction and transfer workflows. | MET | sources/run.sh:45-47 uses cmp -s on stdout for C1-C3; sources/run.sh:H1-H3 repeat the comparison after the transfer and posting workflows; governed gate stdout: PASS C1, C2, C3, H1, H2, H3 |
| st-006 | behavioral | The application shall retain account additions and renames and transaction postings and amendments across command invocations, return their current values on retrieval, remove successfully deleted records, refuse deletion of an account with transactions with exit code 3, and report an absent record with exit code 4. | MET | sources/run.sh:E1-E4 add, get, and rename CASH9 with expected returned values, all PASS; sources/run.sh:E6 'account delete DRAWER1' exits 3 and PASS; sources/run.sh:E7-E8 delete CASH9, then get exits 4, PASS; sources/run.sh:F1-F3 post, get, and amend txn 121 with current values, PASS; sources/run.sh:F8-F9 delete txn 121, then get exits 4, PASS |
| st-007 | behavioral | If a load, account change, transaction change, or transfer violates a validation or business rule, then the application shall exit 3 and preserve all previously stored ledger records without adding, altering, or removing any record. | MET | sources/run.sh:D1-D2 rejected load of bad transactions and duplicate account load exit 3, PASS; sources/run.sh:D3 counts still 4/7/120, PASS; sources/run.sh:E2 duplicate account add exits 3, then E3 reads CASH9 unchanged, PASS; sources/run.sh:F5-F7 rejected postings exit 3; H1-H3 later show unchanged totals for the same accounts; probe st011: 'post bad account' and 'post bad date' rc=3, stdout empty |
| st-008 | behavioral | If loading transactions, posting, amending, deleting, or transferring would leave any account balance below zero, then the application shall reject the entire command with exit code 3 and preserve the prior balances. | MET | sources/run.sh:G2 transfer SAFE->PETTY 999.99 exits 3, PASS; sources/run.sh:G3 post PETTY -1000.00 exits 3, PASS; sources/run.sh:G4 amend txn 1 to 1.00 and G5 delete txn 1 each exit 3, PASS; sources/run.sh:H1 PETTY balance 293.91 and SAFE 750.00 show the rejected G-series commands changed nothing, PASS |
| st-010 | behavioral | When a valid transfer is requested between distinct accounts, the application shall record an equal debit and credit in category TRANSFER, return both transaction rows, and update both account balances without changing the total cash held. | MET | sources/run.sh:G1 expects txn rows 122 (-500.00 DRAWER1) and 123 (+500.00 SAFE), category TRANSFER, PASS; sources/run.sh:H1 SAFE 250.00 -> 750.00 and DRAWER1 2299.38 -> 1799.38 after G1, PASS; sources/run.sh:H2 TRANSFER net 0.00 at inflow and outflow 5600.00, PASS |
| st-011 | behavioral | The application shall return the CSV headers, row ordering, two-decimal monetary values, and exit codes specified in sources/INSTRUCTIONS.md, returning exit 2 for unknown commands or reports and incorrect argument counts, and writing failures only to standard error. | MET | probe st011: 'frobnicate' rc=2, stdout 0 lines, stderr 1 line; probe st011: 'report nosuch' rc=2, stdout 0 lines, stderr 1 line; probe st011: 'account get' with no argument and with extra arguments rc=2, stdout empty, stderr 1 line; probe st011: 'count extra' and 'init extra' rc=2, stdout empty; probe st011: 'get absent acct' rc=4, stderr 'error: account NOSUCH does not exist'; sources/run.sh:U1-U2 expect exit 2 for unknown command and report, PASS; README.md:28-35 defines the exit-code and stderr contract that the probe checked |

**Ranked improvements:**
1. st-011 cites sources/INSTRUCTIONS.md, which is not in the tree; the contract actually lives in README.md. Either restore the file or repoint the criterion at README.md so the spec it grades against exists.
2. sources/run.sh captures stderr but never compares it, so the 'failures only to standard error' clause of st-011 is only checked by an ad-hoc probe. Add a check that asserts stdout is empty and stderr holds one line for each failing case.
3. st-010 does not say what happens when the two accounts are the same. Either add that case to the criterion (expected exit 3) and to the grader, or state that it is out of scope.
4. Several README requirements have no grader or probe coverage: unknown table names exit 2, and exit 1 for unreadable files is only checked in my probe. Add these to the grader so the gate covers the full exit-code contract.

**Material decisions:**

- Unopenable database detection — 
- Schema bootstrap detaches the acceptance harness — 
- All-or-nothing insert atomicity — 
- Placeholder load commands in this block — 
