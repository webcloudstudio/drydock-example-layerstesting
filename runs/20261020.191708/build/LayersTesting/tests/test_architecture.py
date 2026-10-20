from importlib import import_module
import inspect


def test_cli_and_persistence_packages_are_importable():
    cli = import_module("cli")
    persistence = import_module("persistence")
    assert hasattr(cli, "main")
    assert hasattr(persistence, "open_database")


def test_cli_main_accepts_argv_and_reports_missing_command():
    from cli import main

    assert "argv" in inspect.signature(main).parameters
    assert main([]) == 2


def test_configuration_precedence():
    from configuration import database_dsn

    assert database_dsn({}) == "data/app.db"
    assert database_dsn({"DATABASE_PATH": "path.db"}) == "path.db"
    assert database_dsn({"DATABASE_URL": "url", "DATABASE_PATH": "path.db"}) == "url"


def test_validation_keeps_money_as_integer_cents():
    from validation import validate_cents

    assert validate_cents(125) == 125


def test_validation_rejects_punctuation_in_codes():
    import pytest

    from validation import validate_code

    with pytest.raises(ValueError):
        validate_code("BAD-CODE")
