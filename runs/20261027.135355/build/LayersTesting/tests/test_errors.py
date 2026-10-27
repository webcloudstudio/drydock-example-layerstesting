"""Domain error classes and their exit codes."""

import pytest

from ledger_core.errors import LedgerError, NotFound, Operational, Rejected


@pytest.mark.parametrize(
    ("cls", "code"),
    [(Rejected, 3), (NotFound, 4), (Operational, 1)],
)
def test_error_class_carries_exit_code(cls, code):
    assert cls("probe").exit_code == code


@pytest.mark.parametrize("cls", [Rejected, NotFound, Operational])
def test_error_class_derives_from_ledger_error(cls):
    assert issubclass(cls, LedgerError)


def test_error_keeps_its_message():
    assert str(Rejected("duplicate account")) == "duplicate account"
