#!/usr/bin/env python3
"""Graph-Aware Dependency and Blast-Radius Intelligence Engine.

Provides zero-dependency dependency graph extraction, symbol linkage,
and blast-radius evaluation for AI coding agents.

Dual-Mode Architecture:
1. Native AST Engine (Default):
   Uses Python's standard library `ast` module to scan workspace imports and
   definitions on-the-fly in <10ms with ZERO external dependencies.
   Users and agents DO NOT need to install or initialize Graphify.

2. Graphify Ingestion Adapter (Auto-Adaptive):
   If Graphify's output (`graphify-out/graph.json` or `.graphify/graph.json`)
   is detected in the workspace, this engine automatically ingests it to
   augment blast-radius metrics with multi-language nodes and Louvain communities.
"""

from __future__ import annotations

import ast
from collections import defaultdict, deque
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

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
    ".mypy_cache",
}

GRAPHIFY_CANDIDATE_PATHS = [
    Path("graphify-out") / "graph.json",
    Path(".graphify") / "graph.json",
    Path("graph.json"),
]


@dataclass
class BlastRadius:
    target: str
    score: int
    level: str  # NONE, LOW, MEDIUM, HIGH
    direct_dependents: list[str] = field(default_factory=list)
    transitive_dependents: list[str] = field(default_factory=list)
    source: str = "native_ast"  # native_ast, graphify, none
    advisory: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "score": self.score,
            "level": self.level,
            "direct_dependents": self.direct_dependents,
            "transitive_dependents": self.transitive_dependents,
            "source": self.source,
            "advisory": self.advisory,
        }


class DependencyGraph:
    """Directed dependency graph representing file-level and symbol-level connections."""

    def __init__(self, source: str = "native_ast"):
        self.source = source
        # file_path -> set of files that import it (callers/dependents)
        self.dependents: dict[str, set[str]] = defaultdict(set)
        # file_path -> set of files that it imports (dependencies)
        self.dependencies: dict[str, set[str]] = defaultdict(set)
        # file_path -> list of symbols defined
        self.symbols: dict[str, list[str]] = defaultdict(list)
        # file_path -> community id/name (if provided by Graphify)
        self.communities: dict[str, Any] = {}

    def add_dependency(self, from_file: str, to_file: str):
        if from_file == to_file:
            return
        self.dependencies[from_file].add(to_file)
        self.dependents[to_file].add(from_file)

    def compute_blast_radius(self, target: str, max_depth: int = 2) -> BlastRadius:
        """Computes blast radius of modifying `target` file."""
        norm_target = str(Path(target).as_posix()).lower()

        # Find matching key in dependents
        matched_key = None
        for key in self.dependents.keys():
            k_low = key.lower()
            if k_low == norm_target or norm_target.endswith("/" + k_low) or k_low.endswith("/" + norm_target):
                matched_key = key
                break

        if not matched_key:
            # Check if it's a known dependency without dependents
            for key in self.dependencies.keys():
                k_low = key.lower()
                if k_low == norm_target or norm_target.endswith("/" + k_low) or k_low.endswith("/" + norm_target):
                    matched_key = key
                    break

        if not matched_key:
            return BlastRadius(
                target=target,
                score=0,
                level="NONE",
                direct_dependents=[],
                transitive_dependents=[],
                source=self.source,
                advisory="No known dependents identified.",
            )

        direct = sorted(list(self.dependents.get(matched_key, set())))

        # BFS for transitive dependents
        visited = set()
        queue = deque([(matched_key, 0)])
        while queue:
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for dep in self.dependents.get(current, set()):
                if dep not in visited and dep != matched_key:
                    visited.add(dep)
                    queue.append((dep, depth + 1))

        all_deps = sorted(list(visited))
        score = len(all_deps)

        if score == 0:
            level = "NONE"
            advisory = f"Target '{target}' has no external dependents."
        elif score <= 2:
            level = "LOW"
            advisory = f"Target '{target}' has low blast radius ({score} dependent{'s' if score > 1 else ''})."
        elif score <= 4:
            level = "MEDIUM"
            advisory = (
                f"Target '{target}' has medium blast radius ({score} dependents: {', '.join(all_deps[:3])}). "
                "Ensure public interfaces remain stable."
            )
        else:
            level = "HIGH"
            advisory = (
                f"CRITICAL BLAST RADIUS: Target '{target}' is depended on by {score} files "
                f"({', '.join(all_deps[:4])}{'...' if len(all_deps) > 4 else ''}). "
                "Mutations to public symbols may cause cascading failures across callers."
            )

        return BlastRadius(
            target=target,
            score=score,
            level=level,
            direct_dependents=direct,
            transitive_dependents=all_deps,
            source=self.source,
            advisory=advisory,
        )


