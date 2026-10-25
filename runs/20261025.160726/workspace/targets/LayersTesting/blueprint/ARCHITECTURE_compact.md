<!-- Compacted from ARCHITECTURE.md sha256=99ca066328acb591ecca1c7a8e4a44bcc283f6fe22444f777eca292d0f11b75b on 2026-10-25 by drydock build agent -->

Executable `ledger` at application root calls cli.main(argv) and exits with its return value.
cli: main(argv) -> int; registry.register(words, handler, nargs); errors LedgerError(code) with OperationalError=1, UsageError=2, Rejected=3, NotFound=4; config.resolve_dsn(environ); context.open_store(); testing.cli_runner(*args) -> (code, stdout, stderr).
Exit codes: 0 success, 1 operational or unexpected, 2 usage, 3 rejected, 4 not found.
Output: successful commands write unquoted CSV, LF endings, two-decimal amounts; failures write nothing to stdout and one stderr line.
Persistence only through persistence.open_database; no driver import outside persistence/.
Money is integer cents at every layer.
