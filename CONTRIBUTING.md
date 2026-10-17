# Contributing to Universal Frontier Harness

Thank you for your interest in contributing to the Universal Frontier Harness. We welcome contributions that make autonomous coding agents safer, more verifiable, and disciplined.

---

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dopesir/universal-frontier-harness.git
   cd universal-frontier-harness
   ```

2. **Verify prerequisites**:
   - Python 3.10, 3.11, 3.12, or 3.13.
   - Zero external packages required (uses pure Python standard library).

3. **Run the complete test suite (44 tests)**:
   ```bash
   python -m unittest discover tests
   ```

4. **Run the full system integrity verifier**:
   ```bash
   python scripts/verify_harness.py
   ```

---

## Core Contribution Invariants

Every pull request must strictly comply with these engineering rules:

1. **Zero External Runtime Dependencies**:
   - Core runtime modules (`core/`), hook scripts (`hooks/`), and installer scripts (`scripts/`) must rely **strictly** on the Python standard library.
   - Do not add packages to `dependencies` in `pyproject.toml` unless discussed and approved in an RFC issue.
2. **Cross-Platform Portability**:
   - Never use raw path strings with OS-specific slashes (`\` or `/`). Use `pathlib.Path` or `pathlib.PureWindowsPath` / `pathlib.PurePosixPath`.
   - Every file read or write must explicitly pass `encoding="utf-8"`.
3. **Reproduce Before Repair**:
   - When submitting a bug fix, first formulate an automated test in `tests/` that demonstrates the failure.
4. **Surgical Diff Principle**:
   - Keep pull requests focused. Do not combine stylistic refactoring with functional changes.
5. **Caller & Invariant Preservation**:
   - Never break public API signatures in `core/` or weaken tests to force a build to pass.

---

## Pull Request Checklist

Before opening a pull request, ensure:

- [ ] All 44 tests pass locally: `python -m unittest discover tests` (exit code 0).
- [ ] System integrity verifier passes: `python scripts/verify_harness.py`.
- [ ] New functionality includes corresponding unit and/or integration tests.
- [ ] Code follows standard library idioms and preserves type hints (`from __future__ import annotations`).
- [ ] Documentation is updated if behavior or flags change.
