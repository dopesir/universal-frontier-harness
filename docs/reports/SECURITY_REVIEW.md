# SECURITY AND SUPPLY CHAIN REVIEW — Universal Frontier Harness (v7.0)

**Date**: 2026-10-17  
**Auditor**: Senior Systems & Security Reviewer  
**Status**: AUDITED & COMPLIANT  

---

## 1. Third-Party Dependencies & Supply Chain Risk

- **Total Third-Party Runtime Dependencies**: **0**
- **Standard Library Only**: The entire runtime (`core/`, `hooks/`, `scripts/`) executes strictly on Python standard library modules (`ast`, `json`, `os`, `sys`, `pathlib`, `shutil`, `datetime`, `subprocess`, `unittest`, `argparse`).
- **Supply Chain Vulnerability Surface**: Effectively zero external package hijacking or dependency confusion vectors.
- **Setuptools Requirement**: Build system specifies `setuptools>=61.0` in `pyproject.toml` for standard PEP 517/621 packaging.

---

## 2. Process Execution & Subprocess Security

- **Subprocess Invocations in Core**: Core runtime modules (`core/`) contain **zero** `subprocess` or `os.system` execution calls.
- **Hook Scripts**:
  - `pre_tool.py`, `post_tool.py`, and `stop_gate.py` execute as passive evaluation scripts. They do not spawn shell processes.
- **Integration Tests**:
  - `tests/test_installation.py` invokes `subprocess.run` exclusively with `sys.executable` (current Python interpreter) targeting local scripts with `shell=False`.
  - Stdin is explicitly isolated via `stdin=subprocess.DEVNULL` or explicit JSON strings to prevent pipe deadlocks.

---

## 3. Data Storage & Privacy Audit

- **Data Storage Location**: All runtime state is strictly confined to `.agents/sessions/<conversation_id>/` within the active project root.
- **Data Retention**:
  - `reads.jsonl`: Local file paths inspected during the session.
  - `mutations.jsonl`: Local file paths modified and UTC timestamps.
  - `evidence.jsonl`: Test commands executed, integer exit codes, and timestamps.
  - `failures.jsonl`: Action fingerprints and error messages to feed circuit breakers.
- **No Secrets Extraction**: The harness does not capture environment variables, authorization headers, or private keys.
- **Zero Telemetry**: No network sockets, HTTP requests, or external telemetry pings exist in the codebase.

---

## 4. Filesystem Boundaries & Permissions

- **Scope Fencing**: `core.policy.evaluate_action` enforces `allowed_write_scope`. Any mutation targeted outside the allowed scope is denied.
- **Path Traversal Protection**: Paths are resolved using `Path(p).resolve()`. Normalization prevents directory traversal attacks via `..` segments.
- **Space and Special Character Handling**: All path manipulations use `pathlib.Path` objects rather than raw string concatenation.

---

## 5. Security Conclusions

The Universal Frontier Harness adheres to the highest tier of local-first, zero-telemetry software security principles. No vulnerabilities or privilege escalation vectors were identified during this audit.
