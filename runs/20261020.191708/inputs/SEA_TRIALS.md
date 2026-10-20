# Sea Trials: LayersTesting

## Policy

| Consequence | On FAIL | On INCONCLUSIVE |
|---|---|---|
| blocks  | fail   | attest |
| scores  | score  | score  |
| attests | report | report |

## st-001: The supplied grader passes
Type: technical
Required: yes
Criterion: The completed ledger shall make sh sources/run.sh exit zero; that script's exit status is the sole acceptance verdict.
Testability: deterministic
Consequence: blocks
Verification: proof
Command: ["sh", "sources/run.sh"]
Pattern: ubiquitous

## st-002: Test suite passes
Type: technical
Required: yes
Criterion: The application shall provide a POSIX-compatible bin/test.sh that exits zero when every automated test passes.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: ubiquitous

## st-003: Initialization creates an empty schema
Type: behavioral
Required: yes
Criterion: When ledger init runs, the application shall drop and recreate the accounts, categories, and transactions tables so that ledger count reports zero rows in each.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: event

## st-004: The seed files load exactly
Type: behavioral
Required: yes
Criterion: When the three seed files are loaded into an initialized database, the application shall report 4 accounts, 7 categories, and 120 transactions.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: event

## st-005: Reports match the known answers
Type: behavioral
Required: yes
Criterion: The application shall compute the balances, categories, and monthly reports from the database, matching the known answers in sources/run.sh byte for byte.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: ubiquitous

## st-006: Accounts and transactions support create, read, update, and delete
Type: behavioral
Required: yes
Criterion: The application shall add, get, rename, and delete accounts and post, get, amend, and delete transactions, reporting an absent record with exit code 4.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: ubiquitous

## st-007: A failed command changes nothing
Type: behavioral
Required: yes
Criterion: If a load, post, amend, delete, or transfer is rejected, then the application shall exit 3 and leave every table exactly as it was.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: unwanted

## st-008: No balance goes negative
Type: behavioral
Required: yes
Criterion: If a command would leave any account balance below zero, then the application shall reject it with exit code 3.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: unwanted

## st-009: Persistence goes through the shipped library
Type: technical
Required: yes
Criterion: The application shall reach the database only through the shipped persistence library, selected by DATABASE_URL, with amounts stored as integer cents.
Testability: judgeable
Consequence: scores
Verification: llm
Pattern: ubiquitous
