#!/usr/bin/env python3
"""Repository Symbol Map Generator (Aider/Tree-Sitter Pattern).

Parses source code files in the workspace into a compact, high-density symbol map
(classes, methods, functions, and signatures) so the agent has instant structural
awareness without reading entire files or cluttering context.
"""

import ast
import os
import re
import sys


def parse_python_file(filepath):
    symbols = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            tree = ast.parse(f.read(), filename=filepath)
    except Exception:
        return symbols

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args = [a.arg for a in item.args.args]
                    class_methods.append(f"    def {item.name}({', '.join(args)})")
            symbols.append({
                "type": "class",
                "name": node.name,
                "methods": class_methods,
                "line": node.lineno
            })
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [a.arg for a in node.args.args]
            symbols.append({
                "type": "function",
                "name": node.name,
                "sig": f"def {node.name}({', '.join(args)})",
                "line": node.lineno
            })
    return symbols


def parse_js_ts_file(filepath):
    symbols = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return symbols

    fn_pattern = re.compile(r"^\s*(export\s+)?(async\s+)?function\s+([A-Za-z0-9_$]+)\s*\((.*?)\)")
    class_pattern = re.compile(r"^\s*(export\s+)?class\s+([A-Za-z0-9_$]+)")
    const_fn_pattern = re.compile(r"^\s*(export\s+)?const\s+([A-Za-z0-9_$]+)\s*=\s*(async\s+)?\((.*?)\)\s*=>")

    for idx, line in enumerate(lines, 1):
        m_fn = fn_pattern.match(line)
        if m_fn:
            symbols.append({"type": "function", "name": m_fn.group(3), "sig": f"function {m_fn.group(3)}({m_fn.group(4)})", "line": idx})
            continue
        m_class = class_pattern.match(line)
        if m_class:
            symbols.append({"type": "class", "name": m_class.group(2), "methods": [], "line": idx})
            continue
        m_cfn = const_fn_pattern.match(line)
        if m_cfn:
            symbols.append({"type": "function", "name": m_cfn.group(2), "sig": f"const {m_cfn.group(2)} = ({m_cfn.group(4)}) =>", "line": idx})
    return symbols


def generate_repo_map(root_dir, max_files=100):
    map_lines = []
    file_count = 0

    ignore_dirs = {
        ".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build",
        ".next", ".agents", "coverage", ".bundle", "vendor", "staging_pass1",
        "staging_pass2", "staging_pass3", "forensic_delivery"
    }

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs and not d.startswith(".")]
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in [".py", ".ts", ".js", ".tsx", ".jsx"]:
                full_path = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(full_path, root_dir)

                if ext == ".py":
                    syms = parse_python_file(full_path)
                else:
                    syms = parse_js_ts_file(full_path)

                if syms:
                    map_lines.append(f"FILE: {rel_path}:")
                    for s in syms:
                        if s["type"] == "class":
                            map_lines.append(f"  class {s['name']}:")
                            for m in s.get("methods", []):
                                map_lines.append(f"  {m}")
                        elif s["type"] == "function":
                            map_lines.append(f"  {s['sig']}")
                    file_count += 1
                    if file_count >= max_files:
                        map_lines.append(f"\n[Truncated: capped at {max_files} mapped files]")
                        break
        if file_count >= max_files:
            break

    return "\n".join(map_lines)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    target_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    print(generate_repo_map(target_dir))
