"""Anthropic Claude Code and OpenCode universal adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.policy import Action


class ClaudeCodeAdapter:
    """Adapts Claude Code CLI hooks and tool formats."""

    @staticmethod
    def parse_tool_payload(payload: dict[str, Any]) -> tuple[Action, str, Path]:
        tool_name = payload.get("tool_name", payload.get("name", ""))
        tool_input = payload.get("tool_input", payload.get("input", {}))
        cwd = Path(payload.get("cwd", Path.cwd()))

        paths = []
        if "file_path" in tool_input:
            paths.append(tool_input["file_path"])
        elif "path" in tool_input:
            paths.append(tool_input["path"])

        kind = "unknown"
        if tool_name in ("View", "ReadFile"):
            kind = "read"
        elif tool_name in ("Edit", "WriteFile"):
            kind = "write"
        elif tool_name in ("Bash", "Terminal"):
            kind = "execute"

        action = Action(kind=kind, tool=tool_name, paths=paths, command=tool_input.get("command", ""))
        return action, "claude-session", cwd


class GenericAgentAdapter:
    """Fallback adapter for generic JSON-RPC agent environments."""

    @staticmethod
    def parse_tool_payload(payload: dict[str, Any]) -> tuple[Action, str, Path]:
        tool = payload.get("tool", payload.get("name", "unknown"))
        args = payload.get("arguments", payload.get("args", {}))
        return Action(kind="unknown", tool=tool), "generic", Path.cwd()
