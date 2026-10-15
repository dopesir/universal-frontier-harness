---
name: subagent-orchestration
description: Multi-agent coordination patterns. Separates Coordinator, Researcher, Implementer, and Hostile Verifier roles to eliminate cognitive overload and author confirmation bias.
---

# Subagent Orchestration & Role Architecture

## The 4 Specialized Roles

1. **Coordinator (Lead Orchestrator)**:
   - Maintains contract and task state in `.agents/memory/task_state.md`.
   - Never loads large file logs; keeps context lean (<10k tokens).
   - Coordinates subagents and validates integration.

2. **Researcher (Read-Only Investigator)**:
   - Toolset: `view_file`, `search_web`, read-only commands.
   - Explores large repos, searches docs, outputs 30-line synthesis.
   - Prevents 50k+ raw token dumps in primary coordinator context.

3. **Implementer (Surgical Mutator)**:
   - Scope-fenced to targeted files only.
   - Follows Ponytail YAGNI ladder.
   - Runs local unit tests and fast AST linter.

4. **Hostile Verifier (Independent Auditor)**:
   - Spawned with a **fresh context window** (zero exposure to author rationalizations).
   - Adversarial stance: tries to break code against the 6 Vulnerability Vectors.
   - A task cannot conclude without a signed PASS from the Hostile Verifier.
