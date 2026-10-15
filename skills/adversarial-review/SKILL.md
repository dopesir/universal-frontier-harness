---
name: adversarial-review
description: Structured adversarial self-review procedure. Challenges completed work against the 6 Vulnerability Vectors before declaring a task complete.
---

# Adversarial Review & Hostile QA Stress Matrix

Before declaring completion on non-trivial work, test the solution against the **6 Vulnerability Vectors**:

1. **Nullability & Emptiness**: What happens if input is `None`, `null`, `[]`, `{}`, `""`, or `0`?
2. **Boundary & Scale**: Does it work with 0 elements, 1 element, 10,000 elements, off-by-one indices?
3. **Type Mismatches**: Does it handle float vs int, string vs bytes, unexpected subclasses?
4. **Failure Paths**: How does it behave on network timeouts, missing files, broken pipes, or permission errors?
5. **State Pollution**: Does running the function multiple times leak memory, mutate shared parameters, or corrupt state?
6. **Caller Invariance**: Did we alter any public method signatures, default arguments, or return types that break callers?

## Evaluation Protocol
Produce an explicit QA table:
| Vector | Stress Case Tested | Observed Behavior | Status |
| :--- | :--- | :--- | :--- |
| Nullability | `input=None` | Handled via early return | PASS |
| Boundary | Empty list `[]` | Returns empty array | PASS |
| Types | String passed to int | Typeguard raises ValueError | PASS |
| Failure | File missing | Caught and logged | PASS |
| State | 100 consecutive calls | Memory constant, no leak | PASS |
| Caller | Public signature | Unchanged | PASS |
