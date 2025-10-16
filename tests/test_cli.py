import artctl.cli as cli


def test_version_flag(capsys):
    exit_code = cli.main(["--version"])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_SUCCESS
    assert "0.1.0" in captured.out


def test_list_subcommand(capsys):
    exit_code = cli.main(["list"])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_SUCCESS
    assert "not implemented" in captured.out


def test_help_subcommand_requires_program(capsys):
    exit_code = cli.main(["help", "demo"])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_SUCCESS
    assert "demo" in captured.out


def test_run_subcommand_supports_dry_run(capsys):
    exit_code = cli.main(["run", "demo", "--dry-run", "--set", "turns=10"])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_SUCCESS
    assert "Dry run" in captured.out
