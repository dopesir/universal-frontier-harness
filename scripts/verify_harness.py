#!/usr/bin/env python3
"""Universal Engineering Harness V2 - Health & Integrity Verification Script.

Validates:
1. Workspace entry point (.agents/AGENTS.md)
2. Core behavioral rules (13 rules in .agents/plugins/universal-harness/rules/AGENTS.md)
3. All 5 required skills with valid YAML frontmatter
4. All 5 persistent memory files in .agents/memory/
5. Plugin configuration (plugin.json, hooks.json)
6. Supporting scripts functionality (pre_invocation_check.py)

Usage:
    python verify_harness.py
Exit code 0 on all checks PASS, 1 on any FAIL.
"""

import json
import os
import re
import sys


def check_file_exists(path, description):
    if os.path.isfile(path):
        print(f"  [PASS] {description}: {os.path.basename(path)}")
        return True
    else:
        print(f"  [FAIL] {description} MISSING: {path}")
        return False


def check_skill(skill_dir, skill_name):
    skill_file = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_file):
        print(f"  [FAIL] Skill '{skill_name}' missing SKILL.md")
        return False

    try:
        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  [FAIL] Skill '{skill_name}' could not be read: {e}")
        return False

    # Check for frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not fm_match:
        print(f"  [FAIL] Skill '{skill_name}' missing valid YAML frontmatter")
        return False

    fm = fm_match.group(1)
    if f"name: {skill_name}" not in fm and f'name: "{skill_name}"' not in fm:
        print(f"  [FAIL] Skill '{skill_name}' frontmatter name mismatch")
        return False

    print(f"  [PASS] Skill '{skill_name}' verified")
    return True


def verify_plugin(plugin_dir, is_global=False):
    label = "Global Plugin" if is_global else "Workspace Plugin"
    print(f"\n--- Checking {label} ({plugin_dir}) ---")
    passed = True

    # Core rules (v7.1.0: 5 Sections & 6 Invariants)
    print("\n  Core Behavioral Rules:")
    rules_file = os.path.join(plugin_dir, "rules", "AGENTS.md")
    if check_file_exists(rules_file, f"{label} rules AGENTS.md"):
        with open(rules_file, "r", encoding="utf-8-sig") as f:
            rules_content = f.read()

        sections = [
            "The 6 Non-Negotiable Invariants",
            "The Finite State Machine",
            "The Ponytail YAGNI Ladder",
            "Web & UI Deliverables Protocol",
            "Skills & Progressive Disclosure",
        ]
        for idx, sec in enumerate(sections, 1):
            if sec in rules_content or f"## {idx}." in rules_content:
                print(f"    [PASS] Section {idx}: {sec}")
            else:
                print(f"    [FAIL] Section {idx} missing: {sec}")
                passed = False

        invariants = [
            "Reconnaissance Before Mutation",
            "Reproduce Before Repair",
            "Surgical Diff Principle",
            "Evidence-First Completion",
            "Circuit Breakers",
            "Caller & Invariant Preservation",
        ]
        for inv in invariants:
            if inv in rules_content:
                print(f"    [PASS] Invariant: {inv}")
            else:
                print(f"    [FAIL] Invariant missing: {inv}")
                passed = False
    else:
        passed = False

    # Skills catalog (9 skills)
    print("\n  Skills Catalog:")
    skills_dir = os.path.join(plugin_dir, "skills")
    required_skills = [
        "adversarial-review",
        "ast-repo-mapper",
        "cold-verification",
        "deterministic-lint-guard",
        "engineering-recon",
        "intent-grounding-and-architecture",
        "project-memory",
        "repro-first-debugging",
        "subagent-patterns"
    ]
    for s in required_skills:
        s_dir = os.path.join(skills_dir, s)
        if not check_skill(s_dir, s):
            passed = False

    # Plugin configuration & hooks
    print("\n  Plugin Configuration & Hooks:")
    plugin_json = os.path.join(plugin_dir, "plugin.json")
    hooks_json = os.path.join(plugin_dir, "hooks.json")
    if check_file_exists(plugin_json, "plugin.json"):
        try:
            with open(plugin_json, "r", encoding="utf-8-sig") as f:
                json.load(f)
            print("    [PASS] plugin.json is valid JSON")
        except Exception as e:
            print(f"    [FAIL] plugin.json invalid: {e}")
            passed = False
    else:
        passed = False

    if check_file_exists(hooks_json, "hooks.json"):
        try:
            with open(hooks_json, "r", encoding="utf-8-sig") as f:
                json.load(f)
            print("    [PASS] hooks.json is valid JSON")
        except Exception as e:
            print(f"    [FAIL] hooks.json invalid: {e}")
            passed = False
    else:
        passed = False

    # Supporting scripts
    print("\n  Supporting Scripts:")
    for script_name in ["pre_invocation_check.py", "repo_map.py", "lint_guard.py", "serve_preview.py", "harness_rsi.py"]:
        script_path = os.path.join(plugin_dir, "scripts", script_name)
        if not check_file_exists(script_path, script_name):
            passed = False

    return passed


