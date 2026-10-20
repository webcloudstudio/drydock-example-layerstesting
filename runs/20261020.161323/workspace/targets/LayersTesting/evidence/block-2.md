# Evidence: Block 2 · Foundational (block-2)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 9657
- execution id: 20261020.162113.828Z-f33c708c

## Stories built
- Provide database configuration and the shipped persistence boundary. (persist-001) [story]

## Reusable compacts
- DATABASE_compact.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: DATABASE.md (SP 2195)
- stack: common.md (SP 1812)
- stack: persistence.md (SP 2407)
- stack: sqlite.md (SP 1818)

## Build directory changes
- config.py
- persistence/db.py
- tests/test_persistence_boundary.py

## Repair attempts
- attempt 0 (initial build): failed; no checks model=gpt-5.6-luna; execution 20261020.161941.681Z-25085663; reason: acceptance regression: architecture-cli-boundary
- attempt 1 (repair 1): built; no checks model=gpt-5.6-luna; execution 20261020.162113.828Z-f33c708c

## Build summary
<reusable-compact filename="DATABASE.md">
Database DSN precedence: `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`. PostgreSQL DSNs use PostgreSQL; other values use SQLite paths, including `sqlite://`.

Schema tables: `accounts(account PK, name)`, `categories(category PK, description)`, and `transactions(txn_id PK, date, account FK, category FK, amount integer cents, memo)`. Foreign keys are enforced.

Persistence access is exclusively through `persistence.open_database(dsn)` and declared typed table operations. Initialization is idempotent and supports recreating all tables. Writes are atomic and fully validated before mutation. No floating-point monetary values.
</reusable-compact>

RESULT: SUCCESS

FILES CHANGED:
- persistence/db.py

SUMMARY:
Restored the persistence boundary’s `initialize()` and `counts()` lifecycle methods. Existing tests pass: 5 passed. The full terminal harness reports 4 passed and 39 failures from later CLI workflow stories outside this build block.

BLOCKERS:
- Full-product `sources/run.sh` remains incomplete because later CLI stories are not part of this block.
