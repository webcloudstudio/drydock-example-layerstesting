# Evidence: Block 2 · Foundational (block-2)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 6943
- execution id: 20261020.192313.901Z-c00a830f

## Stories built
- Establish the relational ledger schema and persistence contract. (database-schema) [story]

## Reusable compacts
- DATABASE_compact.md

## Missing context
- context: INSTRUCTIONS.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: DATABASE.md (SP 1294)
- stack: persistence.md (SP 2407)
- stack: sqlite.md (SP 1818)

## Build directory changes
- persistence/schema.py
- tests/test_database_schema.py

## Build summary
<reusable-compact filename="DATABASE.md">
Relational ledger persistence uses `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`. Tables: `accounts(account VARCHAR(12) PK, name VARCHAR(40))`; `categories(category VARCHAR(12) PK, description VARCHAR(40))`; `transactions(txn_id INTEGER PK, date VARCHAR(10), account/category foreign keys, amount INTEGER cents, memo VARCHAR(60))`. Foreign keys are enforced; initialization recreates all tables empty; rejected operations preserve existing rows; callers use only `persistence.open_database`.
</reusable-compact>

RESULT: SUCCESS

FILES CHANGED:
- persistence/schema.py
- tests/test_database_schema.py

SUMMARY:
Corrected generated row type annotations and added schema round-trip, foreign-key, idempotence, and field-shape tests. Python suite passes: 9 tests.

BLOCKERS:
- `sources/run.sh` remains 2/43 because later CLI/application build blocks are not implemented yet.
