#!/usr/bin/env python3
"""Pre-invocation hook: Injects ephemeral recency reminders before model generation.

Counters the 'Lost-in-the-Middle' effect by placing active task state directly
at the model's recency boundary.
Fast execution (<15ms), non-blocking, strict UTF-8.
"""

import json
import os
import re
import sys
from pathlib import Path


def main():
    try:
        input_data = {} if sys.stdin.isatty() else json.load(sys.stdin)
    except Exception:
        input_data = {}

    workspace_paths = input_data.get("workspacePaths", [])
    if workspace_paths:
        root = Path(workspace_paths[0])
    else:
        root = Path.cwd()

    task_state_path = root / ".agents" / "memory" / "task_state.md"
    if not task_state_path.is_file():
        # Try finding in current directory
        task_state_path = Path(".agents/memory/task_state.md")

    if not task_state_path.is_file():
        json.dump({}, sys.stdout)
        return

    try:
        content = task_state_path.read_text(encoding="utf-8", errors="replace").strip()
    except Exception:
        json.dump({}, sys.stdout)
        return

    # Strip HTML comments
    stripped = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL).strip()
    if not stripped or len(stripped) < 50:
        json.dump({}, sys.stdout)
        return

    summary = content[:450]
    if len(content) > 450:
        summary += "\n\n[... truncated — read .agents/memory/task_state.md for complete record]"

    reminder = (
        "[Universal Frontier Harness] Active task state detected. "
        "Adhere to 6 Invariants and Ponytail YAGNI ladder.\n\n"
        f"{summary}"
    )

    result = {"injectSteps": [{"ephemeralMessage": reminder}]}
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
