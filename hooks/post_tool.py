#!/usr/bin/env python3
"""Post-tool hook: Deterministic validation and evidence ledger recorder.

Runs immediately after tool execution:
1. Runs sub-15ms fast AST linter on mutated files
2. Appends passing test outputs to evidence.jsonl
3. Logs failures and action fingerprints to failures.jsonl to feed circuit breakers
4. Records mutation timestamps to enforce evidence freshness
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Robust core import resolution (supports both root and .agents layouts)
_here = Path(__file__).resolve().parent
for _candidate in [_here.parent, _here.parent.parent]:
    if (_candidate / "core").is_dir() and str(_candidate) not in sys.path:
        sys.path.insert(0, str(_candidate))

from core.evidence import append_evidence
from core.fast_lint import lint_file
from core.policy import action_fingerprint, classify_action


def get_session_dir(root: Path, conversation_id: str = "") -> Path:
    base = root / ".agents" / "sessions"
    if conversation_id:
        return base / conversation_id
    return base / "default"


def record_mutation(session_dir: Path, file_path: str):
    session_dir.mkdir(parents=True, exist_ok=True)
    mutations_file = session_dir / "mutations.jsonl"
    with open(mutations_file, "a", encoding="utf-8") as f:
        f.write(
            json.dumps({
                "path": str(Path(file_path).resolve()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            + "\n"
        )


def record_failure(session_dir: Path, fingerprint: str, tool: str, error: str):
    session_dir.mkdir(parents=True, exist_ok=True)
    failures_file = session_dir / "failures.jsonl"
    with open(failures_file, "a", encoding="utf-8") as f:
        f.write(
            json.dumps({
                "fingerprint": fingerprint,
                "tool": tool,
                "error": error[:300],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "resolved": False,
            })
            + "\n"
        )


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
    tool_output = payload.get("toolOutput", "")

    conv_id = payload.get("conversationId", "")
    workspace_paths = payload.get("workspacePaths", [])
    root = Path(workspace_paths[0]) if workspace_paths else Path.cwd()
    session_dir = get_session_dir(root, conv_id)

    action = classify_action(tool_name, tool_args)
    fingerprint = action_fingerprint(tool_name, tool_args)

    injected_messages = []

    # 1. File write handling: fast AST linting and mutation tracking
    if action.kind == "write" and action.paths:
        for p in action.paths:
            record_mutation(session_dir, p)
            # Run sub-15ms fast AST linter
            lint_res = lint_file(p)
            if not lint_res.valid:
                err_summary = "; ".join(lint_res.errors[:2])
                record_failure(session_dir, fingerprint, tool_name, f"Syntax/AST error in {p}: {err_summary}")
                injected_messages.append(
                    f"[Universal Harness AST Guard] SYNTAX DEFECT DETECTED in '{p}' ({lint_res.file_type}):\n"
                    f"{lint_res.errors[0]}\n"
                    "Repair this syntax defect before running tests or declaring completion."
                )

    # 2. Command execution handling: test evidence and failure logging
    if action.kind == "execute":
        exit_code = payload.get("exitCode", 0)
        output_str = str(tool_output)

        # Check for test failure
        if exit_code != 0 or "FAIL" in output_str or "Error:" in output_str:
            record_failure(session_dir, fingerprint, tool_name, output_str)
        elif exit_code == 0 and any(kw in action.command.lower() for kw in ("test", "pytest", "unittest", "check")):
            # Record passing evidence entry
            append_evidence(
                session_dir,
                {
                    "criterion_id": "AUTO_TEST",
                    "validator_id": action.command,
                    "command": action.command,
                    "exit_code": exit_code,
                    "passed": True,
                    "stdout_summary": output_str[:200],
                },
            )

    result = {}
    if injected_messages:
        result["injectSteps"] = [{"ephemeralMessage": msg} for msg in injected_messages]

    print(json.dumps(result))


if __name__ == "__main__":
    main()
