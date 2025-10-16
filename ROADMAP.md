

# Implementation Roadmap — `artctl`

**Status:** MVP scope (CLI-only, local)

**Principles:** small steps, working CLI at every stage, no dates, no external services.

---

## Milestones (ordered)

### M0. Repo Bootstrap & Housekeeping
**Goal:** Prepare a clean Python project managed by `uv`.
- Create repo with top-level package layout (no `src/`).
- Add `.gitignore` (Python, macOS, Node, editor files; include `.venv`, `outputs/`, `uv.lock`).
- Add `pyproject.toml` (PEP 621) per TSD §14; set console script `artctl = "artctl.cli:main"`.
- Create package skeleton: `artctl/__init__.py`, `artctl/cli.py`, `artctl/registry.py`, `artctl/params.py`, `artctl/templater.py`, `artctl/runner.py`.
- Create folders: `registry/`, `generators/`, `outputs/`.
- Initialize `uv` environment: `uv sync`.
**Definition of Done (DoD):** `uv run artctl --help` shows CLI usage stub.

### M1. CLI Skeleton & Subcommand Wiring
**Goal:** Establish CLI grammar and command dispatch.
- Implement argparse for `list`, `help <program>`, `run <program> [--set ...]`.
- Centralize exit codes (0/1/2/3/4 per TSD §4.3).
**DoD:** Commands print placeholder output without touching filesystem.

### M2. Registry Loader (YAML) & Validation
**Goal:** Load program definitions from `registry/*.yaml`.
- Implement schema fields and validation per TSD §2.
- Normalize paths relative to project root.
- Surface helpful errors (unknown program, invalid YAML, duplicate params).
**DoD:** `artctl list` enumerates names from YAML files; `artctl help <program>` prints structured info.

### M3. Parameter Parsing & Coercion
**Goal:** Convert `--set key=value` into typed param values.
- Support types: string, int, float, bool (flag style), enum, file, dir.
- Enforce unknown/duplicate overrides as errors; maintain declaration order.
**DoD:** `artctl help <program>` shows defaults/required; invalid overrides exit with code 1 and a clear message.

### M4. Command Templating
**Goal:** Expand registry `command` arrays with placeholders and params.
- Implement placeholders: `{project_root}`, `{entrypoint}`, `{output}`, `{name}`, `{params}`.
- Render `--<name> <value>` flags; `bool` flags as `--flag` when true.
**DoD:** Dry-run output prints fully expanded argv for inspection.

### M5. Output Manager
**Goal:** Standardize output paths and verify when required.
- Create dated path `outputs/YYYY/MM/DD/`.
- Default filename `{name}.{ext}` with de-dup suffix `-HHMMSS` when needed.
- Add `output.required` verification (exit code 4 if missing).
**DoD:** `artctl run <program>` prints final output path and creates directories.

### M6. Runner (Subprocess Execution)
**Goal:** Execute generators reliably without shell interpolation.
- Use `subprocess.run(argv, shell=False)`; working dir = project root.
- Stream stdout/stderr; return non-zero child codes as exit 3 with context.
**DoD:** Successful run returns 0; failure returns 3 with the command shown.

### M7. End-to-End Happy Path (Python Example)
**Goal:** Prove the pipeline with a minimal Python generator.
- Add `registry/spiral.yaml` (example from TSD §9.1).
- Add `generators/spiral.py` (writes an image to `--output`).
- Run: `uv run artctl run spiral --set turns=5` → image written.
**DoD:** Output file exists in the dated directory; exit 0; help/list accurate.

### M8. Cross-Runtime Check (Node/p5.js Example)
**Goal:** Verify multi-language support locally.
- Add `registry/night_sky.yaml` and a minimal Node script.
- Skip test on machines without Node (document skip behavior).
**DoD:** When Node is present, `artctl run night_sky` writes output; otherwise `help` still works.

### M9. Errors & Edge Cases
**Goal:** Tighten ergonomics and predictable behavior.
- Unknown program / missing entrypoint / bad type → friendly messages.
- Required output missing → exit 4 with expected path.
- Multiple overrides for same key → last wins (documented).
**DoD:** Manual tests cover these cases; exit codes match TSD.

### M10. Developer Experience Polish
**Goal:** Make it pleasant to develop and use.
- Add `ruff` and `pytest` (already in dev group) and basic config in `pyproject.toml`.
- Write a concise `README.md` with quickstart and examples.
- Add example YAML templates and comments in `registry/`.
**DoD:** `ruff` passes, tests green, README quickstart works on a fresh clone.

### M11. Packaging & Version Bump 0.1.0
**Goal:** Ship a tagged MVP usable by others.
- Confirm console entry point works after `uv build` (optional) or direct `uv run`.
- Tag `v0.1.0` and note known limitations (no scheduler, no DB, local only).
**DoD:** Clean `git status`; README reflects current behavior; tag created.

---

## Deliverables by Milestone
- **M0:** `.gitignore`, `pyproject.toml`, empty package files/folders.
- **M1–M6:** Implemented modules with CLI, loader, params, templater, runner, outputs.
- **M7–M8:** Example registry + generators (Python, Node).
- **M9:** Documented error matrix and exit codes.
- **M10:** Lint/test config, README, examples.
- **M11:** Tag `v0.1.0`.

---

## Handoff / Next Step
Confirm this roadmap. I’ll proceed to implement **M0** first (repo bootstrap + `.gitignore` + `pyproject.toml` + skeleton package) and then move sequentially. If you'd like any changes to the order or scope, say the word before we start M0.