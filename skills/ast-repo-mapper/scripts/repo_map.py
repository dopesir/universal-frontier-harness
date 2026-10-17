#!/usr/bin/env python3
"""AST Repository Symbol Mapper.

Extracts classes, methods, and functions into a high-density index
with zero third-party dependencies.
"""

from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".agents",
    "venv",
    ".venv",
}


def parse_python_symbols(path: Path) -> list[str]:
    symbols = []
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(content, filename=str(path))
    except Exception:
        return []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            symbols.append(f"  class {node.name}")
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args = [a.arg for a in item.args.args if a.arg != "self"]
                    symbols.append(f"    def {item.name}({', '.join(args)})")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [a.arg for a in node.args.args]
            symbols.append(f"  def {node.name}({', '.join(args)})")

    return symbols


def parse_js_ts_symbols(path: Path) -> list[str]:
    symbols = []
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    # Simple regex extractor for functions and classes
    fn_matches = re.findall(r"(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_$]+)\s*\(([^)]*)\)", content)
    for name, params in fn_matches:
        symbols.append(f"  function {name}({params.strip()})")

    class_matches = re.findall(r"(?:export\s+)?class\s+([A-Za-z0-9_$]+)", content)
    for name in class_matches:
        symbols.append(f"  class {name}")

    return symbols


def generate_repo_map(root_dir: str | Path, max_files: int = 50, include_blast_radius: bool = False) -> str:
    root = Path(root_dir).resolve()
    lines = [f"# Symbol Map: {root.name}"]
    count = 0

    graph = None
    if include_blast_radius:
        try:
            for cand in [root, root.parent, Path(__file__).resolve().parent.parent.parent.parent]:
                if (cand / "core").is_dir() and str(cand) not in sys.path:
                    sys.path.insert(0, str(cand))
            from core.graph_intel import get_dependency_graph
            graph = get_dependency_graph(root)
        except Exception:
            pass

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for f in filenames:
            p = Path(dirpath) / f
            ext = p.suffix.lower()
            if ext not in (".py", ".js", ".ts", ".jsx", ".tsx"):
                continue

            rel_path = p.relative_to(root)
            symbols = []
            if ext == ".py":
                symbols = parse_python_symbols(p)
            else:
                symbols = parse_js_ts_symbols(p)

            if symbols:
                header = f"\n{rel_path}:"
                if graph:
                    br = graph.compute_blast_radius(str(rel_path).replace("\\", "/"))
                    if br.score > 0:
                        header = f"\n{rel_path} [Blast Radius: {br.level} ({br.score} dep{'s' if br.score > 1 else ''})]:"
                lines.append(header)
                lines.extend(symbols)
                count += 1
                if count >= max_files:
                    lines.append(f"\n[... truncated at {max_files} files]")
                    return "\n".join(lines)

    return "\n".join(lines)


if __name__ == "__main__":
    args = sys.argv[1:]
    with_br = "--with-blast-radius" in args or "--blast-radius" in args
    filtered_args = [a for a in args if not a.startswith("--")]
    target = filtered_args[0] if filtered_args else "."
    print(generate_repo_map(target, include_blast_radius=with_br))
