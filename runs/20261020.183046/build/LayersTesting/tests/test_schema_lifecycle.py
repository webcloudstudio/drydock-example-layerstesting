from __future__ import annotations

import csv
import os

from cli.testing import cli_runner


def _count_rows(output: str) -> list[list[str]]:
    return list(csv.reader(output.splitlines()))


def test_init_creates_empty_schema_and_count_uses_documented_order(tmp_path) -> None:
    database_path = str(tmp_path / "ledger.db")
    old_path = os.environ.get("DATABASE_PATH")
    old_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_PATH"] = database_path
    os.environ.pop("DATABASE_URL", None)
    try:
        code, output, error = cli_runner("init")
        assert (code, output, error) == (0, "", "")

        code, output, error = cli_runner("count")
        assert code == 0
        assert error == ""
        assert _count_rows(output) == [
            ["table", "rows"],
            ["accounts", "0"],
            ["categories", "0"],
            ["transactions", "0"],
        ]
    finally:
        if old_path is None:
            os.environ.pop("DATABASE_PATH", None)
        else:
            os.environ["DATABASE_PATH"] = old_path
        if old_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = old_url


def test_init_removes_existing_account_rows(tmp_path) -> None:
    database_path = str(tmp_path / "ledger.db")
    old_path = os.environ.get("DATABASE_PATH")
    old_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_PATH"] = database_path
    os.environ.pop("DATABASE_URL", None)
    try:
        assert cli_runner("init")[0] == 0
        from persistence import open_database

        with open_database(database_path) as database:
            database.accounts.create(account="cash", name="Cash")

        assert cli_runner("init")[0] == 0
        code, output, _error = cli_runner("count")
        assert code == 0
        assert [row[1] for row in _count_rows(output)[1:]] == ["0", "0", "0"]
    finally:
        if old_path is None:
            os.environ.pop("DATABASE_PATH", None)
        else:
            os.environ["DATABASE_PATH"] = old_path
        if old_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = old_url
