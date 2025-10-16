import shutil

import pytest

import artctl.cli as cli


def test_run_spiral_generator(tmp_path):
    output_path = tmp_path / "spiral.png"

    def stub_output(entry, base_dir=None, now=None, params_values=None):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return str(output_path)

    original_output = cli.output_manager.build_output_path
    try:
        cli.output_manager.build_output_path = stub_output
        exit_code = cli.main(["run", "spiral", "--dry-run"])
        assert exit_code == cli.EXIT_SUCCESS

        cli.output_manager.build_output_path = stub_output
        exit_code = cli.main(["run", "spiral"])
    finally:
        cli.output_manager.build_output_path = original_output

    assert exit_code == cli.EXIT_SUCCESS
    assert output_path.exists()
    with open(output_path, "rb") as handle:
        data = handle.read(8)
    assert data == b"\x89PNG\r\n\x1a\n"


@pytest.mark.skipif(shutil.which("node") is None, reason="Node runtime not available")
def test_run_night_sky_generator(tmp_path):
    output_path = tmp_path / "night_sky.png"

    def stub_output(entry, base_dir=None, now=None, params_values=None):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return str(output_path)

    original_output = cli.output_manager.build_output_path
    try:
        cli.output_manager.build_output_path = stub_output
        exit_code = cli.main(["run", "night_sky", "--dry-run"])
        assert exit_code == cli.EXIT_SUCCESS

        cli.output_manager.build_output_path = stub_output
        exit_code = cli.main(["run", "night_sky", "--set", "stars=50"])
    finally:
        cli.output_manager.build_output_path = original_output

    assert exit_code == cli.EXIT_SUCCESS
    assert output_path.exists()
    with open(output_path, "rb") as handle:
        data = handle.read(8)
    assert data == b"\x89PNG\r\n\x1a\n"
