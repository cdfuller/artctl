import textwrap

import artctl.cli as cli


class StubOutputPath:
    def __init__(self, path):
        self.path = path
        self.calls = []

    def __call__(self, entry, base_dir=None, now=None, params_values=None):
        self.calls.append({
            "entry": entry,
            "base_dir": base_dir,
            "now": now,
            "params_values": params_values,
        })
        return self.path


class StubVerifyOutput:
    def __init__(self, should_exist=True):
        self.should_exist = should_exist
        self.calls = []

    def __call__(self, entry, path):
        self.calls.append({"entry": entry, "path": path})
        return self.should_exist


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
    stub_output = StubOutputPath("/tmp/fixed/path.png")
    original = cli.output_manager.build_output_path
    cli.output_manager.build_output_path = stub_output
    try:
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
    finally:
        cli.output_manager.build_output_path = original
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_SUCCESS
    assert "Execution pipeline for 'spiral' is not implemented yet." in captured.out
    assert "Resolved parameters:" in captured.out
    assert "Dry run requested" in captured.out
    assert "turns: 10" in captured.out
    assert "output: /tmp/fixed/path.png" in captured.out
    assert "python3 generators/spiral.py" in captured.out
    assert "--turns 10" in captured.out
    assert "Output path:\n  /tmp/fixed/path.png" in captured.out


def test_help_for_unknown_program(tmp_path, capsys):
    write_registry(tmp_path)
    exit_code = cli.main(["--registry-path", str(tmp_path), "help", "unknown"])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_VALIDATION_ERROR
    assert "Program 'unknown' not found" in captured.err
def test_run_with_missing_param_reports_error(tmp_path, capsys):
    write_registry(tmp_path)
    exit_code = cli.main([
        "--registry-path",
        str(tmp_path),
        "run",
        "spiral",
        "--set",
        "unknown=1",
    ])
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_VALIDATION_ERROR
    assert "Unknown parameter" in captured.err


def test_run_with_missing_entrypoint(tmp_path, capsys):
    write_registry(tmp_path)
    stub_output = StubOutputPath("/tmp/fixed/path.png")
    original_output = cli.output_manager.build_output_path
    try:
        cli.output_manager.build_output_path = stub_output
        exit_code = cli.main([
            "--registry-path",
            str(tmp_path),
            "run",
            "spiral",
        ])
    finally:
        cli.output_manager.build_output_path = original_output
    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_INTERNAL_ERROR
    assert "Execution error" in captured.err


def test_run_reports_missing_output(tmp_path, capsys):
    write_registry(tmp_path)
    stub_output = StubOutputPath("/tmp/fixed/path.png")
    stub_verify = StubVerifyOutput(should_exist=False)
    original_output = cli.output_manager.build_output_path
    original_verify = cli.output_manager.verify_output
    original_execute = cli.runner.execute
    try:
        cli.output_manager.build_output_path = stub_output
        cli.output_manager.verify_output = stub_verify
        cli.runner.execute = lambda command, working_dir=None: 0
        exit_code = cli.main([
            "--registry-path",
            str(tmp_path),
            "run",
            "spiral",
        ])
    finally:
        cli.output_manager.build_output_path = original_output
        cli.output_manager.verify_output = original_verify
        cli.runner.execute = original_execute
    captured = capsys.readouterr()
    assert exit_code == 4
    assert "Expected output was not produced" in captured.err
