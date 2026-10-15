"""Lifecycle state machine for engineering tasks.

Enforces orderly progression:
UNINITIALIZED -> GROUNDED -> PLANNED -> MUTATING -> VALIDATING -> COMPLETED

Prevents skipping critical phases (e.g. jumping from UNINITIALIZED directly to MUTATING).
"""

from __future__ import annotations

from enum import Enum


class LifecycleState(str, Enum):
    UNINITIALIZED = "UNINITIALIZED"
    GROUNDED = "GROUNDED"
    PLANNED = "PLANNED"
    MUTATING = "MUTATING"
    VALIDATING = "VALIDATING"
    COMPLETED = "COMPLETED"


# Allowed state transitions
VALID_TRANSITIONS: dict[LifecycleState, set[LifecycleState]] = {
    LifecycleState.UNINITIALIZED: {LifecycleState.GROUNDED, LifecycleState.PLANNED},
    LifecycleState.GROUNDED: {LifecycleState.PLANNED, LifecycleState.MUTATING},
    LifecycleState.PLANNED: {LifecycleState.MUTATING, LifecycleState.VALIDATING},
    LifecycleState.MUTATING: {LifecycleState.VALIDATING, LifecycleState.MUTATING},
    LifecycleState.VALIDATING: {LifecycleState.MUTATING, LifecycleState.COMPLETED, LifecycleState.PLANNED},
    LifecycleState.COMPLETED: {LifecycleState.UNINITIALIZED},
}


def can_transition(current: LifecycleState | str, target: LifecycleState | str) -> bool:
    """Checks whether transitioning from current to target state is permissible."""
    try:
        curr_state = LifecycleState(current)
        targ_state = LifecycleState(target)
    except ValueError:
        return False

    return targ_state in VALID_TRANSITIONS.get(curr_state, set())


def validate_transition(current: str, target: str) -> tuple[bool, str]:
    """Validates transition and returns diagnostic reason on failure."""
    if not can_transition(current, target):
        return (
            False,
            f"Invalid state transition: Cannot transition from '{current}' to '{target}'. Required flow is UNINITIALIZED -> GROUNDED -> PLANNED -> MUTATING -> VALIDATING -> COMPLETED.",
        )
    return True, f"Transition from '{current}' to '{target}' accepted."