def main():
    if "--version" in sys.argv:
        print("Universal Frontier Harness v6.2.0")
        sys.exit(0)

    print("=== Universal Frontier Harness v6.2 Health & Integrity Check ===")
    
    check_mode = "all" if "--all" in sys.argv else ("global" if "--global" in sys.argv else "auto")
    global_plugin_dir = os.path.expanduser(r"~\.gemini\config\plugins\universal-harness")
    
    # Parse explicit workspace override if provided
    workspace_override = None
    for idx, arg in enumerate(sys.argv):
        if arg == "--workspace" and idx + 1 < len(sys.argv):
            workspace_override = sys.argv[idx + 1]
            break
        elif arg.startswith("--workspace="):
            workspace_override = arg.split("=", 1)[1]
            break

    all_passed = True

    # 1. Check Workspace if requested/present
    if check_mode in ("auto", "all", "workspace"):
        workspace_found = False
        if workspace_override:
            candidate = os.path.abspath(workspace_override)
            if os.path.isfile(os.path.join(candidate, ".agents", "AGENTS.md")) or \
               os.path.isdir(os.path.join(candidate, ".agents", "plugins", "universal-harness")):
                workspace_found = True
            elif os.path.isdir(candidate) and os.path.basename(candidate) == ".agents":
                candidate = os.path.dirname(candidate)
                workspace_found = True
        else:
            candidate = os.path.abspath(os.getcwd())
            while True:
                if os.path.isfile(os.path.join(candidate, ".agents", "AGENTS.md")) or \
                   os.path.isdir(os.path.join(candidate, ".agents", "plugins", "universal-harness")):
                    workspace_found = True
                    break
                parent = os.path.dirname(candidate)
                if parent == candidate:
                    break
                candidate = parent

        if workspace_found:
            workspace_root = candidate
            agents_dir = os.path.join(workspace_root, ".agents")
            plugin_dir = os.path.join(agents_dir, "plugins", "universal-harness")

            print("\n1. Workspace Entry Point:")
            entry_point = os.path.join(agents_dir, "AGENTS.md")
            if not check_file_exists(entry_point, "Workspace entry AGENTS.md"):
                all_passed = False

            if not verify_plugin(plugin_dir, is_global=False):
                all_passed = False

            print("\n  Persistent Memory:")
            memory_dir = os.path.join(agents_dir, "memory")
            required_mem_files = [
                "task_state.md",
                "decisions.md",
                "constraints.md",
                "unresolved.md",
                "verification.md"
            ]
            for mf in required_mem_files:
                mf_path = os.path.join(memory_dir, mf)
                if not check_file_exists(mf_path, f"Memory file '{mf}'"):
                    all_passed = False
        elif check_mode == "workspace":
            print("ERROR: Could not locate active .agents harness in specified workspace.")
            sys.exit(1)
        elif check_mode == "all":
            print("\n[INFO] No active workspace harness detected in current path. Evaluating global installation.")

    # 2. Check Global Plugin
    if check_mode in ("auto", "all", "global"):
        if os.path.isdir(global_plugin_dir):
            if not verify_plugin(global_plugin_dir, is_global=True):
                all_passed = False
        else:
            if check_mode in ("all", "global"):
                print(f"\n[FAIL] Global plugin not found at: {global_plugin_dir}")
                all_passed = False

    print("\n=======================================================")
    if all_passed:
        print("RESULT: ALL HARNESS CHECKS PASSED. SYSTEM IS HEALTHY.")
        print("=======================================================")
        sys.exit(0)
    else:
        print("RESULT: ONE OR MORE CHECKS FAILED.")
        print("=======================================================")
        sys.exit(1)


if __name__ == "__main__":
    main()
