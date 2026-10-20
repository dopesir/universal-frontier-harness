# Changelog

All notable changes to the Universal Frontier Harness are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [7.1.1] - 2026-10-20

### Added
- **Harness² Recursive Self-Improvement Engine (`scripts/harness_rsi.py`)**:
  - Implements recursive harness adaptation inspired by Google Cloud AI Research's Harness² framework.
  - Automated context bloat auditing (`--audit`) enforcing a strict $\le 25\text{k}$ token ceiling to eliminate prompt degradation.
  - Trajectory and empirical continual learning recorder (`--log`) targeting `experience.md`.
- **Spatial Multi-Viewport Workbench (`scripts/serve_preview.py`)**:
  - Background HTTP preview daemon hosting a multi-viewport testing suite at `/__spatial__`.
  - Concurrent live rendering across Desktop ($1440\text{px}$), Tablet ($768\text{px}$), and Mobile ($390\text{px}$) viewports.
- **`SLOP-11` Zero-Remote Asset Sandboxing**:
  - Codified into Section 4 of operational kernel rules.
  - Prohibits ungrounded external CDN dependencies; mandates local sandboxing in `assets/`.
- **Awwwards Creative Engineering Laws**:
  - Added formal constraints: Single Motion Verb easing (`cubic-bezier(0.16, 1, 0.3, 1)`), extreme typographic scale contrast ratio ($\ge 7.0$), and negative space void ratio ($35\% - 65\%$).

### Changed
- **Delimiter Linting Resilience (`core/fast_lint.py`)**:
  - Exempted markup and documentation formats (`.md`, `.txt`, `.rst`, `.html`, `.svg`, `.xml`) from delimiter checks to prevent false syntax flags.

---

## [7.1.0] - 2026-10-17

### Added
- **Graph-Aware Intelligence Engine (`core.graph_intel`)**:
  - **Native AST Dependency Extraction**: Real-time dependency graph mapping and caller resolution built entirely on Python standard library `ast` with zero external dependencies.
  - **Graphify Consumer Adapter**: Automatically detects and ingests Graphify output (`graphify-out/graph.json` or `.graphify/graph.json`) when present to augment metrics with multi-language nodes and Louvain communities.
  - **Zero Setup Required**: Explicitly decoupled — users and autonomous agents do **NOT** need to install, configure, or initialize Graphify; the native engine functions out of the box.
  - **Blast-Radius Protection**: Computes risk levels (`NONE`, `LOW`, `MEDIUM`, `HIGH`) and surfaces surgical advisories when an agent attempts to mutate high-blast-radius files (5+ dependents) without inspecting callers.
  - **Strict Blast Radius Mode**: Added `strict-blast-radius` contract mode allowing projects to hard-block uninspected high-blast-radius modifications.
  - **Interactive CLI Diagnostics**: Added `python -m core.graph_intel status`, `blast-radius <file>`, and `dependents <file>` commands (<0.3ms cached latency).
- **Symbol Map Blast Radius Annotations (`skills/ast-repo-mapper`)**:
  - Added `--with-blast-radius` flag to `repo_map.py` to annotate file headers with risk levels and dependent counts directly in the structural symbol tree.
- **Unit Test Coverage**:
  - Added 6 new unit tests in `tests/test_graph_intel.py`, expanding the test suite to 50 automated tests.

---

## [7.0.1] - 2026-10-17

### Added
- **Hardened Project Installer (`scripts/init_harness.py`)**:
  - Added `--dry-run` flag to preview planned operations without modifying files.
  - Added safe-by-default file preservation: existing rules and hooks are skipped unless explicitly authorized.
  - Added automated timestamped backups (`.bak.<timestamp>`) when `--overwrite` is specified.
  - Added `--uninstall` flag to cleanly remove runtime files while strictly preserving `.agents/memory/` and user data.
  - Full runtime distribution: now installs `.agents/rules/`, `.agents/core/` (all 7 core modules), and `.agents/hooks/` (all 4 hook scripts + manifest).
  - Cross-platform support for paths containing spaces.
- **Fail-Closed Contract Enforcement**:
  - `core.contract.load_contract` now raises `ValueError` if a physical contract file is corrupted.
  - `core.stop_gate.evaluate_stop` catches corrupted contracts and fails closed (`decision: "continue"`).
- **Strict Evidence Validation**:
  - `core.evidence.owned_validator_pass` now enforces exact integer `exit_code == 0`, exact boolean `passed is True`, non-empty `command` string, and matches `task_id` against the active contract.
  - Rejects string exit codes, contradictory outputs, and evidence from mismatched tasks.
- **Honest Language Validation Levels**:
  - `core.fast_lint.LintResult` now reports explicit `validation_level`: `"ast_parse"` (Python), `"full_json_parse"` (JSON), and `"delimiter_balance"` (JS/TS).
- **Expanded Test Suite**:
  - Added 28 new tests across `tests/test_installation.py` (9 tests), `tests/test_enforcement_and_evidence.py` (10 tests), and `tests/test_language_validation.py` (9 tests), bringing total test inventory to 44 passing tests.
- **Documentation Suite**:
  - Added `docs/INSTALLATION.md`, `docs/ARCHITECTURE.md`, `docs/COMPATIBILITY.md`, `docs/TROUBLESHOOTING.md`, `SECURITY.md`, and `BENCHMARK_PROTOCOL.md`.

### Fixed
- Fixed CI badge URL in `README.md` to point to `dopesir/universal-frontier-harness`.
- Fixed packaging console scripts in `pyproject.toml` by removing hyphenated import references.
- Fixed hanging on TTY `sys.stdin` in hook scripts (`pre_tool.py`, `post_tool.py`, `stop_gate.py`).
- Fixed hardcoded test count in `scripts/verify_harness.py`.

---

## [7.0.0] - 2026-10-15

### Added
- Initial public release of Universal Frontier Engineering Harness.
- Pure Python standard library implementation with zero external runtime dependencies.
- Sub-15ms fast AST syntax linter and delimiter scanner (`core.fast_lint`).
- Deterministic action policy engine with read-before-write, scope fencing, and circuit breaker (`core.policy`).
- Cryptographic timestamped append-only evidence ledger (`core.evidence`).
- Finite state machine (FSM) enforcing 6 lifecycle stages (`core.state_machine`).
- Mechanical stop gate for turn completion (`core.stop_gate`).
- Multi-agent orchestration roles: Coordinator, Researcher, Implementer, Hostile Verifier.
- Cross-platform CI matrix covering Ubuntu, Windows, and macOS on Python 3.10, 3.11, and 3.12.
