<!-- Compacted from ARCHITECTURE.md sha256=49ef8b29edc8ef8fa0d6cd272eec7dbd47a5dcbb584b85a31883482c96cf0e37 on 2026-10-20 by drydock build agent -->

Executable: ./ledger (root, sh launcher) -> python -m cli -> cli.main(argv) -> int. main never calls sys.exit; exit codes 0 success, 1 operational failure, 2 usage.
cli package: main(argv: list[str] | None = None) -> int; cli.testing.cli_runner(*args) -> (exit_code, stdout, stderr) in process; root conftest.py provides fixture cli_runner.
Database location: DATABASE_URL, then DATABASE_PATH, then data/app.db. Only database_location reads these.
Persistence: only via persistence package (open_database(dsn), db.<table>.<verb>(...)); no module imports a driver.
Money: integer cents everywhere; no floats.
Each command runs in one transaction; balance check before commit.
Network: none, except to a PostgreSQL DSN (this build rejects it with exit 1).
Config reads: only database_location reads env vars.
