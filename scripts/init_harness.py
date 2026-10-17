#!/usr/bin/env python3
"""Hardened installer for the Universal Frontier Harness.

Installs the complete harness kernel, core runtime modules, hook scripts,
and persistent memory directories into any target project.

Features:
- Safe by default: detects existing files and prevents silent overwriting.
- Automatic backups: preserves user configuration in timestamped .bak files.
- Dry-run mode (--dry-run): preview planned actions without filesystem changes.
- Explicit overwrite (--overwrite): required to replace existing files.
- Complete runtime layout: installs rules, hooks, and core runtime modules.
- Verification & rollback: validates installation and rolls back on failure.
- Uninstall support (--uninstall): cleanly removes installed runtime files.

Usage:
    python scripts/init_harness.py [target_project_directory] [options]
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent


class InstallPlanItem(NamedTuple):
    action: str  # "create", "overwrite", "skip", "backup"
    source: Path | None
    destination: Path
    details: str


def generate_hooks_manifest() -> dict:
    """Generates the hook manifest configured for the project-local .agents/ layout."""
    return {
        "universal-frontier-runtime": {
            "PreInvocation": [
                {
                    "type": "command",
                    "command": "python .agents/hooks/pre_invocation.py",
                    "timeout": 5,
                }
            ],
            "PreToolUse": [
                {
                    "matcher": "*",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "python .agents/hooks/pre_tool.py",
                            "timeout": 10,
                        }
                    ],
                }
            ],
            "PostToolUse": [
                {
                    "matcher": "*",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "python .agents/hooks/post_tool.py",
                            "timeout": 10,
                        }
                    ],
                }
            ],
            "Stop": [
                {
                    "type": "command",
                    "command": "python .agents/hooks/stop_gate.py",
                    "timeout": 10,
                }
            ],
        }
    }


def compute_install_plan(
    target: Path,
    overwrite: bool = False,
    include_cursor: bool = False,
    include_windsurf: bool = False,
) -> list[InstallPlanItem]:
    """Computes the list of planned filesystem actions."""
    plan: list[InstallPlanItem] = []
    agents_dir = target / ".agents"
    rules_dir = agents_dir / "rules"
    hooks_dir = agents_dir / "hooks"
    core_dir = agents_dir / "core"
    memory_dir = agents_dir / "memory"

    # 1. Rules
    rule_files = [
        (ROOT / "rules" / "AGENTS.md", rules_dir / "AGENTS.md"),
        (ROOT / "rules" / "AGENTS.md", agents_dir / "AGENTS.md"),
        (ROOT / "rules" / "GEMINI.md", agents_dir / "GEMINI.md"),
    ]
    for src, dst in rule_files:
        if dst.exists():
            if overwrite:
                plan.append(InstallPlanItem("overwrite", src, dst, "Overwrite existing rule file"))
            else:
                plan.append(InstallPlanItem("skip", src, dst, "Existing rule file preserved (use --overwrite)"))
        else:
            plan.append(InstallPlanItem("create", src, dst, "Install rule file"))

    # 2. Core runtime modules
    core_files = list((ROOT / "core").glob("*.py"))
    for src in core_files:
        dst = core_dir / src.name
        if dst.exists():
            if overwrite:
                plan.append(InstallPlanItem("overwrite", src, dst, "Overwrite core runtime module"))
            else:
                plan.append(InstallPlanItem("skip", src, dst, "Existing core module preserved"))
        else:
            plan.append(InstallPlanItem("create", src, dst, "Install core runtime module"))

    # 3. Hook scripts
    hook_scripts = list((ROOT / "hooks").glob("*.py"))
    for src in hook_scripts:
        dst = hooks_dir / src.name
        if dst.exists():
            if overwrite:
                plan.append(InstallPlanItem("overwrite", src, dst, "Overwrite hook script"))
            else:
                plan.append(InstallPlanItem("skip", src, dst, "Existing hook script preserved"))
        else:
            plan.append(InstallPlanItem("create", src, dst, "Install hook script"))

    # 4. Hooks manifest (generated)
    hooks_json = hooks_dir / "hooks.json"
    if hooks_json.exists():
        if overwrite:
            plan.append(InstallPlanItem("overwrite", None, hooks_json, "Overwrite hooks manifest"))
        else:
            plan.append(InstallPlanItem("skip", None, hooks_json, "Existing hooks manifest preserved"))
    else:
        plan.append(InstallPlanItem("create", None, hooks_json, "Generate hooks manifest"))

    # 5. Memory templates
    memory_templates = {
        "task_state.md": "# Task State\n\n- **Active Objective**: None\n- **Phase**: UNINITIALIZED\n",
        "decisions.md": "# Architecture Decision Records (ADRs)\n\n| Date | Decision | Rationale | Alternatives Considered |\n| :--- | :--- | :--- | :--- |\n",
        "constraints.md": "# Project Constraints\n\n- Do not modify files outside declared scope.\n- Preserve existing tests and comments.\n",
        "unresolved.md": "# Unresolved Issues\n\nNo unresolved issues recorded.\n",
        "verification.md": "# Verification Evidence Log\n\n| Date | Task ID | Validator | Result | Evidence File |\n| :--- | :--- | :--- | :--- | :--- |\n",
    }
    for fname, _ in memory_templates.items():
        dst = memory_dir / fname
        if dst.exists():
            plan.append(InstallPlanItem("skip", None, dst, "Existing memory file preserved"))
        else:
            plan.append(InstallPlanItem("create", None, dst, f"Initialize {fname} template"))

    # 6. Optional editor templates
    if include_cursor:
        c_src = ROOT / "templates" / ".cursorrules"
        c_dst = target / ".cursorrules"
        if c_dst.exists():
            if overwrite:
                plan.append(InstallPlanItem("overwrite", c_src, c_dst, "Overwrite .cursorrules"))
            else:
                plan.append(InstallPlanItem("skip", c_src, c_dst, "Existing .cursorrules preserved"))
        else:
            plan.append(InstallPlanItem("create", c_src, c_dst, "Install .cursorrules template"))

    if include_windsurf:
        w_src = ROOT / "templates" / ".windsurfrules"
        w_dst = target / ".windsurfrules"
        if w_dst.exists():
            if overwrite:
                plan.append(InstallPlanItem("overwrite", w_src, w_dst, "Overwrite .windsurfrules"))
            else:
                plan.append(InstallPlanItem("skip", w_src, w_dst, "Existing .windsurfrules preserved"))
        else:
            plan.append(InstallPlanItem("create", w_src, w_dst, "Install .windsurfrules template"))

    return plan


def uninstall_harness(target: Path) -> int:
    """Removes installed harness runtime files while preserving memory and user files."""
    print(f"Uninstalling Universal Frontier Harness from: {target.resolve()}")
    agents_dir = target / ".agents"
    if not agents_dir.is_dir():
        print("  [INFO] No .agents directory found in target. Nothing to uninstall.")
        return 0

    removed_count = 0
    # Remove core and hooks directories
    for sub in ("core", "hooks"):
        sub_dir = agents_dir / sub
        if sub_dir.is_dir():
            shutil.rmtree(sub_dir)
            print(f"  [REMOVED] {sub_dir.relative_to(target)}")
            removed_count += 1

    # Remove rules directory
    rules_dir = agents_dir / "rules"
    if rules_dir.is_dir():
        shutil.rmtree(rules_dir)
        print(f"  [REMOVED] {rules_dir.relative_to(target)}")
        removed_count += 1

    # Remove top-level rule files inside .agents/
    for rf in ("AGENTS.md", "GEMINI.md"):
        p = agents_dir / rf
        if p.is_file():
            p.unlink()
            print(f"  [REMOVED] .agents/{rf}")
            removed_count += 1

    print("  [PRESERVED] .agents/memory/ and user files preserved.")
    print(f"\nUninstall complete. Removed {removed_count} harness components.")
    return 0


def init_project(
    target_dir: str | Path = ".",
    dry_run: bool = False,
    overwrite: bool = False,
    backup: bool = True,
    include_cursor: bool = False,
    include_windsurf: bool = False,
) -> int:
    """Installs the harness into target directory with safety checks and validation."""
    target = Path(target_dir).resolve()
    print(f"Universal Frontier Harness Installer (v7.0)")
    print(f"Target Project Directory: {target}\n")

    if not target.exists():
        try:
            target.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"  [ERROR] Cannot create target directory '{target}': {e}", file=sys.stderr)
            return 1

    plan = compute_install_plan(target, overwrite=overwrite, include_cursor=include_cursor, include_windsurf=include_windsurf)

    if dry_run:
        print("--- DRY-RUN MODE (No files will be modified) ---")
        for item in plan:
            print(f"  [{item.action.upper()}] {item.destination.relative_to(target)} ({item.details})")
        print("\nDry-run complete. 0 files modified.")
        return 0

    # Ensure directories exist
    agents_dir = target / ".agents"
    for d in (agents_dir / "rules", agents_dir / "hooks", agents_dir / "core", agents_dir / "memory"):
        d.mkdir(parents=True, exist_ok=True)

    created_files: list[Path] = []
    backups_created: list[Path] = []
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    memory_templates = {
        "task_state.md": "# Task State\n\n- **Active Objective**: None\n- **Phase**: UNINITIALIZED\n",
        "decisions.md": "# Architecture Decision Records (ADRs)\n\n| Date | Decision | Rationale | Alternatives Considered |\n| :--- | :--- | :--- | :--- |\n",
        "constraints.md": "# Project Constraints\n\n- Do not modify files outside declared scope.\n- Preserve existing tests and comments.\n",
        "unresolved.md": "# Unresolved Issues\n\nNo unresolved issues recorded.\n",
        "verification.md": "# Verification Evidence Log\n\n| Date | Task ID | Validator | Result | Evidence File |\n| :--- | :--- | :--- | :--- | :--- |\n",
    }

    try:
        for item in plan:
            dst = item.destination
            rel_name = dst.relative_to(target)

            if item.action == "skip":
                print(f"  [SKIP] {rel_name} ({item.details})")
                continue

            if item.action == "overwrite":
                if backup and dst.exists():
                    bak_file = dst.with_name(f"{dst.name}.bak.{timestamp}")
                    shutil.copy2(dst, bak_file)
                    backups_created.append(bak_file)
                    print(f"  [BACKUP] Created backup: {bak_file.relative_to(target)}")

            # Perform write
            if item.source is not None and item.source.is_file():
                shutil.copy2(item.source, dst)
                created_files.append(dst)
                print(f"  [{'OVERWROTE' if item.action == 'overwrite' else 'CREATED'}] {rel_name}")
            elif dst.name == "hooks.json":
                manifest = generate_hooks_manifest()
                dst.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
                created_files.append(dst)
                print(f"  [CREATED] {rel_name}")
            elif dst.name in memory_templates:
                content = memory_templates[dst.name]
                dst.write_text(content, encoding="utf-8")
                created_files.append(dst)
                print(f"  [CREATED] {rel_name}")

        # Post-installation verification check
        print("\nVerifying installed runtime layout...")
        required_checks = [
            agents_dir / "rules" / "AGENTS.md",
            agents_dir / "hooks" / "hooks.json",
            agents_dir / "hooks" / "pre_tool.py",
            agents_dir / "hooks" / "post_tool.py",
            agents_dir / "hooks" / "stop_gate.py",
            agents_dir / "core" / "contract.py",
            agents_dir / "core" / "evidence.py",
            agents_dir / "core" / "fast_lint.py",
            agents_dir / "core" / "graph_intel.py",
            agents_dir / "core" / "policy.py",
            agents_dir / "core" / "stop_gate.py",
        ]
        missing = [f for f in required_checks if not f.is_file()]
        if missing:
            print(f"  [ERROR] Installation incomplete. Missing required runtime files: {missing}", file=sys.stderr)
            print("  Rolling back created files...", file=sys.stderr)
            for f in created_files:
                f.unlink(missing_ok=True)
            return 1

        print("  [PASS] All required runtime files and modules verified.")
        print("\nUniversal Frontier Harness installation successfully completed!")
        if backups_created:
            print(f"Backups preserved: {len(backups_created)} file(s).")
        return 0

    except Exception as e:
        print(f"\n  [ERROR] Installation failed: {e}", file=sys.stderr)
        print("  Rolling back created files...", file=sys.stderr)
        for f in created_files:
            f.unlink(missing_ok=True)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Universal Frontier Harness - Hardened Project Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("target", nargs="?", default=".", help="Target project root directory (default: current directory)")
    parser.add_argument("--dry-run", action="store_true", help="Preview planned changes without writing to disk")
    parser.add_argument("--overwrite", action="store_true", help="Explicitly allow overwriting existing files")
    parser.add_argument("--no-backup", action="store_true", help="Do not create .bak files when overwriting")
    parser.add_argument("--uninstall", action="store_true", help="Safely remove harness runtime files from target project")
    parser.add_argument("--include-cursor", action="store_true", help="Also install .cursorrules template at project root")
    parser.add_argument("--include-windsurf", action="store_true", help="Also install .windsurfrules template at project root")

    args = parser.parse_args()

    if args.uninstall:
        sys.exit(uninstall_harness(Path(args.target)))

    rc = init_project(
        target_dir=args.target,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
        backup=not args.no_backup,
        include_cursor=args.include_cursor,
        include_windsurf=args.include_windsurf,
    )
    sys.exit(rc)


if __name__ == "__main__":
    main()
