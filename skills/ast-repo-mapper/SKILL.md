---
name: ast-repo-mapper
description: High-density symbol map generator using AST parsing. Generates a compact structural index of classes, methods, and functions across the entire codebase in seconds.
---

# AST Repository Mapper

Generates high-density structural outlines of repositories without dumping full file contents into the LLM context.

## Usage
```bash
python skills/ast-repo-mapper/scripts/repo_map.py [directory] [--max-files 50] [--with-blast-radius]
```

## Features
- Parses Python class definitions, method signatures, and top-level functions using native `ast`.
- Parses JavaScript / TypeScript exports and function signatures using regex extractors.
- Annotates files with **Blast Radius** risk levels (NONE, LOW, MEDIUM, HIGH) and dependent caller counts via `core.graph_intel` when `--with-blast-radius` is supplied.
- Output is formatted for optimal LLM context packing (<500 tokens for a full module tree).
- **Zero External Dependencies**: Operates 100% with Python stdlib; no external graph engines or setup required. Auto-consumes Graphify output if present.
