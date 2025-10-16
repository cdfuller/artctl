import os
import textwrap

import pytest

import artctl.registry as registry


def write_file(directory, name, content):
    path = directory / name
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")
    return path


def test_load_registry_success(tmp_path):
    write_file(
        tmp_path,
        "spiral.yaml",
        """
        name: spiral
        description: Spiral generator
        runtime: python
        entrypoint: generators/spiral.py
        command:
          - python3
          - generators/spiral.py
        """,
    )
    entries = registry.load_registry(tmp_path)
    assert "spiral" in entries
    entry = entries["spiral"]
    assert entry["runtime"] == "python"
    assert entry["source_path"] == os.path.join(tmp_path, "spiral.yaml")


def test_duplicate_registry_name_raises(tmp_path):
    write_file(
        tmp_path,
        "a.yaml",
        """
        name: spiral
        description: Spiral generator
        runtime: python
        entrypoint: generators/spiral.py
        command:
          - python3
          - generators/spiral.py
        """,
    )
    write_file(
        tmp_path,
        "b.yaml",
        """
        name: spiral
        description: Duplicate spiral
        runtime: python
        entrypoint: generators/spiral.py
        command:
          - python3
          - generators/spiral.py
        """,
    )
    with pytest.raises(registry.RegistryError) as excinfo:
        registry.load_registry(tmp_path)
    assert "Duplicate registry name 'spiral'" in str(excinfo.value)


def test_missing_required_field_raises(tmp_path):
    write_file(
        tmp_path,
        "invalid.yaml",
        """
        name: spiral
        description: Missing command
        runtime: python
        entrypoint: generators/spiral.py
        """,
    )
    with pytest.raises(registry.RegistryError) as excinfo:
        registry.load_registry(tmp_path)
    assert "Missing required fields" in str(excinfo.value)


def test_unknown_top_level_field_raises(tmp_path):
    write_file(
        tmp_path,
        "extra.yaml",
        """
        name: spiral
        description: Spiral generator
        runtime: python
        entrypoint: generators/spiral.py
        command:
          - python3
          - generators/spiral.py
        extra_field: nope
        """,
    )
    with pytest.raises(registry.RegistryError) as excinfo:
        registry.load_registry(tmp_path)
    assert "Unknown fields" in str(excinfo.value)


def test_invalid_param_definition_raises(tmp_path):
    write_file(
        tmp_path,
        "bad_param.yaml",
        """
        name: spiral
        description: Spiral generator
        runtime: python
        entrypoint: generators/spiral.py
        command:
          - python3
          - generators/spiral.py
        params:
          - name: turns
            default: 20
        """,
    )
    with pytest.raises(registry.RegistryError) as excinfo:
        registry.load_registry(tmp_path)
    assert "missing fields" in str(excinfo.value)
