"""Typed application outcomes used by the CLI boundary."""


class UsageError(Exception):
    """The command line was malformed or incomplete."""


class RejectedError(Exception):
    """The requested operation violates a ledger rule."""


class NotFoundError(Exception):
    """A requested ledger record does not exist."""

