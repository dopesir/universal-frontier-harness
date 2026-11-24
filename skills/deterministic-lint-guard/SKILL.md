---
name: deterministic-lint-guard
description: >-
  Immediate deterministic syntax and lint verification (SWE-agent / Codacy pattern).
  Validates that modified files have valid AST syntax and balanced delimiters before
  running full test suites or declaring tasks complete.
---

# Deterministic Lint Guardrail

The **Deterministic Lint Guardrail** provides an unyielding, model-agnostic quality floor.
It catches syntax errors, unclosed brackets, missing colons, and broken imports immediately
after an edit, preventing the agent from wasting turns diagnosing basic syntax failures.

---

## When to Use

- Immediately after applying an edit with `replace_file_content` or `write_to_file`.
- Before running complex test suites or build commands.
- Before declaring a task complete.

---

## How to Run

Execute the bundled lint guard script on any modified file:

```bash
# Verify a Python file:
python .agents/plugins/universal-harness/scripts/lint_guard.py path/to/file.py

# Verify a TypeScript / JavaScript file:
python .agents/plugins/universal-harness/scripts/lint_guard.py path/to/file.ts
```

---

## Output Behavior

- **Exit code 0 (`[LINT GUARD PASS]`)**: Syntax and delimiters are valid. Proceed to tests.
- **Exit code 1 (`[LINT GUARD FAIL]`)**: Syntax error or unclosed delimiter detected.
  The exact line and offset are reported so the agent can immediately correct the edit.
