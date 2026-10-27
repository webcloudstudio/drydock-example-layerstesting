"""Shared CSV reader for the ``ledger load`` commands.

The reader only reads: it never touches the database and never writes to a file.
"""

import csv
from collections.abc import Sequence

from ledger_core.errors import Operational, Rejected

Row = tuple[int, list[str]]


def read_rows(path: str, header: Sequence[str]) -> list[Row]:
    """Return ``(line_number, fields)`` for every data row of ``path``, in file order.

    ``header`` lists the column names the table requires, in order. Line numbers are 1-based, so the
    first data row after a header on line 1 is line 2. Blank lines are skipped. Raises ``Operational``
    when the file cannot be read or decoded, and ``Rejected`` when the header differs, the file is
    empty, or a data row's field count differs from ``len(header)``.
    """
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            return _read(fh, path, list(header))
    except OSError as exc:
        raise Operational(f"cannot read {path}: {exc.strerror or exc}") from exc
    except UnicodeDecodeError as exc:
        raise Operational(f"cannot decode {path} as UTF-8: {exc}") from exc


def _read(fh, path: str, header: list[str]) -> list[Row]:
    reader = csv.reader(fh)
    try:
        first = next(reader, None)
        if first is None:
            raise Rejected(f"{path} is empty; expected header {','.join(header)}")
        if first != header:
            raise Rejected(f"{path} line 1: header must be {','.join(header)}")
        rows: list[Row] = []
        for fields in reader:
            if not fields:
                continue
            if len(fields) != len(header):
                raise Rejected(
                    f"{path} line {reader.line_num}: expected {len(header)} fields, found {len(fields)}"
                )
            rows.append((reader.line_num, fields))
        return rows
    except csv.Error as exc:
        raise Rejected(f"{path} line {reader.line_num}: malformed CSV: {exc}") from exc
