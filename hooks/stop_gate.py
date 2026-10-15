#!/usr/bin/env python3
"""Stop hook: Zero-bypass mechanical completion gate.

Intercepts the agent's turn completion attempt.
Ensures no task is declared complete without fresh, passing evidence.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path for core imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.stop_gate import evaluate_stop


def get_session_dir(root: Path, conversation_id: str = "") -> Path:
    base = root / ".agents" / "sessions"
    if conversation_id:
        return base / conversation_id
    return base / "default"


def count_stop_cycles(session_dir: Path) -> int:
    log_file = session_dir / "stop_gate.log"
    if not log_file.is_file():
        return 0
    try:
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            return sum(1 for line in f if line.strip())
    except Exception:
        return 0


def log_stop_cycle(session_dir: Path, decision: str, reason: str):
    session_dir.mkdir(parents=True, exist_ok=True)
    log_file = session_dir / "stop_gate.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps({"decision": decision, "reason": reason}) + "\n")


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return

    conv_id = payload.get("conversationId", "")
    workspace_paths = payload.get("workspacePaths", [])
    root = Path(workspace_paths[0]) if workspace_paths else Path.cwd()
    session_dir = get_session_dir(root, conv_id)

    cycle_count = count_stop_cycles(session_dir)
    result = evaluate_stop(session_dir, cycle_count=cycle_count)

    log_stop_cycle(session_dir, result.get("decision", "allow"), result.get("reason", ""))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
