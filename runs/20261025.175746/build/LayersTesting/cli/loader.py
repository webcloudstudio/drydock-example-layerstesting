"""Read a bulk-load CSV file into rows of text. Field rules are applied by each load command."""

from __future__ import annotations

import csv
from collections.abc import Sequence

from cli.errors import Operational, Rejected


def read_csv_rows(path: str, header: Sequence[str]) -> list[list[str]]:
    """Return the data rows of ``path``, each checked to carry exactly ``len(header)`` fields.

    An unreadable file raises ``Operational`` (exit 1). A header other than ``header`` or a row with
    the wrong number of fields raises ``Rejected`` (exit 3). Nothing is written here.
    """
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            records = list(csv.reader(fh))
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise Operational(f"cannot read {path}: {exc}") from exc
    if not records or records[0] != list(header):
        raise Rejected(f"header must be {','.join(header)}")
    rows = []
    for number, record in enumerate(records[1:], start=2):
        if len(record) != len(header):
            raise Rejected(f"line {number} must have {len(header)} fields")
        rows.append(record)
    return rows
