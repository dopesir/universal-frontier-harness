---
name: project-memory
description: >-
  Lightweight persistent project state management for long-running tasks.
  Use this skill when starting a long task, resuming interrupted work, when
  instructed to "save state", "checkpoint", "record decisions", or "persist
  progress". Maintains human-readable markdown files in .agents/memory/ that
  enable session recovery without relying on conversational context.
---

# Project Memory — Persistent State Management

## When to Use

- At the start of any LARGE or CRITICAL task
- When a task spans multiple sessions or may be interrupted
- When important architecture decisions are made
- When explicitly instructed to checkpoint or save state
- When resuming work and needing to understand prior context

## Memory Location

All state files live in `.agents/memory/` at the workspace root:

```text
.agents/memory/
├── decisions.md        # Architecture decisions & rationale
├── constraints.md      # Discovered conventions & constraints
├── task_state.md       # Current task progress & verification status
├── unresolved.md       # Open issues & unresolved problems
└── verification.md     # Verification history & results
```

## Initialization

Run the init script to create the directory structure with template files:

```bash
python .agents/plugins/universal-harness/skills/project-memory/scripts/init_memory.py
```

Or create the files manually. The structure is simple markdown.

## File Formats

### decisions.md

Record architecture and implementation decisions with rationale:

```markdown
# Decisions

## YYYY-MM-DD — [Decision Title]

**Context**: [why this decision was needed]
**Decision**: [what was decided]
**Rationale**: [why this option was chosen]
**Alternatives Considered**: [what was rejected and why]
**Status**: ACTIVE | SUPERSEDED | REVERSED
```

### constraints.md

Record discovered project constraints and conventions:

```markdown
# Constraints & Conventions

## Build
- [e.g., "TypeScript strict mode is enforced"]

## Architecture
- [e.g., "Single ExoPlayer instance — never create a second"]

## Testing
- [e.g., "Jest with React Native preset, run via `npm test`"]

## External
- [e.g., "API rate limit: 100 req/min on archive.org"]
```

### task_state.md

Track current task progress:

```markdown
# Task State

**Objective**: [what we're trying to accomplish]
**Started**: [date/time]
**Complexity**: TRIVIAL | SMALL | MEDIUM | LARGE | CRITICAL

## Sub-Tasks
- [x] [completed task] — VERIFIED via [evidence]
- [/] [in-progress task] — [current status]
- [ ] [pending task]

## Key Decisions Made
- [decision 1 — see decisions.md for detail]

## Current Blockers
- [blocker if any]

## Next Steps
1. [immediate next action]
```

### unresolved.md

Track open issues that need attention:

```markdown
# Unresolved Issues

## ISSUE-001 — [Title]
**Severity**: LOW | MEDIUM | HIGH | CRITICAL
**Discovered**: [date]
**Context**: [what happened]
**Impact**: [what's affected]
**Attempted Fixes**: [what was tried]
**Status**: OPEN | INVESTIGATING | BLOCKED | DEFERRED
```

### verification.md

Record verification history:

```markdown
# Verification History

## [Date] — [What was verified]
**Method**: [build / test / runtime / visual / manual]
**Command**: [exact command if applicable]
**Result**: PASS | FAIL | PARTIAL
**Evidence**: [output summary or screenshot path]
**Notes**: [any relevant observations]
```

## Usage Guidelines

- **Keep files small**: Each file should be under 200 lines. Archive old
  entries if they grow too large.
- **Human-readable**: Anyone (human or agent) should be able to read these
  files and understand the project state.
- **Version-controllable**: These files can be committed to git if desired.
- **No raw transcripts**: Never dump conversation transcripts into memory
  files. Distill to actionable state only.
- **Update incrementally**: Don't rewrite entire files — append or update
  specific sections.

## Recovery Procedure

When resuming interrupted work:

1. Read `task_state.md` to understand the objective and progress
2. Read `unresolved.md` for any blockers or open issues
3. Read `decisions.md` for decisions already made
4. Read `verification.md` for what has been verified
5. Inspect git state for changes since last checkpoint
6. Continue from the next uncompleted sub-task

## Anti-Patterns

- Do NOT create memory files for TRIVIAL or SMALL tasks
- Do NOT store raw conversation transcripts
- Do NOT create a giant uncontrolled memory database
- Do NOT update memory after every single action — update at meaningful
  checkpoints
- Do NOT rely on memory files as a substitute for reading actual code
