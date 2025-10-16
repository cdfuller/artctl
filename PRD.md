# Product Requirements Document (PRD) — `artctl`

**Summary:** A CLI for running generative art programs via a YAML-defined registry.

---

## 1. Overview

### Problem Statement
Managing multiple generative art programs—each with different parameters, inputs, and runtimes—is cumbersome. Running them manually or maintaining separate scripts per project limits experimentation and scalability. There’s no unified interface for discovering, configuring, and executing creative code across languages.

### Proposed Solution
`artctl` provides a consistent command-line interface to register, list, and execute generative art programs. Each generator is described by a YAML file specifying its runtime (Python, Node/p5.js, binaries), entrypoint, and configurable parameters. The MVP focuses on manual execution and structured output directories without any scheduling or orchestration.

### Value Proposition
- Enables cross-language consistency for creative coders.  
- Simplifies running and managing multiple art generators.  
- Encourages reproducibility through declarative YAML definitions.  
- Lays groundwork for future automation and galleries.

---

## 2. Goals

- Provide a **single, unified CLI** for running generative art programs.  
- Support **multi-runtime execution** (Python, Node/p5.js, binaries).
- Use **YAML-based registries** for configuration and parameter discovery.  
- Organize outputs in timestamped directories (`outputs/YYYY/MM/DD/`).  
- Offer clear **CLI commands** for listing, running, and inspecting programs.  
- Keep the MVP **local, offline, and dependency-light**.  
- Focus on developer ergonomics and clarity of structure.

---

## 3. Non-Goals

- No web dashboard or GUI in MVP.  
- No scheduling, automation, or orchestration.  
- No deployment features.  
- No persistent database for run history.  
- No parameter sweeps, plugin discovery, or cloud execution yet.  
- No API server or networked components.

---

## 4. Core Features

| Feature | Description |
|----------|-------------|
| **Program Registry** | YAML files in `/registry/` define available generators, including runtime, entrypoint, parameters, and command template. |
| **Listing Programs** | `artctl list` shows all registered generators with short descriptions. |
| **Run Command** | `artctl run &lt;program&gt;` executes a generator with optional parameter overrides. |
| **Help Command** | `artctl help &lt;program&gt;` displays available parameters and default values from the YAML registry. |
| **Output Management** | Outputs automatically stored in timestamped subdirectories. |
| **Console Feedback** | Print concise execution status (command run, success/failure, output path). |
| **Multi-language Support** | Each YAML entry defines how to execute its generator (e.g., `python3`, `node`, or `./binary`). |

---

## 5. Functional Requirements

1. **Registry Parsing**
   - `artctl` must read YAML registry files from a `/registry/` directory.
   - Each file defines:
     - `name` (unique string)
     - `runtime`
     - `entrypoint`
     - `command` (templated)
     - `params` (list of name/type/default)
     - `tags` (optional)

2. **Execution**
   - Build shell commands dynamically from the registry’s command template.
   - Inject parameter overrides from CLI arguments.
   - Execute via subprocess while printing real-time feedback.
   - Return exit code and status.

3. **CLI Commands**
   - `artctl list` → display all available registry names.
   - `artctl run &lt;program&gt; [--set key=value]` → run generator.
   - `artctl help &lt;program&gt;` → print registry parameter info.

4. **Output Handling**
   - Each run writes to a dated directory (`outputs/YYYY/MM/DD/`).
   - Generated outputs (images, videos, data) are stored inside it.
   - Standardize output filenames where possible (`program.png` by default).

5. **Error Handling**
   - Catch missing registry, missing entrypoint, or invalid parameters.
   - Print human-readable errors; no log files in MVP.

---

## 6. User Experience (CLI Flow)

Example session:

```bash
$ artctl list
- spiral
- night_sky
- gradient_fields

$ artctl help spiral
Name: spiral
Runtime: python
Entrypoint: generators/spiral.py
Parameters:
  - turns (int, default=20)
  - radius (int, default=400)

$ artctl run spiral --set turns=50 radius=250
▶ Running spiral...
   Command: python3 generators/spiral.py --turns 50 --radius 250 --output outputs/2025/10/16/spiral.png
✅ Output saved to outputs/2025/10/16/spiral.png
```

---

## 7. Acceptance Criteria

- ✅ `artctl list` successfully enumerates all registry YAMLs.  
- ✅ `artctl run` executes a Python or Node generator correctly.  
- ✅ `artctl help` outputs all parameter details from the YAML.  
- ✅ Output directory structure follows `outputs/YYYY/MM/DD/`.  
- ✅ Errors (missing file, invalid parameter, bad command) print clearly to console.  
- ✅ No internet or database required.  
- ✅ CLI runs on macOS and Linux.

---

## 8. Future Extensions (Post-MVP)

- Scheduling (`--hourly`, `--daily`) and orchestration as optional add-ons.  
- Output metadata tracking (JSON logs, thumbnails, hashes).  
- Containerized generators (Docker per runtime).  
- Plugin interface for new runtimes (Rust, Go, GLSL).  
- Integration with art gallery web dashboards.  
- Parameter sweeps and automated composition generation.
