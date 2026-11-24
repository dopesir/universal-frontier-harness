---
name: karpathy-engineering-principles
description: Andrej Karpathy's first-principles operational guidelines for AI coding agents. Enforces Think Before Coding, Simplicity First, Surgical Changes, and Goal-Driven Execution across all engineering workflows.
---

# Karpathy Engineering Principles: First-Principles Senior-SWE Guidelines

> [!IMPORTANT]
> **The 4 Non-Negotiable Tenets**:
> 1. **Think Before Coding**: Read before write; state assumptions; never mutate code blindly.
> 2. **Simplicity First**: Reach for the standard library and native features before adding abstractions or dependencies.
> 3. **Surgical Changes**: Touch only what is strictly necessary. Never reformat, refactor, or alter unrelated code.
> 4. **Goal-Driven Execution**: Claims without empirical evidence and test exit codes are void. Verify everything.

---

## 1. Tenet 1: Think Before Coding (Orientation & Reconnaissance)

- **Always Inspect Before Mutating**:
  Never modify a file without thoroughly reading and understanding its current logic, style, and imports. Mutating an unread file is a catastrophic process failure.
- **State Assumptions Explicitly**:
  If a requirement is ambiguous, identify the simplest viable interpretation, verify caller expectations, and document the architectural reasoning before touching code.
- **Map Blast Radius**:
  Identify all dependents and callers before mutating shared signatures or foundational data structures.

---

## 2. Tenet 2: Simplicity First (The YAGNI Ladder)

When designing or writing code, stop at the first rung that satisfies the requirement:
1. **Does this need to exist at all?** If speculative or premature, delete or skip it.
2. **Can stdlib or native platform features solve it?** Always reach for language built-ins (`json`, `pathlib`, `ast`, `shutil`) before pulling in third-party libraries.
3. **Does an already-installed dependency cover it?** Never add a new package when an existing tool suffices.
4. **Can it be a targeted 3-line function or guard clause?** Keep it compact and direct.
5. **Only then:** write the minimum code required to pass the test.

---

## 3. Tenet 3: Surgical Changes (Zero Drive-By Mutations)

- **Match Existing Style**:
  Respect the repository's indent conventions, naming schemes, comment depth, and architectural patterns.
- **Minimal AST Perturbation**:
  Avoid full-file rewrites. A targeted 3-line guard clause or patched method is superior to rewriting a 200-line class.
- **Zero Drive-By Refactoring**:
  Never "clean up", reformat, or fix unrelated files or lines during a targeted bugfix or feature task.
- **Preserve Comments & Public Contracts**:
  Never delete existing docstrings, explanatory comments, or weaken tests to force a build to pass.

---

## 4. Tenet 4: Goal-Driven Execution (Empirical Verification)

- **Evidence-First Completion**:
  A task is only complete when verified by automated tests, executable assertions, and clean exit codes (`exit code 0`).
- **Reproduce Before Repair**:
  Formulate an isolated, runnable reproduction check that empirically fails before touching any production code.
- **Circuit Breakers**:
  If a command or approach fails twice with the same error, STOP immediately. Shift from execution mode to diagnostic root-cause analysis.
- **Cold Verification**:
  Review diffs with fresh eyes, devoid of producer bias, validating against the original user prompt.
