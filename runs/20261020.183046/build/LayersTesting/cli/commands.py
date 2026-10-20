"""Command dispatch kept separate from argparse construction."""

from __future__ import annotations

from argparse import Namespace

from ledger_app.services import dispatch as service_dispatch


def dispatch(args: Namespace, database_dsn: str) -> int:
    """Pass a parsed command to the application service boundary."""

    return service_dispatch(args, database_dsn)
