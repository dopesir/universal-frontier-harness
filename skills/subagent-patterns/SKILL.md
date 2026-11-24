---
name: subagent-patterns
description: >-
  Recommended patterns for multi-agent delegation using Antigravity subagents.
  Use this skill when a task would benefit from parallel work, independent
  review, or specialized research. Provides templates for RESEARCHER, REVIEWER,
  and IMPLEMENTER agent roles with delegation guidelines.
---

# Subagent Patterns — Multi-Agent Delegation

## When to Use

- When tasks are genuinely separable and can benefit from parallel execution
- When independent review would improve confidence (LARGE/CRITICAL tasks)
- When extensive research is needed without cluttering the main context
- When explicitly instructed to use multiple agents

## When NOT to Use

- For TRIVIAL or SMALL tasks — overhead exceeds benefit
- When tasks are tightly coupled and cannot be meaningfully separated
- When the same work would be duplicated across agents
- Merely because the system supports subagents

## Available Subagent Types

Antigravity provides two built-in subagent types:

| Type | Capabilities | Best For |
|------|-------------|----------|
| `research` | Read-only: file reading, searching, web browsing | Investigation, documentation review, code analysis |
| `self` | Full capabilities: read, write, execute | Independent implementation of separable components |

## Recommended Patterns

### RESEARCHER — Codebase/Documentation Investigation

Use for: broad surveys, documentation reading, understanding unfamiliar code.

```
TypeName: "research"
Role: "Codebase Researcher"
Prompt: "Investigate [specific topic]. Read [specific files/docs].
         Report: (1) what you found, (2) relevant code locations,
         (3) constraints or patterns discovered.
         Focus on FACTS — tag anything uncertain as INFERENCE or ASSUMPTION."
```

### REVIEWER — Independent Adversarial Review

Use for: code review of completed work, catching errors the implementer missed.

```
TypeName: "research"
Role: "Independent Code Reviewer"
Prompt: "Review the following changes for correctness, edge cases, and
         potential regressions. You are reviewing work done by another agent.
         Be specific and evidence-based. Files changed: [list].
         Original requirements: [summary].
         Report: (1) issues found with severity, (2) edge cases not covered,
         (3) overall assessment: PASS / CONDITIONAL PASS / FAIL."
```

### IMPLEMENTER — Parallel Independent Implementation

Use for: implementing components that have no shared dependencies.

```
TypeName: "self"
Role: "Component Implementer"
Prompt: "Implement [specific component]. Requirements: [list].
         Constraints: [list]. Do NOT modify files outside [scope].
         When complete, verify: [build/test command].
         Report what was implemented and verification results."
```

## Delegation Rules

1. **Parent owns integration**: The parent agent is responsible for integrating
   subagent results, resolving conflicts, and performing final verification.

2. **Clear scope boundaries**: Each subagent must have a clearly defined scope.
   Specify which files it may read/modify and what output is expected.

3. **No redundant work**: Do not assign the same task to multiple subagents
   unless you specifically need independent perspectives (e.g., review).

4. **Results are INFERENCE**: Subagent outputs should be treated as INFERENCE
   until independently verified by the parent.

5. **Fail gracefully**: If a subagent fails or returns poor results, the parent
   should handle the failure rather than silently accepting bad output.

## Anti-Patterns

- Spawning agents for every minor sub-task
- Having multiple agents modify the same files
- Treating subagent output as FACT without verification
- Using subagents to avoid thinking about the problem
- Creating long chains of delegation (agent → subagent → sub-subagent)
