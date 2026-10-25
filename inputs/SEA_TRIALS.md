# Sea Trials: LayersTesting

## Policy

| Consequence | On FAIL | On INCONCLUSIVE |
|---|---|---|
| blocks  | fail   | attest |
| scores  | score  | score  |
| attests | report | report |

## Acceptance scope

Sea Trials assess ledger workflows and their observable results. Database preparation is a
prerequisite exercised by the supplied grader, not a separate release criterion. Verification
uses the declared ledger commands and supplied data; it does not introduce schema mutations,
schema-replacement requirements, or database-engine qualification tests. Stack and persistence
implementation constraints remain in the build instructions.

The supplied grader and the behavioral criteria below are required release evidence. Its exit
status establishes grader conformance; it is not the sole verdict for all Sea Trials. Criterion
identifiers are retained; st-002, st-003, and st-009 are retired.

## st-001: The supplied grader passes
Type: technical
Required: yes
Criterion: The completed ledger shall pass every check in the supplied end-to-end workflow grader, sh sources/run.sh, with exit code zero.
Testability: deterministic
Consequence: blocks
Verification: proof
Command: ["sh", "sources/run.sh"]
Pattern: ubiquitous

## st-004: The seed files load exactly
Type: behavioral
Required: yes
Criterion: When the supplied accounts, categories, and transactions files are loaded in order into an empty ledger, the application shall accept all records, report the loaded counts, and retain 4 accounts, 7 categories, and 120 transactions across subsequent command invocations.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: event

## st-005: Reports match the known answers
Type: behavioral
Required: yes
Criterion: The application shall compute account balances, category totals, and monthly totals from stored ledger data, matching the known answers in sources/run.sh byte for byte both before and after the supplied transaction and transfer workflows.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: ubiquitous

## st-006: Accounts and transactions support create, read, update, and delete
Type: behavioral
Required: yes
Criterion: The application shall retain account additions and renames and transaction postings and amendments across command invocations, return their current values on retrieval, remove successfully deleted records, refuse deletion of an account with transactions with exit code 3, and report an absent record with exit code 4.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: ubiquitous

## st-007: A failed command changes nothing
Type: behavioral
Required: yes
Criterion: If a load, account change, transaction change, or transfer violates a validation or business rule, then the application shall exit 3 and preserve all previously stored ledger records without adding, altering, or removing any record.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: unwanted

## st-008: No balance goes negative
Type: behavioral
Required: yes
Criterion: If loading transactions, posting, amending, deleting, or transferring would leave any account balance below zero, then the application shall reject the entire command with exit code 3 and preserve the prior balances.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: unwanted

## st-010: Transfers conserve cash
Type: behavioral
Required: yes
Criterion: When a valid transfer is requested between distinct accounts, the application shall record an equal debit and credit in category TRANSFER, return both transaction rows, and update both account balances without changing the total cash held.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: event

## st-011: Command results follow the CLI contract
Type: behavioral
Required: yes
Criterion: The application shall return the CSV headers, row ordering, two-decimal monetary values, and exit codes specified in sources/INSTRUCTIONS.md, returning exit 2 for unknown commands or reports and incorrect argument counts, and writing failures only to standard error.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: ubiquitous
