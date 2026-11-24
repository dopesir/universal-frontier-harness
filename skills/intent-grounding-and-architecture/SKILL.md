---
name: intent-grounding-and-architecture
description: >-
  Framework for deep user intent extraction, architectural problem-solving, and root-cause tracing.
  Use when tasks are ambiguous, conceptually complex, require architectural choices, or when
  debugging recurring system-level defects.
---

# Intent Grounding & Architectural Problem-Solving (Astra & Fable Framework)

Two primary factors degrade agent effectiveness in autonomous engineering:
1. **Misalignment on User Intent**: Solving the literal words of a prompt while missing the core user objective or latent invariants.
2. **Symptomatic Band-Aiding**: Patching symptoms with defensive guards (`try/except: pass`, `if x is None: return`) rather than eliminating root causes.

This skill provides a systematic protocol to guarantee intent alignment and robust algorithmic problem solving.

---

## Part 1: User Intent Triangulation

Before designing or executing any non-trivial solution:

### 1. The 3-Facet Intent Decomposition
Analyze the user request across three facets:
- **Core Objective (The "Why" & "What")**: What is the actual functional capability or defect resolution desired?
- **Latent Invariants (The "Unspoken Rules")**: What must remain true even if unstated?
  - E.g., Zero performance regressions, preservation of public API signatures, matching surrounding visual design, no data loss.
- **Anti-Goals (The "What NOT to do")**: What paths must be avoided?
  - E.g., Do not touch existing database tables, do not add heavy external dependencies, do not rewrite working modules.

### 2. Ambiguity Resolution Protocol
- If a requirement has **low risk and clear industry standard defaults**: Adopt the convention and state the decision clearly in the plan.
- If a requirement has **multiple valid architectural paths with divergent trade-offs**:
  Explicitly outline the options and trade-offs rather than silently picking an arbitrary one.

---

## Part 2: Root-Cause Architectural Problem-Solving

### 1. The "5-Whys" Trace in Code
When encountering an unexpected error or state (e.g. `TypeError: Cannot read properties of undefined`):
- **Level 1 (Symptom)**: Why did it crash? -> Property accessed on `undefined`.
- **Level 2 (Caller)**: Why was it `undefined`? -> The lookup returned no match.
- **Level 3 (Data Flow)**: Why was there no match? -> The key was formatted as an integer instead of string.
- **Level 4 (Producer)**: Why was it formatted as an integer? -> The deserializer didn't cast incoming IDs.
- **Level 5 (Root Cause)**: The API schema contract changed in the upstream payload.

**RULE**: Never fix Level 1 (e.g. `obj?.prop ?? ""` or `try/except`) if the problem is at Level 4 or Level 5. Fix the producer or the transformation boundary.

### 2. State Machine & Invariant Mapping
Model the defect as a state transition:
- **Precondition**: What must be true before this function runs?
- **Invariant**: What must remain true throughout execution?
- **Postcondition**: What must be guaranteed when returning?

Ensure that all error branches cleanly restore invariants (clean up file descriptors, unlock mutexes, reset loading flags).

### 3. Algorithmic & Structural Efficiency
Before finalizing code:
- Check lookup complexity: Replace $O(N)$ repeated list scans with $O(1)$ set/map lookups.
- Avoid memory bloat: Use streams/generators for large sequences instead of full array materialization.
- Minimize AST perturbation: Target only the logical node that requires adjustment.
