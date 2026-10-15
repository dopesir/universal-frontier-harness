---
name: engineering-recon
description: Systematic workspace orientation and reconnaissance procedure. Discovers project structure, tooling, conventions, and existing instructions before any changes are made.
---

# Engineering Reconnaissance

## 1. Orientation Protocol
Before modifying any files:
1. Inspect directory structure, package manifests (`pyproject.toml`, `package.json`, `Cargo.toml`).
2. Identify existing tests and build commands.
3. Check for existing project conventions (indentation, typing, naming).
4. Never assume a framework or structure without empirical tool evidence.

## 2. Output Format
Produce a concise summary:
- **Language & Runtime**: e.g. Python 3.11 / Node 20
- **Build & Test Runner**: e.g. `pytest`, `npm test`
- **Key Modules**: Primary entry points and critical domain paths
- **Identified Constraints**: Existing linter rules, typing configs
