# BENCHMARK PROTOCOL — Universal Frontier Harness (v7.0)

**Document**: Controlled Empirical Evaluation Protocol for AI Coding Agent Harnesses  
**Version**: 1.0.0 (Pilot Phase)  
**Status**: DRAFT / PILOT PROTOCOL  

---

## 1. Objective & Scientific Grounding

This protocol defines a controlled, reproducible methodology for evaluating the impact of the Universal Frontier Harness on autonomous AI coding agents.

> **Methodological Invariant**: Unit test pass rates within this repository verify that the harness functions as engineered; they do **not** serve as empirical proof of improved coding agent problem-solving. True efficacy must be evaluated through controlled task trials.

---

## 2. Experimental Configurations

Every trial evaluates identical task instances under strictly controlled conditions:

| Parameter | Configuration A: Baseline (Vanilla Host) | Configuration B: Harness Enabled (v7.0) |
| :--- | :--- | :--- |
| **Model** | Frozen Model ID (e.g. `claude-3-5-sonnet-20241022`), `temp=0.0` | Identical Model ID, `temp=0.0` |
| **Workspace Snapshot** | Clean git checkout at tagged commit | Identical git checkout at tagged commit |
| **Rules Configuration** | Standard system prompt only | Standard prompt + `.agents/rules/AGENTS.md` |
| **Active Hooks** | None | `pre_tool.py`, `post_tool.py`, `stop_gate.py` |
| **Memory State** | Ephemeral | Persistent `.agents/memory/task_state.md` |
| **Max Turn Budget** | 25 turns | 25 turns |
| **Timeout Budget** | 10 minutes | 10 minutes |

---

## 3. Evaluated Metrics & Definitions

1. **Premature Completion Rate (PCR)**:
   $$\text{PCR} = \frac{\text{Runs declaring turn completion with failing or unexecuted test suites}}{\text{Total Runs}} \times 100\%$$
   *Target with Harness*: $\le 0\%$ (strictly blocked by mechanical stop gate).

2. **Diff Inflation Ratio (DIR)**:
   $$\text{DIR} = \frac{\text{Total Lines Modified by Agent}}{\text{Minimum Viable Diff Lines}}$$
   *Hypothesis*: The Surgical Diff Invariant and read-before-write policy reduce extraneous refactoring and scope creep.

3. **Task Resolution Rate (TRR)**:
   $$\text{TRR} = \frac{\text{Tasks where independently executed test suite exits with code 0}}{\text{Total Tasks}} \times 100\%$$

4. **Runtime Overhead**:
   - Pre-tool policy evaluation latency (target: $< 5\text{ms}$).
   - Post-tool AST linting latency (target: $< 15\text{ms}$).

---

## 4. Frozen Pilot Task Set (10 Calibrated Tasks)

To minimize variance before running large-scale benchmarks, a frozen pilot task set is established:

- **AM-001 (Python)**: Off-by-one boundary index in binary search algorithm.
- **AM-002 (Python)**: Unhandled `NoneType` in nested dictionary config parser.
- **AM-003 (Python)**: Circular import regression during package modularization.
- **AM-004 (JSON/Schema)**: Malformed JSON with trailing commas and unquoted keys.
- **AM-005 (TypeScript)**: Missing type narrowing in union discrimination handler.
- **BF-001 (Refactor)**: 3-line bug fix inside 1,000-line legacy calculator class (tests diff bloat).
- **BF-002 (Regression)**: Guard against public API breaking change on existing method signature.
- **BF-003 (Stale Evidence)**: Agent mutates code after running test and attempts turn completion.
- **BF-004 (Circuit Breaker)**: Agent enters 3-turn repeating loop on missing dependency.
- **BF-005 (Read-Before-Write)**: Agent attempts blind write to uninspected production module.

---

## 5. Execution & Scoring Procedure

1. **Pre-Run Sanitization**: Clean target repository with `git reset --hard && git clean -fdx`.
2. **Execution**: Launch agent CLI or API runner with task description.
3. **Turn Recording**: Stream all tool calls, arguments, stdout, stderr, and timestamps to `run_trajectory.jsonl`.
4. **Independent Grading**:
   - Execute task verification test suite via an external runner independent of the agent.
   - Record exact exit code, stdout, and execution duration.
   - Run `git diff --stat` to measure lines added, deleted, and modified.
5. **Human Review / Audit**: Verify that passing runs solved the actual issue without disabling tests or altering criteria.

---

## 6. Documented Limitations & Anti-Hype Disclaimers

- **Sample Size**: Pilot results on 10 tasks provide directional guidance, not statistically significant benchmark superiority.
- **Model Variance**: Frontier model updates and nondeterminism (even at `temp=0.0`) can cause variance across evaluation dates.
- **Leaderboard Claims**: Universal Frontier Harness does **not** claim official SWE-bench Verified leaderboard rankings until an official, independent third-party evaluation submission is conducted and published.
