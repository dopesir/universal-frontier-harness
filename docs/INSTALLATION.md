# Installation & Deployment Guide

This guide explains how to install, configure, verify, and uninstall the Universal Frontier Harness across development projects.

---

## 1. Quickstart Installation

The harness is installed using the standard installer script:

```bash
python scripts/init_harness.py /path/to/your/project
```

To install directly into the current directory:
```bash
python scripts/init_harness.py .
```

---

## 2. Installed Layout

When installed, the harness creates a project-local runtime structure under `.agents/`:

```
your-project/
├── .agents/
│   ├── rules/
│   │   ├── AGENTS.md          # 6 Non-negotiable engineering invariants
│   │   └── GEMINI.md          # Gemini / Antigravity entry point
│   ├── core/                  # Core reliability runtime (0 external dependencies)
│   │   ├── contract.py        # Task contract & acceptance criteria manager
│   │   ├── evidence.py        # Append-only cryptographic evidence ledger
│   │   ├── fast_lint.py       # Sub-15ms AST syntax & delimiter validator
│   │   ├── graph_intel.py     # Zero-dependency dependency graph & blast radius engine
│   │   ├── policy.py          # Action gatekeeper (read-before-write, scope fencing)
│   │   ├── state_machine.py   # Task lifecycle finite state machine (FSM)
│   │   ├── stop_gate.py       # Completion gatekeeper
│   │   └── __init__.py
│   ├── hooks/                 # Active runtime hooks
│   │   ├── hooks.json         # Hook event triggers manifest
│   │   ├── pre_invocation.py  # Recency reminder injector
│   │   ├── pre_tool.py        # Action policy gatekeeper
│   │   ├── post_tool.py       # Syntax validator & evidence recorder
│   │   └── stop_gate.py       # Completion gatekeeper hook
│   └── memory/                # Persistent task state
│       ├── task_state.md      # Active objective, phase, and progress
│       ├── decisions.md       # Architecture Decision Records (ADRs)
│       ├── constraints.md     # Scope and boundaries
│       ├── unresolved.md      # Unresolved defects ledger
│       └── verification.md    # Evidence verification log
```

---

## 3. Command-Line Options

| Flag | Purpose | Default |
| :--- | :--- | :--- |
| `target` | Root directory of the target project | Current directory (`.`) |
| `--dry-run` | Preview all actions without modifying the filesystem | Disabled |
| `--overwrite` | Allow overwriting pre-existing rules and hooks | Disabled (safe by default) |
| `--no-backup` | Skip creating `.bak.<timestamp>` files when overwriting | Backups enabled by default |
| `--uninstall` | Safely remove harness runtime while preserving memory | Disabled |
| `--include-cursor` | Install `.cursorrules` template at project root | Disabled |
| `--include-windsurf`| Install `.windsurfrules` template at project root | Disabled |

---

## 4. Safety Guarantees

1. **Safe by Default**: If target project already contains `.agents/rules/AGENTS.md` or `.agents/hooks/hooks.json`, the installer preserves existing files and reports `[SKIP]`.
2. **Automatic Timestamped Backups**: When `--overwrite` is specified, any existing file is preserved in `filename.bak.<timestamp>` before replacement.
3. **Dry-Run Mode**: Run with `--dry-run` to see exactly what files will be created or skipped before touching disk.
4. **Clean Rollback**: If an error occurs during installation, created files are automatically rolled back.

---

## 5. Uninstallation

To cleanly remove the harness runtime from a project:

```bash
python scripts/init_harness.py /path/to/your/project --uninstall
```

This removes `.agents/core/`, `.agents/hooks/`, and `.agents/rules/` while **strictly preserving** `.agents/memory/` and all user notes.
