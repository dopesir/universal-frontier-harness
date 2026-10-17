#!/usr/bin/env python3
"""Universal Frontier Harness - System Health and Integrity Verifier.

Usage:
    python scripts/verify_harness.py
Exit code 0 on all checks PASS, 1 on any failure.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check_file(rel_path: str, description: str) -> bool:
    p = ROOT / rel_path
    if p.is_file():
        print(f"  [PASS] {description}: {rel_path}")
        return True
    print(f"  [FAIL] {description} MISSING: {rel_path}")
    return False


def check_skill(skill_dir: Path) -> bool:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        print(f"  [FAIL] Skill '{skill_dir.name}' missing SKILL.md")
        return False
    try:
        content = skill_file.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  [FAIL] Could not read '{skill_dir.name}/SKILL.md': {e}")
        return False

    # Check for frontmatter
    fm = re.match(r"^---\s*\n(.*?)\n---", content, flags=re.DOTALL)
    if not fm:
        print(f"  [FAIL] Skill '{skill_dir.name}' missing valid YAML frontmatter (---)")
        return False

    header = fm.group(1)
    if not re.search(r"^name:\s*\S+", header, re.MULTILINE):
        print(f"  [FAIL] Skill '{skill_dir.name}' missing 'name' in frontmatter")
        return False
    if not re.search(r"^description:\s*\S+", header, re.MULTILINE):
        print(f"  [FAIL] Skill '{skill_dir.name}' missing 'description' in frontmatter")
        return False

    print(f"  [PASS] Skill '{skill_dir.name}': valid frontmatter")
    return True


def main():
    print("=======================================================")
    print(" Universal Frontier Harness — System Integrity Audit")
    print("=======================================================\n")

    all_passed = True

    # 1. Entry point checks
    print("1. Entry Points & Rules:")
    if not check_file("rules/AGENTS.md", "Kernel rules"):
        all_passed = False
    if not check_file("rules/GEMINI.md", "Gemini entry point"):
        all_passed = False

    # 2. Core modules
    print("\n2. Core Reliability Modules:")
    core_modules = [
        "core/__init__.py",
        "core/contract.py",
        "core/evidence.py",
        "core/fast_lint.py",
        "core/graph_intel.py",
        "core/policy.py",
        "core/state_machine.py",
        "core/stop_gate.py",
    ]
    for m in core_modules:
        if not check_file(m, f"Core module {m}"):
            all_passed = False

    # 3. Hook manifest and scripts
    print("\n3. Hooks & Manifests:")
    hooks = [
        "hooks/hooks.json",
        "hooks/pre_invocation.py",
        "hooks/pre_tool.py",
        "hooks/post_tool.py",
        "hooks/stop_gate.py",
    ]
    for h in hooks:
        if not check_file(h, f"Hook {h}"):
            all_passed = False

    # Validate hooks.json schema
    hooks_manifest = ROOT / "hooks" / "hooks.json"
    if hooks_manifest.is_file():
        try:
            with open(hooks_manifest, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "universal-frontier-runtime" in data:
                print("  [PASS] hooks.json contains valid 'universal-frontier-runtime' manifest")
            else:
                print("  [FAIL] hooks.json missing 'universal-frontier-runtime' key")
                all_passed = False
        except Exception as e:
            print(f"  [FAIL] hooks.json failed to parse: {e}")
            all_passed = False

    # 4. Specialized skills
    print("\n4. Specialized Skills:")
    skills_dir = ROOT / "skills"
    if skills_dir.is_dir():
        for s_path in skills_dir.iterdir():
            if s_path.is_dir():
                if not check_skill(s_path):
                    all_passed = False
    else:
        print("  [FAIL] skills/ directory missing")
        all_passed = False

    # 5. Unit test suite
    print("\n5. Executable Unit Test Suite:")
    res = subprocess.run([sys.executable, "-m", "unittest", "discover", "tests"], cwd=str(ROOT))
    if res.returncode == 0:
        print("  [PASS] All test suite checks passed cleanly (exit code 0)")
    else:
        print(f"  [FAIL] Unit test suite failed with exit code {res.returncode}")
        all_passed = False

    print("\n=======================================================")
    if all_passed:
        print("RESULT: ALL HARNESS CHECKS PASSED. SYSTEM IS 100% HEALTHY.")
        print("=======================================================")
        sys.exit(0)
    else:
        print("RESULT: ONE OR MORE CHECKS FAILED.")
        print("=======================================================")
        sys.exit(1)


if __name__ == "__main__":
    main()
