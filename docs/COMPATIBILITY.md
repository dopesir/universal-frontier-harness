# Host & Platform Compatibility Matrix

This document details the verified compatibility status of the Universal Frontier Harness across operating systems, Python runtimes, and host agent environments.

---

## 1. Operating Systems & Python Runtimes

| Operating System | Python 3.10 | Python 3.11 | Python 3.12 | Python 3.13 | CI Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Ubuntu Linux (22.04 LTS)** | :white_check_mark: Verified | :white_check_mark: Verified | :white_check_mark: Verified | :white_check_mark: Verified | [Active CI Matrix](https://github.com/dopesir/universal-frontier-harness/actions) |
| **macOS (Apple Silicon & Intel)** | :white_check_mark: Verified | :white_check_mark: Verified | :white_check_mark: Verified | :white_check_mark: Verified | [Active CI Matrix](https://github.com/dopesir/universal-frontier-harness/actions) |
| **Windows 11 / 10** | :white_check_mark: Verified | :white_check_mark: Verified | :white_check_mark: Verified | :white_check_mark: Verified | [Active CI Matrix](https://github.com/dopesir/universal-frontier-harness/actions) |

All 50 automated tests execute identically across Windows, macOS, and Linux.

---

## 2. Agent Host Environments

| Agent Host / Tool | Integration Mechanism | Status | Notes |
| :--- | :--- | :---: | :--- |
| **Google Antigravity** | `.agents/rules/AGENTS.md` + `.agents/hooks/hooks.json` | :white_check_mark: **Full Support** | Native plugin structure, pre/post tool hooks, stop gate interceptor. |
| **Anthropic Claude Code** | `.agents/rules/AGENTS.md` + `adapters/claude_code.py` | :white_check_mark: **Verified** | Standard tool envelope mapping (View, Edit, Bash). |
| **Cursor** | `.cursorrules` / `.agents/rules/` | :white_check_mark: **Verified** | Drop-in rule templates under `templates/.cursorrules`. |
| **Windsurf (Codeium)** | `.windsurfrules` / `.agents/rules/` | :white_check_mark: **Verified** | Drop-in rule templates under `templates/.windsurfrules`. |
| **Aider / OpenHands** | Repo-level rules + CLI invocation | :white_check_mark: **Verified** | Prompt-level invariants + external validator. |

---

## 3. Language & File Format Validation Support

| Language | Validation Engine | Level | Detection Scope |
| :--- | :--- | :--- | :--- |
| **Python** (`.py`) | Standard `ast.parse` | `ast_parse` | Full AST syntax parsing, indentation, tokens. |
| **JSON** (`.json`) | Standard `json.loads` | `full_json_parse` | Full document parse, trailing commas, quoting. |
| **JavaScript** (`.js`, `.jsx`, `.mjs`) | Lexical stack scanner | `delimiter_balance` | Structural delimiter & string literal pairing. |
| **TypeScript** (`.ts`, `.tsx`) | Lexical stack scanner | `delimiter_balance` | Structural delimiter & template literal pairing. |

---

## 4. Graph & Dependency Intelligence Support

| Intelligence Engine | Setup Required | Dependencies | Capability |
| :--- | :---: | :--- | :--- |
| **Native AST Engine** (`core.graph_intel`) | **None (Zero Setup)** | Pure Python Standard Library | Real-time import & symbol mapping, caller tracing, blast-radius calculation. Default engine. |
| **Graphify Ingestion Adapter** | **None** (Auto-detected) | None (consumes static JSON) | Ingests `graphify-out/graph.json` to augment AST maps with multi-language nodes and Louvain communities. |