def _load_graphify_graph(json_path: Path, root: Path) -> DependencyGraph | None:
    """Parses Graphify graph.json into a DependencyGraph."""
    try:
        with open(json_path, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
    except Exception:
        return None

    nodes = data.get("nodes", [])
    links = data.get("links", []) or data.get("edges", [])

    if not nodes and not links:
        return None

    graph = DependencyGraph(source="graphify")

    # Map node id -> source_file
    id_to_file: dict[str, str] = {}
    for node in nodes:
        node_id = str(node.get("id", ""))
        src_file = node.get("source_file") or node.get("file") or ""
        if src_file:
            norm_path = str(Path(src_file).as_posix())
            id_to_file[node_id] = norm_path
            comm = node.get("community")
            if comm is not None:
                graph.communities[norm_path] = comm
            label = node.get("label")
            if label:
                graph.symbols[norm_path].append(label)

    # Ingest edges
    for link in links:
        src = str(link.get("source") or link.get("_src") or "")
        tgt = str(link.get("target") or link.get("_tgt") or "")
        relation = str(link.get("relation", "")).lower()

        src_file = id_to_file.get(src, "")
        tgt_file = id_to_file.get(tgt, "")

        if src_file and tgt_file and src_file != tgt_file:
            # If relation is 'imports_from', src_file imports tgt_file
            if "import" in relation or relation in ("calls", "uses", "depends_on"):
                graph.add_dependency(from_file=src_file, to_file=tgt_file)
            else:
                graph.add_dependency(from_file=src_file, to_file=tgt_file)

    return graph


def _extract_python_ast(path: Path, root: Path) -> tuple[list[str], list[str]]:
    """Extracts defined symbols and imported module names using stdlib ast."""
    symbols = []
    imports = []

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(content, filename=str(path))
    except Exception:
        return [], []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            symbols.append(f"class:{node.name}")
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols.append(f"method:{node.name}.{item.name}")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append(f"func:{node.name}")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if node.level > 0:
                # Relative import
                pkg_parts = list(path.relative_to(root).parent.parts)
                trim = node.level - 1
                if trim > 0 and len(pkg_parts) >= trim:
                    pkg_parts = pkg_parts[:-trim]
                if mod:
                    pkg_parts.append(mod)
                imports.append(".".join(pkg_parts))
            elif mod:
                imports.append(mod)

    return symbols, imports


def _build_native_ast_graph(root: Path) -> DependencyGraph:
    """Builds a DependencyGraph using pure Python stdlib AST in <10ms."""
    graph = DependencyGraph(source="native_ast")
    py_files: dict[str, Path] = {}
    imports_map: dict[str, list[str]] = {}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for f in filenames:
            if f.endswith(".py"):
                full_path = Path(dirpath) / f
                try:
                    rel_path = full_path.relative_to(root).as_posix()
                except ValueError:
                    rel_path = full_path.as_posix()

                py_files[rel_path] = full_path
                symbols, imports = _extract_python_ast(full_path, root)
                graph.symbols[rel_path] = symbols
                imports_map[rel_path] = imports

    # Resolve module imports to local file paths
    # Create module lookup table: "core.policy" -> "core/policy.py", "policy" -> "core/policy.py"
    mod_lookup: dict[str, str] = {}
    for rel_path in py_files.keys():
        clean_path = rel_path[:-3] if rel_path.endswith(".py") else rel_path
        mod_dotted = clean_path.replace("/", ".")
        mod_lookup[mod_dotted] = rel_path
        base_name = Path(rel_path).stem
        if base_name not in mod_lookup:
            mod_lookup[base_name] = rel_path

    for rel_path, imported_modules in imports_map.items():
        for mod in imported_modules:
            target_file = mod_lookup.get(mod)
            if not target_file:
                # Try prefix match (e.g. core.policy.evaluate_action -> core.policy)
                parts = mod.split(".")
                for i in range(len(parts) - 1, 0, -1):
                    prefix = ".".join(parts[:i])
                    if prefix in mod_lookup:
                        target_file = mod_lookup[prefix]
                        break

            if target_file and target_file != rel_path:
                graph.add_dependency(from_file=rel_path, to_file=target_file)

    return graph


_GRAPH_CACHE: tuple[str, float, DependencyGraph] | None = None


def get_dependency_graph(root_dir: str | Path | None = None, force_refresh: bool = False) -> DependencyGraph:
    """Retrieves or builds the dependency graph for the given workspace.

    Resolution Priority:
    1. Graphify output (if graphify-out/graph.json or .graphify/graph.json exists)
    2. Native stdlib AST engine (runs on-the-fly with ZERO dependencies)

    Note: Users do NOT need Graphify installed or running. The native engine
    provides instant blast-radius evaluation out of the box.
    """
    global _GRAPH_CACHE
    root = Path(root_dir).resolve() if root_dir else Path.cwd().resolve()
    cache_key = str(root)

    # Check cache if valid
    if not force_refresh and _GRAPH_CACHE is not None:
        cached_key, cached_time, cached_graph = _GRAPH_CACHE
        if cached_key == cache_key:
            return cached_graph

    # 1. Check for Graphify output
    for candidate in GRAPHIFY_CANDIDATE_PATHS:
        full_candidate = root / candidate
        if full_candidate.is_file():
            graph = _load_graphify_graph(full_candidate, root)
            if graph is not None:
                _GRAPH_CACHE = (cache_key, full_candidate.stat().st_mtime, graph)
                return graph

    # 2. Fall back to Native AST Engine (pure stdlib, zero setup)
    graph = _build_native_ast_graph(root)
    _GRAPH_CACHE = (cache_key, 0.0, graph)
    return graph


def evaluate_blast_radius(
    target_path: str | Path,
    root_dir: str | Path | None = None,
) -> BlastRadius:
    """Evaluates the blast radius of modifying a target file or symbol."""
    graph = get_dependency_graph(root_dir)
    return graph.compute_blast_radius(str(target_path))


def check_blast_radius_safety(
    target_path: str | Path,
    inspected_paths: set[str] | None = None,
    root_dir: str | Path | None = None,
    threshold: str = "HIGH",
) -> tuple[bool, str]:
    """Evaluates whether mutating `target_path` is safe with respect to inspected callers.

    Returns:
        (is_safe, advisory_message)
    """
    inspected = inspected_paths or set()
    norm_inspected = {str(Path(p).as_posix()).lower() for p in inspected if p}

    br = evaluate_blast_radius(target_path, root_dir)

    # If blast radius is below threshold, pass silently
    level_weights = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}
    target_weight = level_weights.get(br.level, 0)
    thresh_weight = level_weights.get(threshold, 3)

    if target_weight < thresh_weight or br.score == 0:
        return True, ""

    # Check if any dependent callers have been inspected
    inspected_dependents = [
        dep for dep in br.direct_dependents
        if any(dep.lower() in p or p.endswith("/" + dep.lower()) for p in norm_inspected)
    ]

    if not inspected_dependents:
        # None of the callers have been read
        return (
            False,
            f"BLAST RADIUS WARNING: '{br.target}' is imported by {br.score} files "
            f"({', '.join(br.direct_dependents[:3])}{'...' if len(br.direct_dependents) > 3 else ''}) "
            "but none of them have been inspected in this session. "
            "Verify caller contracts before altering public signatures.",
        )

    return True, f"Blast radius: {len(inspected_dependents)}/{br.score} callers inspected."


