"""Domain errors. Each carries the process exit code the CLI reports."""


class LedgerError(Exception):
    """Base class for every domain error the ledger raises."""

    exit_code: int


class Rejected(LedgerError):
    """Invalid input, duplicate key, unknown reference, account in use, or negative balance."""

    exit_code = 3


class NotFound(LedgerError):
    """An account or transaction is absent on get, rename, delete, or amend."""

    exit_code = 4


class Operational(LedgerError):
    """An unreadable file or an unopenable database."""

    exit_code = 1
