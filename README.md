# artctl

Generative art control line interface that standardizes how local generators are discovered, configured, and executed.

`artctl` lets you define creative coding programs in declarative YAML, then run them with consistent CLI ergonomics. The flagship use case is managing multiple Python or Node generators side by side while keeping outputs reproducible.

## Quickstart

```bash
uv sync                    # install dependencies into .venv
uv run artctl list         # inspect available registry entries
uv run artctl run spiral   # run the Python example generator
uv run artctl help spiral  # inspect parameters and metadata
```

Outputs land under `outputs/YYYY/MM/DD/` with timestamped filenames. Override parameters inline, such as `uv run artctl run spiral --set turns=40 radius=250`.

## Project Layout

- `artctl/` – CLI entry point plus helpers for registry loading, parameter coercion, templating, output management, and subprocess execution.
- `registry/` – YAML descriptors for available generators. Each file documents runtime expectations and parameter metadata.
- `generators/` – Example Python (`spiral.py`) and Node (`night_sky.js`) scripts that emit placeholder PNG assets.
- `tests/` – Pytest suite covering CLI paths, registry validation, templating, output rules, and integration runs.

## Development Workflow

- Format and lint: `uv run ruff check .`
- Tests: `uv run pytest`
- Dry-run a generator to inspect the command without executing it: `uv run artctl run spiral --dry-run`
- Node is optional; if unavailable the `night_sky` example is skipped automatically.

When authoring a new generator, copy an existing YAML file from `registry/`, adjust the runtime, entrypoint, and parameters, then create the corresponding script under `generators/`. Use `{params.<name>}` placeholders anywhere a parameter should be substituted, and rely on the built-in output manager rather than hard-coding paths.
