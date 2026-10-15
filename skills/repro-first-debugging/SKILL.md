---
name: repro-first-debugging
description: Disciplined empirical bug isolation and repair protocol. Enforces authoring a minimal reproduction script before modifying any production code.
---

# Reproduce Before Repair (Empirical Bug Isolation)

## 1. Protocol Workflow
1. **Formulate Minimal Reproduction**: Write an isolated test script (`repro.py` or test case) asserting the expected behavior.
2. **Execute & Observe Failure**: Run the script and record the exact failure traceback, exit code, and error signature.
3. **Apply Targeted Surgical Fix**: Modify production code following the Ponytail YAGNI ladder.
4. **Re-Run Reproduction**: Confirm the reproduction check now passes with exit code 0.
5. **Run Full Regression Suite**: Verify zero collateral regressions in unrelated modules.

## 2. Hard Anti-Patterns
- ❌ Modifying production code based on an unverified visual guess.
- ❌ Weakening assertions in an existing test to make it pass.
- ❌ Swallowing exceptions (`except Exception: pass`) to hide symptoms.
