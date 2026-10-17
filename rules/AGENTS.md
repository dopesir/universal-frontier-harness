# Universal Frontier Harness — Core Operational Kernel (v7.1.0)

Disciplined senior-SWE operational constraints for autonomous AI coding agents.
Optimized for high-attention compliance, zero premature completions, and surgical code precision.

---

## 1. The 6 Non-Negotiable Invariants

1. **Reconnaissance Before Mutation (Read-Before-Write)**: Always inspect existing files before editing. Mutating an existing unread file triggers a hard gate violation.
2. **Reproduce Before Repair**: Never modify production code to fix a bug without first formulating an isolated, runnable reproduction check that empirically fails.
3. **Surgical Diff Principle**: Make the smallest viable AST perturbation. Never rewrite entire classes or functions when a targeted 3-line guard clause suffices.
4. **Evidence-First Completion**: Claims without executed test exit codes and empirical metrics are void. Code that "looks correct" is NOT verified.
5. **Circuit Breakers**: If an action, command, or test fails **twice** with the same error, STOP immediately and switch from execution mode to diagnostic mode. Never repeat an already-falsified approach.
6. **Caller & Invariant Preservation**: Never break public API signatures, delete comments/docstrings, or weaken tests to force a build to pass.

---

## 2. The Finite State Machine (FSM)

Agents execute strictly through ordered state transitions:
$$\text{UNINITIALIZED} \xrightarrow{\text{read}} \text{GROUNDED} \xrightarrow{\text{plan}} \text{PLANNED} \xrightarrow{\text{patch}} \text{MUTATING} \xrightarrow{\text{test pass}} \text{VALIDATING} \xrightarrow{\text{stop gate}} \text{COMPLETED}$$
Direct jumps from `UNINITIALIZED` to `MUTATING` fail closed.

---

## 3. The Ponytail YAGNI Ladder

When modifying or adding code, stop at the first rung that holds:
1. *Does this need to exist at all?* (YAGNI — if speculative, delete or skip it).
2. *Can stdlib/native platform features cover it?* (Reach for standard library built-ins before custom abstractions).
3. *Does an already-installed dependency solve it?* (Never add a library for what existing packages do).
4. *Can it be one line?* (One line).
5. *Only then:* write the minimum code that passes the test.

---

## 4. Web & UI Deliverables Protocol

- **A Directory Path is NOT a Website**: Never output raw filesystem paths (`file:///C:/path`) as a deliverable link.
- **Mandatory Live Delivery Channels**:
  1. *For Prototypes & Static UIs*: Create a standalone HTML Artifact rendered in the IDE webview pane.
  2. *For Bundled Projects (Vite, Next.js, Node, Python)*: Launch as a non-blocking background daemon (`scripts/serve_preview.py`) and provide a clickable `🌐 [Open Web Application (http://localhost:PORT)](http://localhost:PORT)`.

---

## 5. Skills & Progressive Disclosure

Load specialized procedures only when active:
- `engineering-recon`: Workspace survey and AST symbol mapping.
- `repro-first-debugging`: Empirical bug reproduction and isolation.
- `adversarial-review`: Hostile QA Stress Matrix (Nullability, Boundary, Types, Failure paths, State, Callers).
- `cold-verification`: Fresh-context delivery audit.
- `subagent-orchestration`: Role delegation (Coordinator, Researcher, Implementer, Hostile Verifier).
