import csv

from cli.testing import cli_runner
from persistence import open_database


def _ready(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "ledger.db"))
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "FROM", "Source")[0] == 0
    assert cli_runner("account", "add", "TO", "Destination")[0] == 0
    assert cli_runner("category", "add", "TRANSFER", "Internal transfer")[0] == 0


def test_transfer_creates_ordered_rows_with_transfer_memos(tmp_path, monkeypatch):
    _ready(tmp_path, monkeypatch)
    assert cli_runner("txn", "post", "FROM", "TRANSFER", "100.00", "2026-04-01")[0] == 0

    code, output, stderr = cli_runner("transfer", "FROM", "TO", "25.00", "2026-04-02")

    assert code == 0
    assert stderr == ""
    assert list(csv.reader(output.splitlines())) == [
        ["txn_id", "date", "account", "category", "amount", "memo"],
        ["2", "2026-04-02", "FROM", "TRANSFER", "-25.00", "transfer to TO"],
        ["3", "2026-04-02", "TO", "TRANSFER", "25.00", "transfer from FROM"],
    ]
    with open_database(str(tmp_path / "ledger.db")) as db:
        transactions = db.transactions.list()
        assert [(row.account, row.amount) for row in transactions] == [
            ("FROM", 10000),
            ("FROM", -2500),
            ("TO", 2500),
        ]


def test_transfer_rejects_invalid_inputs_without_writing(tmp_path, monkeypatch):
    _ready(tmp_path, monkeypatch)
    for source, destination, amount, day in (
        ("FROM", "FROM", "1.00", "2026-04-01"),
        ("FROM", "MISSING", "1.00", "2026-04-01"),
        ("FROM", "TO", "0.00", "2026-04-01"),
        ("FROM", "TO", "1.00", "2026-02-30"),
    ):
        assert cli_runner("transfer", source, destination, amount, day)[0] == 3

    with open_database(str(tmp_path / "ledger.db")) as db:
        assert db.transactions.list() == []


def test_transfer_rejects_insufficient_balance_without_writing(tmp_path, monkeypatch):
    _ready(tmp_path, monkeypatch)
    assert cli_runner("txn", "post", "FROM", "TRANSFER", "10.00", "2026-04-01")[0] == 0

    assert cli_runner("transfer", "FROM", "TO", "10.01", "2026-04-02")[0] == 3

    with open_database(str(tmp_path / "ledger.db")) as db:
        transactions = db.transactions.list()
        assert len(transactions) == 1
        assert transactions[0].amount == 1000
