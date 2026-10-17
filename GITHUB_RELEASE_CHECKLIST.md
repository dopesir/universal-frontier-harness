# GITHUB RELEASE CHECKLIST — Universal Frontier Harness (v7.1.0)

**Release Target**: v7.1.0 (Graph-Aware Dependency Intelligence & Blast-Radius Engine)  
**Status**: PREPARED & VALIDATED LOCALLY — Awaiting Maintainer Approval to Tag and Push  

---

## 1. Acceptance Criteria Verification

- [x] **Phase 0 Baseline Complete**: Recorded in `AUDIT_BASELINE.md`.
- [x] **Safe Installation**: Hardened `scripts/init_harness.py` with `--dry-run`, `--overwrite`, and automated `.bak` archives.
- [x] **Complete Runtime Installation**: Installs `.agents/rules/`, `.agents/core/`, and `.agents/hooks/`.
- [x] **Hook Path Resolution**: Verified across both root and `.agents` layouts, with space-tolerant path resolution.
- [x] **Evidence Rigor**: Type-checked integer exit codes (`0`), boolean `passed`, non-empty commands, and task isolation verified.
- [x] **Fail-Closed Contract**: Corrupted `contract.json` fails closed with explicit diagnostic deficits.
- [x] **Language Validation Transparency**: Honest reporting of AST vs full JSON parse vs delimiter balance.
- [x] **Reproducible Test Suite**: 44 tests executed and passing cleanly (0 failures, 0 blocked).
- [x] **CI Alignment**: GitHub Actions matrix configured for Ubuntu, Windows, macOS on Python 3.10–3.13.
- [x] **Badges & URLs Verified**: Corrected all badge URLs and clone links to `github.com/dopesir/universal-frontier-harness`.
- [x] **Security & Contributing**: `SECURITY.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, and issue/PR templates created.
- [x] **Controlled Benchmarking**: Authoring `BENCHMARK_PROTOCOL.md` to prevent unsubstantiated marketing claims.

---

## 2. GitHub Metadata Recommendations

- **Repository Description**:  
  `An open-source, model-agnostic reliability kernel for AI coding agents with mechanical stop gates, sub-15ms AST linting, and policy enforcement.`
- **Topics**:  
  `ai-agents`, `agentic-coding`, `developer-tools`, `software-engineering`, `python`, `verification`, `reliability`
- **License**: MIT
- **Default Branch**: `main`

---

## 3. Release Artifacts & Checksums

When tagged and published, the release archive should include:
- `universal-frontier-harness-7.0.1.zip`
- `universal-frontier-harness-7.0.1.tar.gz`
- Checksums published in release notes (`sha256sum`).

---

## 4. Release Commands (For Maintainer Authorization)

To tag and push the hardened release to GitHub:
```bash
git add .
git commit -m "chore(release): v7.0.1 hardening, evidence safety, and documentation suite"
git tag -a v7.0.1 -m "Release v7.0.1: Hardened installer, fail-closed evidence gates, and 44 reproducible tests"
git push origin main
git push origin v7.0.1
```
*(Per Rule 13: Awaiting explicit maintainer authorization before executing git push or tag creation).*
