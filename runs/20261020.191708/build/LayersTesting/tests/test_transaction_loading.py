import csv

from cli.testing import cli_runner


def _database(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "ledger.db"))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert cli_runner("init")[0] == 0


def _masters(tmp_path):
    accounts = tmp_path / "accounts.csv"
    categories = tmp_path / "categories.csv"
    accounts.write_text("account,name\nA1,Drawer\n", encoding="utf-8")
    categories.write_text("category,description\nC1,Sales\n", encoding="utf-8")
    return accounts, categories


def test_transaction_load_round_trips_integer_cents(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)
    accounts, categories = _masters(tmp_path)
    transactions = tmp_path / "transactions.csv"
    transactions.write_text(
        "txn_id,date,account,category,amount,memo\n"
        "1,2026-01-01,A1,C1,12.34,sale\n",
        encoding="utf-8",
    )

    assert cli_runner("load", "accounts", str(accounts))[0] == 0
    assert cli_runner("load", "categories", str(categories))[0] == 0
    assert cli_runner("load", "transactions", str(transactions))[0] == 0

    code, output, _ = cli_runner("txn", "get", "1")
    assert code == 0
    assert list(csv.reader(output.splitlines()))[1] == [
        "1", "2026-01-01", "A1", "C1", "12.34", "sale"
    ]


def test_transaction_load_rejects_later_bad_reference_atomically(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)
    accounts, categories = _masters(tmp_path)
    transactions = tmp_path / "bad.csv"
    transactions.write_text(
        "txn_id,date,account,category,amount,memo\n"
        "1,2026-01-01,A1,C1,1.00,ok\n"
        "2,2026-01-01,NOPE,C1,1.00,bad\n",
        encoding="utf-8",
    )
    assert cli_runner("load", "accounts", str(accounts))[0] == 0
    assert cli_runner("load", "categories", str(categories))[0] == 0

    assert cli_runner("load", "transactions", str(transactions))[0] == 3
    assert cli_runner("txn", "get", "1")[0] == 4


def test_transaction_load_rejects_header_shape_and_row_shape(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)
    accounts, categories = _masters(tmp_path)
    assert cli_runner("load", "accounts", str(accounts))[0] == 0
    assert cli_runner("load", "categories", str(categories))[0] == 0

    for name, body in {
        "header.csv": "id,date,account,category,amount,memo\n",
        "short.csv": "txn_id,date,account,category,amount,memo\n1,2026-01-01,A1,C1,1.00\n",
        "extra.csv": "txn_id,date,account,category,amount,memo\n1,2026-01-01,A1,C1,1.00,x,extra\n",
    }.items():
        path = tmp_path / name
        path.write_text(body, encoding="utf-8")
        assert cli_runner("load", "transactions", str(path))[0] == 3


def test_transaction_load_rejects_invalid_date_amount_duplicate_and_balance(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)
    accounts, categories = _masters(tmp_path)
    assert cli_runner("load", "accounts", str(accounts))[0] == 0
    assert cli_runner("load", "categories", str(categories))[0] == 0

    cases = {
        "date.csv": "1,2026-02-30,A1,C1,1.00,x\n",
        "amount.csv": "1,2026-01-01,A1,C1,1.234,x\n",
        "duplicate.csv": "1,2026-01-01,A1,C1,1.00,x\n1,2026-01-01,A1,C1,1.00,y\n",
        "balance.csv": "1,2026-01-01,A1,C1,-1.00,x\n",
    }
    for name, rows in cases.items():
        path = tmp_path / name
        path.write_text("txn_id,date,account,category,amount,memo\n" + rows, encoding="utf-8")
        assert cli_runner("load", "transactions", str(path))[0] == 3

