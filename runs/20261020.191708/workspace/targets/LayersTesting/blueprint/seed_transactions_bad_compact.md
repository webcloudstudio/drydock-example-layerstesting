<!-- Compacted from seed_transactions_bad.csv sha256=a7cffd87094d0bec741438e34dd8992f893d2e93ec0d32dad8395502d4b5af46 on 2026-10-20 by drydock build agent -->

CSV contract matches `seed_transactions.csv`. The staged dataset contains 11 rows: 10 valid transactions followed by one transaction referencing `NOSUCH`; the complete batch must be rejected atomically with no rows inserted.
