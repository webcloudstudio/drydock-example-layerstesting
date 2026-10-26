"""Expected failures of the ledger, each carrying the exit code the process reports."""

from __future__ import annotations


class LedgerError(Exception):
    """An expected failure. ``exit_code`` is what the dispatcher returns for it."""

    exit_code: int = 1


class Operational(LedgerError):
    """A failure of the ledger's own operation, such as an unreadable input file."""

    exit_code = 1


class Usage(LedgerError):
    """A command line the ledger does not accept: unknown command, table, or report, or arity."""

    exit_code = 2


class Rejected(LedgerError):
    """Input that fails validation or a business rule. Nothing has been written."""

    exit_code = 3


class NotFound(LedgerError):
    """A well-formed request for a record that does not exist."""

    exit_code = 4
