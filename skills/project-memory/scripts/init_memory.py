#!/usr/bin/env python3
"""Initialize the .agents/memory/ directory structure with template files.

Creates the memory directory and populates it with empty template files
if they don't already exist. Safe to run multiple times — never overwrites
existing content.
"""

import os
import sys

MEMORY_DIR = os.path.join(".agents", "memory")

TEMPLATES = {
    "decisions.md": """# Decisions

<!-- Record architecture and implementation decisions with rationale.
     Format:
     ## YYYY-MM-DD — [Decision Title]
     **Context**: [why]
     **Decision**: [what]
     **Rationale**: [why this option]
     **Status**: ACTIVE | SUPERSEDED | REVERSED
-->
""",
    "constraints.md": """# Constraints & Conventions

<!-- Record discovered project constraints and conventions. -->

## Build

## Architecture

## Testing

## External
""",
    "task_state.md": """# Task State

<!-- Track current task progress. Update at meaningful checkpoints. -->
""",
    "unresolved.md": """# Unresolved Issues

<!-- Track open issues that need attention.
     Format:
     ## ISSUE-NNN — [Title]
     **Severity**: LOW | MEDIUM | HIGH | CRITICAL
     **Status**: OPEN | INVESTIGATING | BLOCKED | DEFERRED
-->
""",
    "verification.md": """# Verification History

<!-- Record verification results.
     Format:
     ## [Date] — [What was verified]
     **Method**: build | test | runtime | visual | manual
     **Result**: PASS | FAIL | PARTIAL
     **Evidence**: [output or path]
-->
""",
}


def main():
    # Find workspace root (walk up to find .agents/ or .git/)
    workspace_root = os.getcwd()

    memory_path = os.path.join(workspace_root, MEMORY_DIR)
    os.makedirs(memory_path, exist_ok=True)

    created = []
    skipped = []

    for filename, template in TEMPLATES.items():
        filepath = os.path.join(memory_path, filename)
        if os.path.exists(filepath):
            skipped.append(filename)
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(template)
            created.append(filename)

    print(f"Memory directory: {memory_path}")
    if created:
        print(f"Created: {', '.join(created)}")
    if skipped:
        print(f"Skipped (already exist): {', '.join(skipped)}")
    if not created and not skipped:
        print("No files to create.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
