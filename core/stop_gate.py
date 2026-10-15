"""Completion stop gatekeeper.

Intercepts agent turn termination to verify that:
1. Every declared acceptance criterion is backed by fresh, passing evidence in evidence.jsonl.
2. All required validators have executed and passed since the latest file mutation.
3. No known failures remain unresolved in failures.jsonl.
4. Circuit breaker: prevents infinite loops (max 3 consecutive continue cycles).

Returns:
    {"decision": "allow"} OR {"decision": "continue", "reason": "<explicit deficit>"}
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.contract import load_contract
from core.evidence import is_fresh, load_evidence, owned_validator_pass


def load_failures(session_dir: Path) -> list[dict]:
    """Loads failure records from the session failures ledger."""
    path = session_dir / "failures.jsonl"
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


def get_latest_mutation_time(session_dir: Path) -> str | None:
    """Gets the timestamp of the most recent file mutation recorded in session."""
    meta_path = session_dir / "mutations.jsonl"
    if not meta_path.is_file():
        return None
    latest = None
    try:
        with open(meta_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        ts = data.get("timestamp")
                        if ts:
                            latest = ts
                    except json.JSONDecodeError:
                        continue
    except OSError:
        return None
    return latest


def evaluate_stop(session_dir: str | Path, cycle_count: int = 0) -> dict[str, Any]:
    """Evaluates whether completion criteria are fully satisfied."""
    s_dir = Path(session_dir)
    if not s_dir.is_dir():
        # No session initialized; allow completion
        return {"decision": "allow"}

    contract = load_contract(s_dir)
    if not contract:
        # No contract active; allow completion
        return {"decision": "allow"}

    # Circuit breaker: stop after 3 cycles to avoid infinite loops
    if cycle_count >= 3:
        return {
            "decision": "continue",
            "reason": "Completion gate circuit breaker: 3+ verification cycles exhausted. Manual user review required.",
        }

    evidence = load_evidence(s_dir)
    failures = load_failures(s_dir)
    latest_mutation = get_latest_mutation_time(s_dir)

    # 1. Acceptance Criteria Verification
    criteria = contract.get("acceptance_criteria", [])
    unverified_criteria = []

    for idx, crit in enumerate(criteria):
        c_id = crit.get("id", f"AC{idx}") if isinstance(crit, dict) else str(crit)
        c_stmt = crit.get("statement", c_id) if isinstance(crit, dict) else str(crit)

        # Look for fresh passing evidence for this criterion
        has_pass = any(
            entry.get("criterion_id") == c_id and owned_validator_pass(entry) and is_fresh(entry, latest_mutation)
            for entry in evidence
        )
        if not has_pass:
            unverified_criteria.append(f"{c_id} ({c_stmt})")

    if unverified_criteria:
        deficit = "; ".join(unverified_criteria[:3])
        return {
            "decision": "continue",
            "reason": f"Completion blocked: The following acceptance criteria lack fresh passing evidence: {deficit}. Execute tests to verify before stopping.",
        }

    # 2. Required Validators Verification
    required_validators = contract.get("required_validators", [])
    missing_validators = []

    for val_id in required_validators:
        has_val_pass = any(
            entry.get("validator_id") == val_id and owned_validator_pass(entry) and is_fresh(entry, latest_mutation)
            for entry in evidence
        )
        if not has_val_pass:
            missing_validators.append(val_id)

    if missing_validators:
        val_str = ", ".join(missing_validators)
        return {
            "decision": "continue",
            "reason": f"Completion blocked: Required validator(s) have not passed after the latest code modification: {val_str}. Run the required validator suites.",
        }

    # 3. Unresolved Failures Check
    unresolved_failures = [f for f in failures if f.get("resolved") is not True]
    if unresolved_failures:
        err_snippets = "; ".join(f.get("error", "unresolved defect")[:60] for f in unresolved_failures[:2])
        return {
            "decision": "continue",
            "reason": f"Completion blocked: {len(unresolved_failures)} recorded failure(s) are unresolved: [{err_snippets}]. Fix and verify them before concluding.",
        }

    return {"decision": "allow"}
