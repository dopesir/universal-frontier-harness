#!/usr/bin/env python3
"""Pre-tool hook: Enforces deterministic action policies before tool dispatch.

Enforces:
1. Read-before-write (cannot mutate existing file without prior inspection)
2. Scope fencing (cannot modify files outside allowed_write_scope)
3. Mode restrictions (read-only modes fail closed on mutation/execution)
4. Circuit breaker (halts repeated identical failing commands)
"""

import json
import os
import sys
from pathlib import Path

# Robust core import resolution (supports both root and .agents layouts)
_here = Path(__file__).resolve().parent
for _candidate in [_here.parent, _here.parent.parent]:
    if (_candidate / "core").is_dir() and str(_candidate) not in sys.path:
        sys.path.insert(0, str(_candidate))

from core.contract import load_contract
from core.policy import action_fingerprint, classify_action, evaluate_action


def get_session_dir(root: Path, conversation_id: str = "") -> Path:
    base = root / ".agents" / "sessions"
    if conversation_id:
        return base / conversation_id
    return base / "default"


def record_read(session_dir: Path, path: str):
    session_dir.mkdir(parents=True, exist_ok=True)
    reads_file = session_dir / "reads.jsonl"
    with open(reads_file, "a", encoding="utf-8") as f:
        f.write(json.dumps({"path": str(Path(path).resolve())}) + "\n")


def load_reads(session_dir: Path) -> set[str]:
    reads_file = session_dir / "reads.jsonl"
    if not reads_file.is_file():
        return set()
    reads = set()
    try:
        with open(reads_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        reads.add(data.get("path", ""))
                    except Exception:
                        pass
    except Exception:
        pass
    return reads


def load_failed_fingerprints(session_dir: Path) -> set[str]:
    fail_file = session_dir / "failures.jsonl"
    if not fail_file.is_file():
        return set()
    fps = set()
    try:
        with open(fail_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        fp = data.get("fingerprint")
                        if fp:
                            fps.add(fp)
                    except Exception:
                        pass
    except Exception:
        pass
    return fps


def main():
    if sys.stdin.isatty():
        payload = {}
    else:
        try:
            payload = json.load(sys.stdin)
        except Exception:
            payload = {}

    tool_call = payload.get("toolCall", {})
    tool_name = tool_call.get("name", "")
    tool_args = tool_call.get("args", {})

    if not tool_name:
        print(json.dumps({"decision": "allow"}))
        return

    conv_id = payload.get("conversationId", "")
    workspace_paths = payload.get("workspacePaths", [])
    root = Path(workspace_paths[0]) if workspace_paths else Path.cwd()
    session_dir = get_session_dir(root, conv_id)

    action = classify_action(tool_name, tool_args)

    # Track reads
    if action.kind == "read" and action.paths:
        for p in action.paths:
            record_read(session_dir, p)

    contract = load_contract(session_dir) or load_contract(root / ".agents")
    mode = contract.get("mode", "implement")
    allowed_scope = contract.get("allowed_write_scope", [])

    reads = load_reads(session_dir)
    failed_fps = load_failed_fingerprints(session_dir)
    fingerprint = action_fingerprint(tool_name, tool_args)

    decision, reason = evaluate_action(
        action=action,
        mode=mode,
        allowed_scope=allowed_scope,
        reads=reads,
        failed_fingerprints=failed_fps,
        fingerprint=fingerprint,
    )

    result = {"decision": decision}
    if decision != "allow":
        result["reason"] = reason

    print(json.dumps(result))


if __name__ == "__main__":
    main()
