"""Shared pytest fixtures for the project suite."""

import pytest

from cli import testing


@pytest.fixture
def cli_runner():
    return testing.cli_runner