# CLI entry point
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Universal Frontier Harness — Graph-Aware Intelligence Engine")
        print("Usage:")
        print("  python -m core.graph_intel status [dir]")
        print("  python -m core.graph_intel blast-radius <file> [dir]")
        print("  python -m core.graph_intel dependents <file> [dir]")
        sys.exit(0)

    cmd = sys.argv[1].lower()
    target = sys.argv[2] if len(sys.argv) > 2 else ""
    cwd = sys.argv[3] if len(sys.argv) > 3 else "."

    if cmd == "status":
        graph = get_dependency_graph(cwd)
        print(f"Graph Intelligence Engine Status:")
        print(f"  Source Engine: {graph.source.upper()}")
        print(f"  Indexed Files: {len(graph.symbols)}")
        print(f"  Dependency Links: {sum(len(v) for v in graph.dependencies.values())}")
        print(f"  External Graphify Required: NO (Native AST fallback active)")
    elif cmd in ("blast-radius", "br"):
        if not target:
            print("Error: missing target file")
            sys.exit(1)
        br = evaluate_blast_radius(target, cwd)
        print(json.dumps(br.to_dict(), indent=2))
    elif cmd == "dependents":
        if not target:
            print("Error: missing target file")
            sys.exit(1)
        br = evaluate_blast_radius(target, cwd)
        print(f"Dependents for {target}:")
        for dep in br.transitive_dependents:
            print(f"  <- {dep}")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
