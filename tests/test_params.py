import pytest

import artctl.params as params


def test_parse_overrides_coerces_types():
    declared = [
        {"name": "turns", "type": "int", "default": 5},
        {"name": "scale", "type": "float", "default": 1.0},
        {"name": "title", "type": "string", "default": "demo"},
        {"name": "enabled", "type": "bool", "default": True},
    ]
    result = params.parse_overrides(
        ["turns=10", "scale=2.5", "title=art", "enabled=false"],
        declared,
    )
    assert result == {
        "turns": 10,
        "scale": 2.5,
        "title": "art",
        "enabled": False,
    }


def test_parse_overrides_applies_defaults():
    declared = [
        {"name": "turns", "type": "int", "default": 5},
        {"name": "mode", "type": "enum", "choices": ["a", "b"], "default": "a"},
    ]
    result = params.parse_overrides([], declared)
    assert result == {"turns": 5, "mode": "a"}


def test_parse_overrides_unknown_param_raises():
    declared = [{"name": "turns", "type": "int", "default": 5}]
    with pytest.raises(params.ParameterError):
        params.parse_overrides(["radius=10"], declared)


def test_parse_overrides_required_missing_raises():
    declared = [{"name": "turns", "type": "int", "required": True}]
    with pytest.raises(params.ParameterError):
        params.parse_overrides([], declared)


def test_parse_overrides_invalid_format_raises():
    declared = [{"name": "turns", "type": "int"}]
    with pytest.raises(params.ParameterError):
        params.parse_overrides(["turns"], declared)
