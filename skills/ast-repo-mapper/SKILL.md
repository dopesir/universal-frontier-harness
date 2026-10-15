---
name: ast-repo-mapper
description: High-density symbol map generator using AST parsing. Generates a compact structural index of classes, methods, and functions across the entire codebase in seconds.
---

# AST Repository Mapper

Generates high-density structural outlines of repositories without dumping full file contents into the LLM context.

## Usage
```bash
python skills/ast-repo-mapper/scripts/repo_map.py [directory] [--max-files 50]
```

## Features
- Parses Python class definitions, method signatures, and top-level functions using native `ast`.
- Parses JavaScript / TypeScript exports and function signatures using regex extractors.
- Output is formatted for optimal LLM context packing (<500 tokens for a full module tree).
