# AUDIT BASELINE — Universal Frontier Harness (v7.0)

**Date**: 2026-10-17  
**Repository Root**: `C:\Users\Vishnu\OneDrive\Desktop\universal-frontier-harness`  
**Remote URL**: `https://github.com/dopesir/universal-frontier-harness`  
**Active Branch**: `main`  
**Starting Commit SHA**: `b535649281fd8ce2264575208b127c1f43e2c6ee`  
**Current Project Version**: `7.0.0` (declared in `pyproject.toml`)  
**Working Tree Status**: Clean (no uncommitted changes)  

---

## 1. Initial Test Suite Execution Baseline

Command: `python -m unittest discover tests`  
Exit Code: `0`  
Execution Time: `0.038s`  
Total Tests: `16`  
Pass: `16` | Fail: `0` | Blocked: `0`

Command: `python scripts/verify_harness.py`  
Exit Code: `0`  
System Integrity Check: PASS (inside source repository)

---

## 2. Inventory of Inspected Files

- **Metadata & Config**: `pyproject.toml`, `LICENSE`, `.gitignore`, `README.md`, `ACKNOWLEDGMENTS.md`, `CONTRIBUTING.md`
- **CI Workflows**: `.github/workflows/test.yml` (Matrix: Ubuntu, Windows, macOS on Python 3.10, 3.11, 3.12)
- **Runtime Core (`core/`)**: `__init__.py`, `contract.py`, `evidence.py`, `fast_lint.py`, `policy.py`, `state_machine.py`, `stop_gate.py`
- **Hooks (`hooks/`)**: `hooks.json`, `pre_invocation.py`, `pre_tool.py`, `post_tool.py`, `stop_gate.py`
- **Adapters (`adapters/`)**: `__init__.py`, `antigravity.py`, `claude_code.py`
- **Rules (`rules/`)**: `AGENTS.md`, `GEMINI.md`
- **Templates (`templates/`)**: `.cursorrules`, `.windsurfrules`
- **Scripts (`scripts/`)**: `init_harness.py`, `verify_harness.py`
- **Evaluation (`eval/`)**: `runner.py`, `tasks/AM-001.json`, `tasks/BF-001.json`
- **Skills (`skills/`)**: `adversarial-review`, `ast-repo-mapper`, `cold-verification`, `engineering-recon`, `live-preview`, `repro-first-debugging`, `subagent-orchestration`

---

## 3. Audit Findings: Confirmed Defects, Suspected Defects & Untested Claims

### A. Confirmed Defects

1. **Installer Incompleteness & Hook Path Disconnect (`scripts/init_harness.py`)**:
   - `init_harness.py` only copied `rules/AGENTS.md`, `rules/GEMINI.md`, `hooks/hooks.json`, and initialized `.agents/memory/`.
   - It did **not** copy the actual executable hook scripts (`pre_tool.py`, `post_tool.py`, `stop_gate.py`, `pre_invocation.py`) or the `core/` runtime modules into the target project.
   - `hooks/hooks.json` specifies `"command": "python hooks/pre_tool.py"`, which looks for `./hooks/` at the target root, whereas `init_harness.py` placed `hooks.json` inside `.agents/hooks/`.
   - Running the installed hooks in an external target project would immediately fail with `FileNotFoundError` or `ModuleNotFoundError: No module named 'core'`.

2. **Unsafe Installation Overwrite (`scripts/init_harness.py`)**:
   - `init_harness.py` unconditionally executes `shutil.copy2` over `target / ".agents" / "AGENTS.md"` and `target / ".agents" / "rules" / "AGENTS.md"`.
   - Any pre-existing user instructions or rules in the target project are destroyed without warning, backup, or confirmation.
   - Missing `--dry-run` flag and missing `--force` / `--overwrite` opt-in.

3. **Broken CI Badge URL (`README.md:3`)**:
   - Badge points to `https://github.com/universal-frontier/universal-frontier-harness/actions/workflows/test.yml/badge.svg` instead of `https://github.com/dopesir/universal-frontier-harness/actions/workflows/test.yml/badge.svg`.

4. **Invalid Packaging Console Scripts (`pyproject.toml:32-33`)**:
   - `serve-preview = "skills.live_preview.scripts.serve_preview:main"` and `repo-map = "skills.ast_repo_mapper.scripts.repo_map:main"` point to hyphenated directory paths (`skills/live-preview` and `skills/ast-repo-mapper`). In Python, hyphens are illegal in import paths, causing `pip install -e .` console scripts to fail with `ModuleNotFoundError`.

### B. Suspected Defects & Semantic Discrepancies

1. **JS/TS Linter Claim vs. Implementation (`core/fast_lint.py`)**:
   - The README claims a "Sub-15ms native AST syntax linter for Python, JS, TS, JSON".
   - In reality, Python uses `ast.parse` and JSON uses `json.loads` (full AST parsing).
   - JS and TS only use `check_delimiter_balance` (bracket and quote pairing). Malformed JavaScript like `const x = = 5;` passes as valid.
   - The validation level must be explicitly returned (`ast_parse` vs `delimiter_balance`) to prevent false security confidence.

2. **Stop Gate Silence on Uninitialized Sessions (`core/stop_gate.py:71-77`)**:
   - If `session_dir` does not exist or has no `contract.json`, `evaluate_stop` returns `{"decision": "allow"}`.
   - While intended for unmanaged runs, in a configured project where an agent failed to create a session, this allows turning off enforcement silently.

### C. Untested Claims & Exaggerations

1. **SWE-Bench Claims**:
   - `pyproject.toml` keywords include `"swe-bench"`.
   - `eval/runner.py` only validates contract JSON syntax; no official SWE-bench evaluation benchmark has been executed or scored for this release.
   - Keywords and documentation must avoid claiming SWE-bench performance numbers until a controlled benchmark is published.

2. **Antigravity Live Runtime Hook Testing**:
   - While `adapters/antigravity.py` exists, testing has been conducted via unit tests and CLI harness tests, not against an active external proprietary Antigravity server daemon.
   - Live compatibility must be honestly categorized as supported via schema adapter, with experimental live-daemon binding.

---

## 4. Prioritized Action Plan

- **Phase 1**: Re-engineer `scripts/init_harness.py` to support `--dry-run`, automatic backup (`.bak`), explicit `--overwrite`, and complete copy of `core/` and `hooks/` with deterministic relative imports. Add comprehensive installation integration tests in disposable temp dirs.
- **Phase 2**: Harden `core/evidence.py`, `core/stop_gate.py`, and hooks against malformed JSON, corrupted timestamps, missing exit codes, and falsified test results.
- **Phase 3**: Refactor `core/fast_lint.py` to explicitly declare `validation_level` and prevent claiming AST parsing for languages that only delimiter-check.
- **Phase 4**: Add complete adversarial test suite (negative tests, malformed evidence, missing dependencies).
- **Phase 5**: Author `BENCHMARK_PROTOCOL.md` defining a controlled evaluation harness.
- **Phase 6**: Update README, fix badges, add `SECURITY.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, and architectural documentation.
- **Phase 7 & 8**: Prepare clean release checklist and open-source growth plan.
