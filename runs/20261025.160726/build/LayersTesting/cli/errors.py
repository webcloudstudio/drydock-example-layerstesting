"""Expected failures and their exit codes. Each subclass maps to exactly one code."""


class LedgerError(Exception):
    """Base for an expected failure. ``code`` is the process exit status."""

    code = 1

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class OperationalError(LedgerError):
    """The store or a file could not be used: unreachable, missing tables, unreadable file."""

    code = 1


class UsageError(LedgerError):
    """Unknown command, unknown table or report, or a wrong argument count."""

    code = 2


class Rejected(LedgerError):
    """Invalid input, duplicate key, unknown reference, account in use, or a negative balance."""

    code = 3


class NotFound(LedgerError):
    """An absent account or transaction id."""

    code = 4
