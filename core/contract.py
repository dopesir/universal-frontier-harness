"""Formal task contract and acceptance criteria manager.

Defines the explicit boundary, write scope, acceptance criteria,
and required validators for every non-trivial task.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Criterion:
    id: str
    statement: str
    required_validator_id: str = ""


@dataclass
class Contract:
    task_id: str
    description: str
    acceptance_criteria: list[Criterion] = field(default_factory=list)
    allowed_write_scope: list[str] = field(default_factory=list)
    required_validators: list[str] = field(default_factory=list)
    mode: str = "implement"  # plan-only, implement, review-only, repair


def load_contract(session_dir: str | Path) -> dict:
    """Loads contract from session directory.
    
    Returns:
        dict: contract data if found, or empty dict if no contract file exists.
    Raises:
        ValueError: if contract file exists on disk but is corrupted or contains invalid JSON.
    """
    path = Path(session_dir) / "contract.json"
    if not path.is_file():
        return {}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Corrupted contract file '{path}': {e}") from e
    except OSError as e:
        raise ValueError(f"Inaccessible contract file '{path}': {e}") from e


def save_contract(session_dir: str | Path, contract: Contract | dict) -> Path:
    """Saves contract to session directory."""
    path = Path(session_dir) / "contract.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = asdict(contract) if isinstance(contract, Contract) else contract
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path


def validate_contract(data: dict) -> list[str]:
    """Validates contract structure and required fields."""
    errors = []
    if not (data.get("task_id") or data.get("id")):
        errors.append("Contract missing required 'task_id' or 'id'")
    if not data.get("description"):
        errors.append("Contract missing required 'description'")
    if "acceptance_criteria" in data and not isinstance(data["acceptance_criteria"], list):
        errors.append("'acceptance_criteria' must be a list")
    if "allowed_write_scope" in data and not isinstance(data["allowed_write_scope"], list):
        errors.append("'allowed_write_scope' must be a list")
    return errors
