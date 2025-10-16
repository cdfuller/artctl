# Technical Specification Document (TSD) — `artctl`

---

## 1. Purpose & Scope
`artctl` is a command-line runner that orchestrates generative art programs defined through declarative YAML registry files. The MVP scope is local execution on macOS and Linux, without network services or scheduling features. This specification targets contributors implementing the CLI, registry parser, parameter handling, command templating, and subprocess runner.

## 2. Registry Schema
The registry describes each available generator. Files live in `registry/*.yaml` and may be grouped by subdirectories.

### 2.1 Top-Level Shape
Each YAML document must contain the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Unique identifier used by `artctl` commands. |
| `description` | string | yes | Short human-readable summary shown in `list`/`help`. |
| `runtime` | enum | yes | Execution environment label (`python`, `node`, `binary`, `custom`). |
| `entrypoint` | string | yes | Path to the executable file, relative to project root unless absolute. |
| `command` | sequence[string] | yes | Argument vector template; may include placeholders (§5). |
| `params` | sequence[object] | optional | Parameter definitions consumed by `--set`. |
| `output` | object | optional | Output expectations (§7). |
| `tags` | sequence[string] | optional | Free-form categorization for future filtering. |

Unknown top-level keys raise validation errors.

### 2.2 Parameter Definitions
Each element of `params` must include:

- `name` (string, kebab- or snake-case)  
- `type` (one of `string`, `int`, `float`, `bool`, `enum`, `file`, `dir`)  
- `default` (optional; type-dependent)  
- `choices` (required when `type == enum`)  
- `help` (optional, displayed in `help <program>`)  
- `required` (bool; defaults to `false`)

Parameter names must be unique per registry file. Boolean parameters treat `default: true` as implying the flag is passed unless explicitly overridden to false.

### 2.3 Output Block
`output` is optional and supports:

- `required` (bool; default `false`) — whether the runner should verify existence after execution.  
- `path_template` (string) — override for default `outputs/{date}/{name}.{ext}`. Supports placeholders from §5.  
- `extension` (string) — default file suffix when `path_template` omitted.

### 2.4 Validation Rules
- Duplicate `name` values across registry files are rejected during load.  
- Files must parse as valid YAML (single document).  
- `command` entries must be strings; empty arrays are invalid.  
- `entrypoint` must exist on disk when the program is executed; missing files surface as runtime errors (§8).  
- When `runtime == python` or `node`, the first `command` token should reference the interpreter binary (e.g., `python3`, `node`).

## 3. Parameter Coercion
- CLI overrides arrive via `--set key=value` pairs. Multiple `--set` flags are allowed.  
- Unknown parameters trigger exit code 2 (§4.3).  
- Type coercion rules: `int` → `int(value)`, `float` → `float(value)`, `bool` accepts `true/false/1/0`, `enum` matches `choices`, `file`/`dir` pass through but may be validated for existence post-run if `validate_path` future flag is added.  
- When the same key appears multiple times, the last value wins (documented behavior).  
- Required parameters without defaults must be provided via CLI; otherwise exit code 2 with descriptive message.

## 4. CLI Behavior
### 4.1 Commands
- `artctl list` — prints generator names with descriptions.  
- `artctl help <program>` — shows metadata, parameter table, and command template preview.  
- `artctl run <program> [--set key=value ...] [--dry-run]` — resolves parameters, constructs output path, and executes the generator.  
- Global flags: `--registry-path` (override default path), `--version`, `--verbose`.

