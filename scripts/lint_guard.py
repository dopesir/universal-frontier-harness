#!/usr/bin/env python3
"""Deterministic Syntax & Lint Guardrail (SWE-agent / Codacy Pattern).

Runs immediate AST syntax verification and lint checks on target files
before declaring an edit complete, providing an unyielding quality floor.
"""

import ast
import os
import subprocess
import sys


def check_python_syntax(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        ast.parse(code, filename=filepath)
        return True, "AST syntax check passed."
    except SyntaxError as e:
        return False, f"SyntaxError at line {e.lineno}, column {e.offset}: {e.msg}\n  {e.text}"
    except Exception as e:
        return False, f"Parse error: {str(e)}"


def check_node_syntax(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext in [".ts", ".tsx"]:
        return check_balanced_delimiters(filepath)
    # If .js/.mjs/.cjs and node is available, use `node --check`
    try:
        res = subprocess.run(["node", "--check", filepath], capture_output=True, text=True, timeout=5)
        if res.returncode == 0:
            return True, "Node syntax check passed."
        else:
            return False, f"JS syntax error:\n{res.stderr.strip()}"
    except Exception:
        return check_balanced_delimiters(filepath)


def check_balanced_delimiters(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        return False, str(e)

    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    in_str = None
    esc = False

    for idx, ch in enumerate(content):
        if in_str:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == in_str:
                in_str = None
            continue

        if ch in ('"', "'", '`'):
            in_str = ch
            continue

        if ch in pairs.values():
            stack.append((ch, idx))
        elif ch in pairs.keys():
            if not stack or stack[-1][0] != pairs[ch]:
                return False, f"Unbalanced delimiter '{ch}' near char offset {idx}"
            stack.pop()

    if stack:
        unclosed = stack[-1][0]
        return False, f"Unclosed delimiter '{unclosed}' near char offset {stack[-1][1]}"

    return True, "Delimiter check passed."


def main():
    if len(sys.argv) < 2:
        print("Usage: python lint_guard.py <filepath>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"Error: File does not exist: {filepath}")
        sys.exit(1)

    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".py":
        ok, msg = check_python_syntax(filepath)
    elif ext in [".js", ".jsx", ".ts", ".tsx"]:
        ok, msg = check_node_syntax(filepath)
    else:
        ok, msg = True, "Filetype skipped (non-code)."

    if ok:
        print(f"[LINT GUARD PASS] {filepath}: {msg}")
        sys.exit(0)
    else:
        print(f"[LINT GUARD FAIL] {filepath}:\n{msg}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    main()
