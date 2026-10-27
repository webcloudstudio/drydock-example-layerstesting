"""Shared pytest fixtures for the ledger test suite.

The ``db_session`` and ``cli_runner`` fixtures delegate to helpers owned by the
generated ``persistence`` package and the ``cli`` package. Those packages arrive
with their own stories, so the imports stay inside the fixtures until then.
"""

import pytest


@pytest.fixture
def db_session():
    """Provisioned application store, supplied by ``persistence.testing``."""
    from persistence.testing import db_session as provision

    return provision()


@pytest.fixture
def cli_runner():
    """Command runner that invokes the ``ledger`` CLI, supplied by ``cli.testing``."""
    from cli.testing import cli_runner as provision

    return provision()
