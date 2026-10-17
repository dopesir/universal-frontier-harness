# Architecture & Operational Invariants

The Universal Frontier Harness enforces deterministic, reproducible behavior on autonomous AI coding agents through a dual-layer design: **Lean System Prompt Invariants** paired with **Zero-Bypass Mechanical Runtime Hooks**.

---

## 1. The Dual-Layer Architecture

```
                               ┌─────────────────────────┐
                               │       AI PLANNER        │
                               └────────────┬────────────┘
                                            │ Tool Intent
                                            ▼
                               ┌─────────────────────────┐
                               │ 1. PRE-TOOL HOOK        │
                               │ • Read-before-write     │
                               │ • Scope fencing         │
                               │ • Circuit breaker       │
                               └────────────┬────────────┘
                                            │ Approved
                                            ▼
                               ┌─────────────────────────┐
                               │ 2. POST-TOOL HOOK       │
                               │ • Fast AST syntax lint  │
                               │ • Evidence ledger append│
                               │ • Mutation timestamping │
                               └────────────┬────────────┘
                                            │ Agent proposes "DONE"
                                            ▼
                               ┌─────────────────────────┐
                               │ 3. STOP GATE            │
                               │ • Fresh evidence check  │
                               │ • Task ID verification  │
                               │ • Fail-closed gate      │
                               └─────────────────────────┘
```

---

## 2. The 6 Non-Negotiable Invariants

1. **Reconnaissance Before Mutation (Read-Before-Write)**:
   - The agent cannot edit or write to an existing file without first viewing/reading it in the active session.
   - Enforced mechanically by `pre_tool.py` against `session/reads.jsonl`.
2. **Reproduce Before Repair**:
   - Before modifying production code to fix a defect, author a standalone, runnable reproduction test that fails.
3. **Surgical Diff Principle**:
   - Make the smallest viable AST perturbation. Never rewrite entire classes or functions when a 3-line guard clause suffices.
4. **Evidence-First Completion**:
   - Completion claims without executed test exit codes (`exit_code == 0`) and empirical proof are void.
   - Self-reported text claiming "All tests pass" is rejected by `stop_gate.py`.
5. **Circuit Breakers**:
   - If an action or command fails **twice** with the same fingerprint, execution halts immediately and forces diagnosis mode.
6. **Caller & Invariant Preservation**:
   - Never break public API signatures, delete comments/docstrings, or weaken existing tests to force a build to pass.

---

## 3. The Task Lifecycle Finite State Machine (FSM)

Tasks progress strictly through ordered state transitions:

```
[ UNINITIALIZED ]
       │
       ▼ (Read & Reconnaissance)
  [ GROUNDED ]
       │
       ▼ (Formal Plan & Contract)
  [ PLANNED ]
       │
       ▼ (Surgical Patch)
  [ MUTATING ]
       │
       ▼ (Test Execution)
 [ VALIDATING ]
       │
       ▼ (Stop Gate Verified)
 [ COMPLETED ]
```

Direct jumps from `UNINITIALIZED` to `MUTATING` fail closed.

---

## 4. The Ponytail YAGNI Ladder

When adding or modifying logic, agents stop at the first rung that holds:

1. **Does this need to exist at all?** (YAGNI — if speculative or decorative, delete it).
2. **Can stdlib/native platform features cover it?** (Reach for standard library before custom abstractions).
3. **Does an already-installed dependency solve it?** (Never add a library for what existing packages do).
4. **Can it be one line?** (One line).
5. **Only then**: Write the minimum code that satisfies the test.
