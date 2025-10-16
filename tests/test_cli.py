import textwrap

import artctl.cli as cli


def write_registry(tmp_path):
    content = textwrap.dedent(
        """
        name: spiral
        description: Generates a spiral PNG using matplotlib.
        runtime: python
        entrypoint: generators/spiral.py
        command:
          - python3
          - "{entrypoint}"
          - --turns
          - "{params.turns}"
        params:
          - name: turns
            type: int
            default: 20
            help: Number of turns
        output:
          required: true
          extension: png
        tags:
          - python
        """
    ).strip()
    registry_file = tmp_path / "spiral.yaml"
    registry_file.write_text(content + "\n", encoding="utf-8")
    return registry_file


def test_version_flag(capsys):
    exit_code = cli.main(["--version"])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_SUCCESS
    assert "0.1.0" in captured.out


def test_list_subcommand(tmp_path, capsys):
    write_registry(tmp_path)
    exit_code = cli.main(["--registry-path", str(tmp_path), "list"])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_SUCCESS
    assert "- spiral: Generates a spiral PNG using matplotlib." in captured.out


def test_help_subcommand(tmp_path, capsys):
    write_registry(tmp_path)
    exit_code = cli.main(["--registry-path", str(tmp_path), "help", "spiral"])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_SUCCESS
    assert "Name: spiral" in captured.out
    assert "Parameters:" in captured.out
    assert "Source:" in captured.out
    assert "turns: 20" not in captured.out


def test_run_subcommand_reports_placeholder(tmp_path, capsys):
    write_registry(tmp_path)
    exit_code = cli.main(
        [
            "--registry-path",
            str(tmp_path),
            "run",
            "spiral",
            "--dry-run",
            "--set",
            "turns=10",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_SUCCESS
    assert "Execution pipeline for 'spiral' is not implemented yet." in captured.out
    assert "Resolved parameters:" in captured.out
    assert "Dry run requested" in captured.out
    assert "turns: 10" in captured.out
    assert "python3 generators/spiral.py --turns 10" in captured.out


def test_help_for_unknown_program(tmp_path, capsys):
    write_registry(tmp_path)
    exit_code = cli.main(["--registry-path", str(tmp_path), "help", "unknown"])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_VALIDATION_ERROR
    assert "Program 'unknown' not found" in captured.err
