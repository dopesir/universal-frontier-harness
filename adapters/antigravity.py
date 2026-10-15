"""Google Antigravity host envelope and hook bridge."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.policy import Action, classify_action


class AntigravityAdapter:
    """Adapts Antigravity tool payloads and hook contracts."""

    @staticmethod
    def parse_tool_payload(payload: dict[str, Any]) -> tuple[Action, str, Path]:
        tool_call = payload.get("toolCall", {})
        tool_name = tool_call.get("name", "")
        tool_args = tool_call.get("args", {})
        conv_id = payload.get("conversationId", "default")
        paths = payload.get("workspacePaths", [])
        root = Path(paths[0]) if paths else Path.cwd()

        action = classify_action(tool_name, tool_args)
        return action, conv_id, root
