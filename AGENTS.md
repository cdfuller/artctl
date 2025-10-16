# Repository Guidelines

## Project Structure & Module Organization
- Top-level package `artctl/` holds CLI modules: `cli.py`, `registry.py`, `params.py`, `templater.py`, and `runner.py`. Keep new functionality within this namespace unless it is generator-specific.
- YAML registry definitions live in `registry/`, example generators in `generators/`, and rendered assets in `outputs/`. Avoid committing artefacts under `outputs/`.
- Tests should mirror module layout inside `tests/` (e.g., `tests/test_registry.py` for `artctl/registry.py`).

## Build, Test, and Development Commands
- `uv sync` — install dependencies into the managed environment based on `pyproject.toml` and `uv.lock`.
- `uv run artctl --help` — verify CLI wiring after code changes.
- `uv run pytest` — execute the full automated test suite.
- `uv run ruff check .` — lint Python sources and tests; run before submitting changes.

## Coding Style & Naming Conventions
- Python 3.13, 4-space indentation, `snake_case` for functions/variables, `PascalCase` for classes, and `UPPER_SNAKE_CASE` constants.
- Keep modules small and composable; prefer pure functions in `params.py` and `templater.py` to simplify testing.
- Use f-strings for string interpolation and log messages that match CLI tone from the PRD (concise, emoji-friendly when user-facing).

## Testing Guidelines
- Use `pytest` with descriptive test names like `test_parse_registry_missing_entrypoint`.
- Favour fixtures under `tests/conftest.py` for registry samples and temporary directories.
- When adding new CLI flows, include at least one integration-style test using `uv run python -m artctl.cli` via `subprocess` to validate exit codes.

## Commit & Pull Request Guidelines
- Commit messages: single line, imperative verb, no prefixes (e.g., `Add registry schema validator`, `Update runner output verification`). Describe every file touched.
- Pull requests should include: brief summary, linked issue (if applicable), verification commands run, and any new registry examples. Attach screenshots only when output behaviour changes visibly.

## Security & Configuration Tips
- Treat `.env` or credential-like files as read-only; never bake secrets into YAML registries.
- Document any environment variables needed for generators in their YAML `help` fields instead of hardcoding values.
