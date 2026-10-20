<!-- Compacted from ARCHITECTURE.md sha256=5bb2daf4b33e931bfcab4f8a58c3ea712b73318602a2133a2688b9cea780697b on 2026-10-20 by drydock build agent -->

Python CLI ledger with executable `ledger`; configuration precedence is `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`. CLI routing, validation, transactional services, reporting, and persistence are separate boundaries. All database access goes through `persistence.open_database`; amounts use integer cents; commands are atomic; reports query stored data.
