"""Store a group of transaction rows as one unit. Callers validate everything before calling this."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from persistence import PersistenceError


def store_transactions(db, rows: Sequence[Mapping[str, Any]]) -> list[Any]:
    """Create each row in order and return the stored rows.

    The application has no multi-statement transaction, so the group is made all-or-nothing by
    compensation: when a create fails part-way, the rows already created are deleted before the
    failure is raised again.
    """
    created: list[Any] = []
    try:
        for row in rows:
            created.append(db.transactions.create(**row))
    except PersistenceError:
        for stored in created:
            db.transactions.delete(txn_id=stored.txn_id)
        raise
    return created
