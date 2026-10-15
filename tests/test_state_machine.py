"""Tests for core.state_machine lifecycle progression."""

import unittest

from core.state_machine import LifecycleState, can_transition, validate_transition


class TestStateMachine(unittest.TestCase):
    def test_valid_progression(self):
        # UNINITIALIZED -> GROUNDED -> PLANNED -> MUTATING -> VALIDATING -> COMPLETED
        self.assertTrue(can_transition(LifecycleState.UNINITIALIZED, LifecycleState.GROUNDED))
        self.assertTrue(can_transition(LifecycleState.GROUNDED, LifecycleState.PLANNED))
        self.assertTrue(can_transition(LifecycleState.PLANNED, LifecycleState.MUTATING))
        self.assertTrue(can_transition(LifecycleState.MUTATING, LifecycleState.VALIDATING))
        self.assertTrue(can_transition(LifecycleState.VALIDATING, LifecycleState.COMPLETED))

    def test_skipping_phases_is_rejected(self):
        # Cannot jump from UNINITIALIZED directly to MUTATING
        self.assertFalse(can_transition(LifecycleState.UNINITIALIZED, LifecycleState.MUTATING))
        valid, reason = validate_transition(LifecycleState.UNINITIALIZED, LifecycleState.MUTATING)
        self.assertFalse(valid)
        self.assertIn("Invalid state transition", reason)

        # Cannot jump from GROUNDED directly to COMPLETED
        self.assertFalse(can_transition(LifecycleState.GROUNDED, LifecycleState.COMPLETED))


if __name__ == "__main__":
    unittest.main()
