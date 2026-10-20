from cli.testing import cli_runner


def test_unknown_command_is_usage_error():
    code, stdout, stderr = cli_runner("frobnicate")

    assert code == 2
    assert stdout == ""
    assert stderr != ""


def test_unknown_report_is_usage_error():
    code, stdout, stderr = cli_runner("report", "nosuch")

    assert code == 2
    assert stdout == ""
    assert stderr != ""


def test_wrong_argument_count_is_usage_error():
    code, stdout, stderr = cli_runner("account", "add")

    assert code == 2
    assert stdout == ""
    assert stderr != ""


def test_help_is_available_for_dispatcher_and_command_families():
    for arguments in (("--help",), ("account", "--help"), ("txn", "--help"), ("report", "--help")):
        code, stdout, stderr = cli_runner(*arguments)

        assert code == 0
        assert stdout != ""
        assert stderr == ""
