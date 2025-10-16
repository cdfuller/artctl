import textwrap


def write_minimal_registry(tmp_path, extra=None):
    content = {
        "name": "demo",
        "description": "Demo generator",
        "runtime": "python",
        "entrypoint": "generators/demo.py",
        "command": ["python3", "generators/demo.py"],
    }
    if extra:
        content.update(extra)
    return content
