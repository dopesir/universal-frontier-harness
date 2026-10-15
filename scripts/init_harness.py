#!/usr/bin/env python3
"""One-command installer for the Universal Frontier Harness.

Installs the harness kernel, hooks, and persistent memory directories into any target project.
Usage:
    python scripts/init_harness.py [target_project_directory]
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def init_project(target_dir: str | Path) -> None:
    target = Path(target_dir).resolve()
    print(f"Initializing Universal Frontier Harness in: {target}")

    agents_dir = target / ".agents"
    memory_dir = agents_dir / "memory"
    rules_dir = agents_dir / "rules"
    hooks_dir = agents_dir / "hooks"

    for d in (memory_dir, rules_dir, hooks_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 1. Copy Kernel Rules
    shutil.copy2(ROOT / "rules" / "AGENTS.md", rules_dir / "AGENTS.md")
    shutil.copy2(ROOT / "rules" / "AGENTS.md", agents_dir / "AGENTS.md")
    shutil.copy2(ROOT / "rules" / "GEMINI.md", agents_dir / "GEMINI.md")
    print("  [OK] Copied rules to .agents/AGENTS.md and .agents/rules/AGENTS.md")

    # 2. Copy Hooks Manifest
    shutil.copy2(ROOT / "hooks" / "hooks.json", hooks_dir / "hooks.json")
    print("  [OK] Copied hooks to .agents/hooks/hooks.json")

    # 3. Initialize Memory Files
    memory_templates = {
        "task_state.md": "# Task State\n\n- **Active Objective**: None\n- **Phase**: UNINITIALIZED\n",
        "decisions.md": "# Architecture Decision Records (ADRs)\n\n| Date | Decision | Rationale | Alternatives Considered |\n| :--- | :--- | :--- | :--- |\n",
        "constraints.md": "# Project Constraints\n\n- Do not modify files outside declared scope.\n- Preserve existing tests and comments.\n",
        "unresolved.md": "# Unresolved Issues\n\nNo unresolved issues recorded.\n",
        "verification.md": "# Verification Evidence Log\n\n| Date | Task ID | Validator | Result | Evidence File |\n| :--- | :--- | :--- | :--- | :--- |\n",
    }
    for fname, content in memory_templates.items():
        mf = memory_dir / fname
        if not mf.exists():
            mf.write_text(content, encoding="utf-8")
            print(f"  [OK] Initialized .agents/memory/{fname}")

    print("\nUniversal Frontier Harness initialization complete! System is ready.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install Universal Frontier Harness")
    parser.add_argument("target", nargs="?", default=".", help="Target project root directory")
    args = parser.parse_args()
    init_project(args.target)
