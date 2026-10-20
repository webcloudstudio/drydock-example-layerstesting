<!-- Compacted from ARCHITECTURE.md sha256=3360d390c466fa255f8f9444b762fc3f8aa3b3549fc965de9deb50e710830b50 on 2026-10-20 by drydock build agent -->

- Python 3.11+ CLI executable: `./ledger <command>`.
- Boundaries: executable, CLI, configuration, validation, services, persistence, test runner.
- Resolve database via `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`.
- Persistence is exclusively through the shipped `persistence` package.
- Commands include lifecycle, loading, accounts, transactions, transfers, and reports.
- Exit codes: 0 success, 1 operational failure, 2 usage error, 3 rejected input/business rule, 4 absent entity.
- Successful commands emit deterministic CSV; failures emit no stdout and diagnostics on stderr.
- Amounts use integer cents; rejected commands perform no writes.