### 4.2 Console Output
- Use concise, emoji-prefixed status lines for success/failure as in PRD examples.  
- Under `--verbose`, echo resolved argv and environment variables used.  
- Errors provide actionable remediation steps (e.g., “Parameter `turns` expects an integer. Received `abc`.").

### 4.3 Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Success. |
| 1 | Unhandled exception or internal bug (stack trace logged when `--verbose`). |
| 2 | User/validation error (unknown program, bad parameter, missing required argument). |
| 3 | Generator process failed (non-zero exit status). |
| 4 | Output verification failed (required artifact missing). |

## 5. Command Templating
- Placeholder tokens follow `{placeholder}` syntax inside `command` array elements.  
- Supported placeholders: `{project_root}`, `{entrypoint}`, `{name}`, `{output}`, `{params}`, and `{params.<param_name>}` for direct substitution of a single value.  
- `{params}` expands into `["--<param>", "<value>", ...]` preserving registry order. Boolean params only emit the flag when `True`.  
- Templates are resolved prior to execution; no shell interpolation is performed.  
- Additional fields (e.g., environment variables) may be injected later but must be documented here when added.

## 6. Execution Pipeline
1. Parse CLI arguments with `argparse`.  
2. Load registry metadata (cached per invocation).  
3. Coerce parameters and construct output path.  
4. Render final argv.  
5. Run subprocess via `subprocess.run(..., shell=False, cwd=project root)`.  
6. Stream stdout/stderr to console.  
7. Inspect exit code and perform output checks.  
8. Return mapped exit code to caller.

## 7. Output Management
- Default pattern: `outputs/YYYY/MM/DD/<program>[-HHMMSS].<ext>` (ext defaults to `png`).  
- Directories are created lazily before invocation.  
- When `output.required` is true, runner validates file existence after subprocess returns; absence triggers exit code 4 with expected path.  
- Future enhancements (metadata JSON, thumbnails) will extend this section.

## 8. Error Handling & Messaging
- Registry load errors halt execution prior to running commands.  
- CLI parameter issues raise `ValueError`-style exceptions converted into exit code 2 with friendly output.  
- Subprocess failures include command echo, exit status, and truncated stderr preview (first 20 lines).  
- Unexpected exceptions bubble up with stack trace only when `--verbose` is active; otherwise a succinct message plus remediation hint.

## 9. Examples
### 9.1 Example Registry Entry
```yaml
name: spiral
description: Generates a spiral PNG using matplotlib.
runtime: python
entrypoint: generators/spiral.py
command:
  - python3
  - {entrypoint}
  - --turns
  - "{params.turns}"
  - --radius
  - "{params.radius}"
  - --output
  - {output}
params:
  - name: turns
    type: int
    default: 20
    help: Number of rotations to render.
  - name: radius
    type: int
    default: 400
    help: Spiral radius in pixels.
output:
  required: true
  extension: png
tags:
  - python
  - example
```

### 9.2 Example CLI Invocation
```
$ uv run artctl run spiral --set turns=50 radius=250
▶ Running spiral...
   Command: python3 generators/spiral.py --turns 50 --radius 250 --output outputs/2025/10/16/spiral.png
✅ Output saved to outputs/2025/10/16/spiral.png
```

## 10. Implementation Notes (MVP)
- Language: **Python 3.13+**.  
- **Project & dependency manager: `uv`** (fast installs, lockfile, venv management).  
- Runtime dependencies: **PyYAML** for registry parsing; standard library otherwise.  
- Packaging: PEP 621 via **`pyproject.toml`** with a console entry point.  
- Layout: **top-level package directory** (no `src/`).

**Project layout:**
```
artctl/
├─ pyproject.toml
├─ artctl/
│  ├─ __init__.py
│  ├─ cli.py               # argparse and subcommand dispatch
│  ├─ registry.py          # YAML loading & validation
│  ├─ params.py            # --set parsing & coercion
│  ├─ templater.py         # placeholder resolution & argv assembly
│  └─ runner.py            # subprocess execution & output checks
├─ registry/                  # YAML program definitions
├─ generators/                # user/author scripts (unopinionated)
├─ outputs/                   # generated outputs
└─ README.md
```

**Console script:** expose `artctl` via `project.scripts` → `artctl = "artctl.cli:main"` in `pyproject.toml`.

**Common `uv` workflows (MVP):**
- Create/initialize and install deps: `uv init` (once), then `uv add pyyaml`.  
- Sync environment (create `.venv` from lockfile): `uv sync`.  
- Run the CLI without activating venv: `uv run artctl list` (or `uv run python -m artctl.cli list`).  
- Add dev tools: `uv add --dev pytest ruff`.  
- Lock upgrades: `uv lock --upgrade` (all) or `uv lock --upgrade-package <name>`.

(See §14 for full `pyproject.toml` example and `uv` commands.)

## 11. Testing Strategy
- Unit tests for `registry.py`, `params.py`, and `templater.py` to cover schema validation, coercion, and placeholder expansion.  
- Integration test invoking `artctl run` against a sample generator using `uv run` with fixtures stored in `tests/data`.  
- Use `pytest` with temporary directories to validate output management logic.  
- Mock subprocess in unit tests; reserve real generator execution for dedicated integration cases.

## 12. Security & Secrets
- Registry files must not embed secrets; rely on environment variables passed at runtime when needed.  
- CLI should refuse to echo environment variable values when printing commands.  
- Future secret management (e.g., `.env`) must update this section with handling guidelines.

## 13. Limitations & Future Considerations
- No Windows support in MVP.  
- No scheduling or remote execution.  
- Assumes user-installed runtimes (Python, Node, etc.) are available on PATH.  
- Large binary outputs may require streaming optimizations later.

## 14. Project Management with `uv`

### 14.1 `pyproject.toml`
```toml
[project]
name = "artctl"
version = "0.1.0"
description = "CLI for running generative art via a YAML registry"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
  "PyYAML>=6.0"
]

[project.scripts]
artctl = "artctl.cli:main"

[build-system]
requires = ["hatchling>=1.26"]
build-backend = "hatchling.build"

# Local-only development groups (synced by default)
[dependency-groups]
dev = [
  "pytest>=8",
  "ruff>=0.5"
]

[tool.uv]
# Include the dev group by default when running `uv run` / `uv sync`.
default-groups = ["dev"]
```

### 14.2 Typical commands
- **Create project scaffolding** (once):
  - `uv init` (adds a minimal `pyproject.toml`)
  - Optionally install a specific Python: `uv python install 3.13`
- **Add dependencies:** `uv add pyyaml`
- **Add dev dependencies:** `uv add --dev pytest ruff`
- **Install/sync:** `uv sync` (creates `.venv`, writes/updates `uv.lock`)
- **Run the CLI:** `uv run artctl list`
- **Upgrade locks:** `uv lock --upgrade` or `uv lock --upgrade-package PyYAML`
- **Generate a `requirements.txt` (optional interop):** `uv pip compile pyproject.toml -o requirements.txt`

Notes:
- The `dev` group is synced by default; customize via `[tool.uv].default-groups`.  
- `uv run` uses the lockfile to ensure a consistent environment for commands.
