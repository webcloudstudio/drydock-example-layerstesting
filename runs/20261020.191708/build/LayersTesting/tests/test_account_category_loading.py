import csv
from cli.testing import cli_runner


def _database(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "ledger.db"))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert cli_runner("init")[0] == 0


def test_account_and_category_load_round_trip(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)
    accounts = tmp_path / "accounts.csv"
    categories = tmp_path / "categories.csv"
    accounts.write_text("account,name\nA1,Drawer\n", encoding="utf-8")
    categories.write_text("category,description\nC1,Sales\n", encoding="utf-8")

    assert cli_runner("load", "accounts", str(accounts))[0] == 0
    assert cli_runner("load", "categories", str(categories))[0] == 0
    code, output, _ = cli_runner("account", "get", "A1")

    assert code == 0
    assert list(csv.reader(output.splitlines()))[1][:2] == ["A1", "Drawer"]


def test_invalid_load_preserves_existing_rows(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)
    valid = tmp_path / "valid.csv"
    invalid = tmp_path / "invalid.csv"
    valid.write_text("account,name\nA1,Drawer\n", encoding="utf-8")
    invalid.write_text("wrong,header\nA2,Second\n", encoding="utf-8")
    assert cli_runner("load", "accounts", str(valid))[0] == 0
    before = cli_runner("count")

    assert cli_runner("load", "accounts", str(invalid))[0] == 3
    after = cli_runner("count")
    assert after[0] == 0
    assert after[1] == before[1]
    assert cli_runner("load", "accounts", str(tmp_path / "missing.csv"))[0] == 1


def test_master_data_load_rejects_duplicates_codes_and_lengths(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)
    duplicate = tmp_path / "duplicate.csv"
    duplicate.write_text("account,name\nA1,One\nA1,Two\n", encoding="utf-8")
    invalid_code = tmp_path / "invalid-code.csv"
    invalid_code.write_text("category,description\nbad-code,Sales\n", encoding="utf-8")
    too_long = tmp_path / "too-long.csv"
    too_long.write_text("account,name\nA2," + "x" * 41 + "\n", encoding="utf-8")

    assert cli_runner("load", "accounts", str(duplicate))[0] == 3
    assert cli_runner("load", "categories", str(invalid_code))[0] == 3
    assert cli_runner("load", "accounts", str(too_long))[0] == 3


def test_master_data_load_accepts_empty_data_file(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)
    empty = tmp_path / "empty.csv"
    empty.write_text("account,name\n", encoding="utf-8")

    assert cli_runner("load", "accounts", str(empty))[0] == 0
    assert cli_runner("count")[1].splitlines()[1] == "accounts,0"
