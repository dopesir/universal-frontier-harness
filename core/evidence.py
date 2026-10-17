"""Cryptographic and timestamped evidence ledger.

Tracks executable verification outcomes in an append-only JSONL format.
Enforces freshness guarantees: evidence is stale if acquired prior to the latest file mutation.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class EvidenceEntry:
    criterion_id: str
    validator_id: str
    command: str
    exit_code: int
    passed: bool
    task_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    stdout_summary: str = ""
    file_hashes: dict[str, str] = field(default_factory=dict)


def load_evidence(session_dir: str | Path) -> list[dict]:
    """Loads all evidence records from the session evidence ledger."""
    path = Path(session_dir) / "evidence.jsonl"
    if not path.is_file():
        return []

    records = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except OSError:
        return []
    return records


def append_evidence(session_dir: str | Path, entry: EvidenceEntry | dict) -> None:
    """Appends an evidence record to the immutable session ledger."""
    path = Path(session_dir) / "evidence.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)

    data = asdict(entry) if isinstance(entry, EvidenceEntry) else entry
    if "timestamp" not in data:
        data["timestamp"] = datetime.now(timezone.utc).isoformat()

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")


def owned_validator_pass(entry: dict, task_id: str = "") -> bool:
    """Returns True if the entry represents an actual, verified passing validator execution.
    
    Guarantees:
    - Must be a dictionary.
    - If task_id is provided, entry task_id must match if present.
    - passed must be exact boolean True (not truthy strings or objects).
    - exit_code must be exact integer 0 (not None, not strings like "0").
    - command must be a non-empty string.
    - Text alone without exit_code == 0 is never accepted as passing evidence.
    """
    if not isinstance(entry, dict):
        return False
    if task_id and entry.get("task_id") and entry.get("task_id") != task_id:
        return False
    if entry.get("passed") is not True:
        return False
    if type(entry.get("exit_code")) is not int or entry.get("exit_code") != 0:
        return False
    cmd = entry.get("command")
    if not cmd or not str(cmd).strip():
        return False
    return True


def is_fresh(entry: dict, latest_mutation_iso: str | None) -> bool:
    """Verifies that evidence was acquired AFTER the most recent file mutation.
    
    Returns False if timestamp is missing or malformed (fails closed).
    """
    if not latest_mutation_iso:
        return True
    if not isinstance(entry, dict):
        return False
    entry_ts = entry.get("timestamp")
    if not entry_ts:
        return False
    try:
        t_entry = datetime.fromisoformat(entry_ts)
        t_mut = datetime.fromisoformat(latest_mutation_iso)
        return t_entry >= t_mut
    except (ValueError, TypeError):
        return False
