# Universal Frontier Engineering Harness (v7.0)

[![CI](https://github.com/universal-frontier/universal-frontier-harness/actions/workflows/test.yml/badge.svg)](https://github.com/universal-frontier/universal-frontier-harness/actions/workflows/test.yml)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Dependencies: Zero](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)](#zero-dependencies)
[![Platform: Win/Linux/macOS](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blueviolet.svg)](#cross-platform)

**A deterministic reliability runtime and senior-SWE operational framework for autonomous AI coding agents.**

The Universal Frontier Harness eliminates model-specific behavioral divergence, context drift, and premature completion claims by combining **lean, high-attention prompt invariants** with **zero-bypass mechanical runtime hooks**.

---

## Why Purely Textual Prompts Fail

Even frontier LLMs with 1M+ token context windows suffer from structural attention dynamics when loaded with large, passive rule catalogs:

1. **Attention Dilution & Softmax Saturation**: As an agent accumulates file reads and compiler outputs (30k–100k tokens), the softmax attention probability mass assigned to passive rules in the system prompt degrades to under 5%.
2. **Lost-in-the-Middle Effect**: Standard transformers exhibit a U-shaped recall curve. Mid-context instructions are systematically skipped or forgotten.
3. **Autoregressive Self-Conditioning**: When an agent outputs *"The bug is fixed and tests pass"* without running them, that hallucination becomes ground-truth context in subsequent turns.
4. **Unaided Self-Correction Failure**: Prompting an agent to "double check its work" without external mechanical validators results in self-reinforcing rationalizations.

---

## The Dual-Layer Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AI CODING AGENT PLANNER                         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Tool Call Intent
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 1. PRE-TOOL HOOK (Action Gatekeeper)                                   │
│    • Read-Before-Write Enforced (Cannot mutate uninspected files)      │
│    • Scope Fencing (Mutations restricted to declared target scope)     │
│    • Circuit Breaker (Identical failing actions halted on 2nd retry)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Allowed
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. POST-TOOL HOOK (Validator & Evidence Recorder)                      │
│    • Sub-15ms Native AST Syntax Linter (Python, JS, TS, JSON)          │
│    • Append-Only Evidence Ledger (evidence.jsonl)                      │
│    • Mutation Timestamp Logging (Enforces Freshness Guarantees)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Agent Proposes "Done"
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. STOP GATE (Completion Gatekeeper)                                   │
│    • Verifies fresh test evidence exists AFTER latest code mutation    │
│    • Rejects premature turn completion: decision: continue             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## The 6 Non-Negotiable Invariants

1. **Reconnaissance Before Mutation (Read-Before-Write)**: Always inspect existing files before editing. Mutating an unread file is blocked mechanically by `pre_tool.py`.
2. **Reproduce Before Repair**: Never modify production code to fix a defect without first authoring an isolated, runnable reproduction check that empirically fails.
3. **Surgical Diff Principle**: Make the smallest viable AST perturbation. Never rewrite entire classes or files when a targeted 3-line guard clause suffices.
4. **Evidence-First Completion**: Claims without executed test exit codes are rejected. Code that "looks correct" is NOT verified.
5. **Circuit Breakers**: If an action, command, or test fails **twice** with the same error, STOP immediately and switch from execution mode to diagnostic mode.
6. **Caller Invariance**: Never break public API signatures, delete docstrings, or weaken existing tests to force a build to pass.

---

## The Ponytail YAGNI Ladder

When adding or modifying logic, stop at the first rung that holds:

```
1. Does this need to exist at all?
   └── (YAGNI — if speculative or decorative, delete it).
2. Can stdlib/native platform features cover it?
   └── (Reach for built-in libraries before custom abstractions).
3. Does an already-installed dependency solve it?
   └── (Never add a library for what existing packages already do).
4. Can it be one line?
   └── (One line).
5. Only then:
   └── Write the minimum code that satisfies the test.
```

---

## Quickstart & Installation

Install the harness into any target repository in one command:

```bash
python scripts/init_harness.py /path/to/your/project
```

This sets up:
* `.agents/rules/AGENTS.md` (Dense, high-contrast operational kernel)
* `.agents/hooks/hooks.json` (Native hook configuration)
* `.agents/memory/` (Human-readable persistent state tracking)

To verify the harness health and run all 16 self-tests:
```bash
python scripts/verify_harness.py
```

---

## Multi-Agent Delegation Roles (`/subagent-patterns`)

To eliminate cognitive overload and author confirmation bias, high-complexity tasks are distributed across 4 specialized roles:

| Role | Permissions | Primary Responsibility |
| :--- | :--- | :--- |
| **Coordinator (Lead)** | Read / State | Owns contract, task state, and integration. Keeps context lean (<10k tokens). |
| **Researcher** | Read-Only | Absorbs 50k+ tokens of raw file logs and outputs compact 30-line summaries. |
| **Implementer** | Scoped Mutator | Scope-fenced to targeted files; executes surgical diffs under the Ponytail ladder. |
| **Hostile Verifier** | Fresh Context Auditor | Independent audit with zero author bias; attacks code via the 6 Vulnerability Vectors. |

---

## Cross-Platform Engineering & Zero Dependencies

- **Zero Third-Party Dependencies**: The entire core engine, AST linter, evidence ledger, and hook scripts run purely on Python 3.10+ standard library.
- **100% Cross-Platform Hardened**: Native UTF-8 streaming eliminates Windows cp1252 charmap encoding bugs, and `pathlib.Path` resolution normalizes Windows `\` and POSIX `/` separators.

---

## Acknowledgments & Prior Art

We gratefully acknowledge:
* **[Gravitas by Uday Sharma (@udaysharmadev)](https://github.com/udaysharmadev/Gravitas)** for pioneering completion stop gates and rigorous failure mode taxonomies.
* **[SWE-agent (Princeton NLP)](https://github.com/princeton-nlp/SWE-agent)** for the Agent-Computer Interface (ACI).
* Academic research by Yao et al. (ReAct), Wang et al. (Plan-and-Solve), and Dhuliawala et al. (Chain-of-Verification).

---

## License

MIT License. See [LICENSE](LICENSE) for details.
