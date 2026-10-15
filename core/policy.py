"""Deterministic policy engine and action guard.

Evaluates proposed tool actions against:
1. Mode restrictions (read-only modes block write/execute)
2. Read-before-write invariant (cannot modify an existing file without reading it first)
3. Scope fencing (cannot modify files outside allowed_write_scope)
4. Circuit breaker (halts repeated execution of identical failing actions)
"""

from __future__ import annotations

import hashlib
import json
import os
import shlex
from dataclasses import dataclass, field
from pathlib import Path

READ_ONLY_MODES = frozenset({"plan-only", "review-only", "recon", "audit"})


@dataclass
class Action:
    kind: str  # read, write, execute, network, unknown
    tool: str
    paths: list[str] = field(default_factory=list)
    command: str = ""
    argv: list[str] = field(default_factory=list)


def action_fingerprint(tool: str, args: dict | str) -> str:
    """Computes a deterministic hash for a tool call to detect repetition."""
    raw = json.dumps({"tool": tool, "args": args}, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def classify_action(tool: str, args: dict) -> Action:
    """Normalizes host tool calls into a unified Action model."""
    tool_lower = tool.lower()

    if tool_lower in ("view_file", "read_file", "read_resource", "get_scene_info", "get_object_info"):
        path = args.get("AbsolutePath") or args.get("TargetFile") or args.get("path") or ""
        return Action(kind="read", tool=tool, paths=[path] if path else [])

    if tool_lower in ("write_to_file", "replace_file_content", "edit_file", "create_file"):
        path = args.get("TargetFile") or args.get("AbsolutePath") or args.get("path") or ""
        return Action(kind="write", tool=tool, paths=[path] if path else [])

    if tool_lower in ("run_command", "execute_command", "bash", "powershell"):
        cmd = args.get("CommandLine") or args.get("command") or ""
        argv = []
        try:
            argv = shlex.split(cmd, posix=(os.name != "nt"))
        except Exception:
            argv = cmd.split()
        return Action(kind="execute", tool=tool, command=cmd, argv=argv)

    if tool_lower in ("search_web", "read_url_content"):
        return Action(kind="network", tool=tool)

    return Action(kind="unknown", tool=tool)


def evaluate_action(
    action: Action,
    mode: str = "implement",
    allowed_scope: list[str] | None = None,
    reads: set[str] | None = None,
    failed_fingerprints: set[str] | None = None,
    fingerprint: str = "",
) -> tuple[str, str]:
    """Evaluates an action against deterministic safety invariants."""
    reads = reads or set()
    failed_fingerprints = failed_fingerprints or set()
    allowed_scope = allowed_scope or []

    # 1. Mode restriction check
    if mode in READ_ONLY_MODES:
        if action.kind in ("write", "execute", "network"):
            return "deny", f"Mode '{mode}' is read-only; {action.kind} actions are prohibited."

    # 2. Circuit breaker check
    if fingerprint and fingerprint in failed_fingerprints:
        return "deny", f"Circuit breaker: tool call fingerprint '{fingerprint}' previously failed. Repetition is blocked."

    # 3. Read-before-write invariant check
    if action.kind == "write" and action.paths:
        target = Path(action.paths[0]).resolve()
        if target.is_file():
            # Check if this file was recorded as read
            normalized_reads = {str(Path(r).resolve()) for r in reads if r}
            if str(target) not in normalized_reads:
                return (
                    "deny",
                    f"Read-before-write violation: file '{target.name}' exists but has not been inspected in this session. Read it first.",
                )

    # 4. Scope fencing check
    if action.kind == "write" and allowed_scope and action.paths:
        target = str(Path(action.paths[0]).resolve()).lower()
        matched = False
        for pattern in allowed_scope:
            normalized_pattern = str(Path(pattern).resolve()).lower()
            if target == normalized_pattern or target.startswith(normalized_pattern + os.sep):
                matched = True
                break
        if not matched:
            scope_str = ", ".join(allowed_scope)
            return "deny", f"Scope fencing violation: target '{action.paths[0]}' is outside allowed write scope: [{scope_str}]."

    return "allow", "Action conforms to active policy."
