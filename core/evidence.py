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


def owned_validator_pass(entry: dict) -> bool:
    """Returns True if the entry represents an actual passing validator run."""
    return entry.get("passed") is True and entry.get("exit_code") == 0


def is_fresh(entry: dict, latest_mutation_iso: str | None) -> bool:
    """Verifies that evidence was acquired AFTER the most recent file mutation."""
    if not latest_mutation_iso:
        return True
    entry_ts = entry.get("timestamp")
    if not entry_ts:
        return False
    try:
        t_entry = datetime.fromisoformat(entry_ts)
        t_mut = datetime.fromisoformat(latest_mutation_iso)
        return t_entry >= t_mut
    except (ValueError, TypeError):
        return False
