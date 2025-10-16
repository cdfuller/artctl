import os
import pytest

import artctl.templater as templater


def build_entry():
    return {
        "name": "spiral",
        "entrypoint": "generators/spiral.py",
        "command": [
            "python3",
            "{entrypoint}",
            "{params.turns}",
            "--output",
            "{output}",
            "{params}",
        ],
        "params": [
            {"name": "turns", "type": "int", "default": 20},
            {"name": "color", "type": "string", "default": "red"},
            {"name": "preview", "type": "bool", "default": False},
        ],
    }


def test_render_command_expands_placeholders(tmp_path):
    entry = build_entry()
    params_values = {"turns": 50, "color": "blue", "preview": True, "output": "out.png"}
    project_root = str(tmp_path)
    result = templater.render_command(entry, params_values, project_root)
    assert result == [
        "python3",
        "generators/spiral.py",
        "50",
        "--output",
        "out.png",
        "--turns",
        "50",
        "--color",
        "blue",
        "--preview",
    ]


def test_render_command_missing_param_raises():
    entry = build_entry()
    params_values = {"color": "blue", "preview": False, "output": "out.png"}
    with pytest.raises(templater.TemplateError):
        templater.render_command(entry, params_values)


def test_render_command_missing_output_raises():
    entry = build_entry()
    params_values = {"turns": 10, "color": "blue", "preview": False}
    with pytest.raises(templater.TemplateError):
        templater.render_command(entry, params_values)


def test_render_command_nonexistent_command_raises():
    entry = {"name": "spiral", "command": []}
    with pytest.raises(templater.TemplateError):
        templater.render_command(entry, {})
