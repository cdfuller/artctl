import os
from datetime import datetime

import pytest

import artctl.output_manager as output_manager


def test_build_output_path_default(tmp_path):
    entry = {"name": "spiral", "output": {"extension": "jpg"}}
    now = datetime(2025, 1, 2, 3, 4, 5)
    path = output_manager.build_output_path(entry, base_dir=str(tmp_path), now=now)
    expected = tmp_path / "2025/01/02/spiral-030405.jpg"
    assert path == str(expected)
    assert expected.parent.exists()


def test_build_output_path_template(tmp_path):
    entry = {
        "name": "spiral",
        "entrypoint": "generators/spiral.py",
        "output": {
            "path_template": "custom/{date_path}/{name}-{params.turns}.png",
        },
    }
    now = datetime(2025, 1, 2, 3, 4, 5)
    path = output_manager.build_output_path(
        entry,
        base_dir=str(tmp_path),
        now=now,
        params_values={"turns": 10},
    )
    expected = tmp_path / "custom/2025/01/02/spiral-10.png"
    assert path == str(expected)
    assert expected.parent.exists()


def test_build_output_path_missing_param_raises():
    entry = {
        "name": "spiral",
        "output": {
            "path_template": "{name}-{params.turns}.png",
        },
    }
    with pytest.raises(output_manager.OutputError):
        output_manager.build_output_path(entry, params_values={})
