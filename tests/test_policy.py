"""Tests for core.policy action evaluation and safety guards."""

import tempfile
import unittest
from pathlib import Path

from core.policy import Action, action_fingerprint, evaluate_action


class TestPolicy(unittest.TestCase):
    def test_read_before_write_blocks_unread_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("existing content")
            f_path = f.name
        try:
            action = Action(kind="write", tool="write_to_file", paths=[f_path])
            decision, reason = evaluate_action(action, reads=set())
            self.assertEqual(decision, "deny")
            self.assertIn("Read-before-write violation", reason)

            # Now record read and test again
            decision, _ = evaluate_action(action, reads={f_path})
            self.assertEqual(decision, "allow")
        finally:
            Path(f_path).unlink(missing_ok=True)

    def test_scope_fencing(self):
        action = Action(kind="write", tool="write_to_file", paths=["/project/src/auth/secret.key"])
        allowed = ["/project/src/ui", "/project/src/components"]

        decision, reason = evaluate_action(action, allowed_scope=allowed)
        self.assertEqual(decision, "deny")
        self.assertIn("Scope fencing violation", reason)

    def test_read_only_mode(self):
        action = Action(kind="write", tool="write_to_file", paths=["some_file.py"])
        decision, reason = evaluate_action(action, mode="plan-only")
        self.assertEqual(decision, "deny")
        self.assertIn("read-only", reason)

    def test_circuit_breaker(self):
        fp = action_fingerprint("run_command", {"command": "failing_cmd"})
        action = Action(kind="execute", tool="run_command", command="failing_cmd")

        decision, reason = evaluate_action(
            action,
            failed_fingerprints={fp},
            fingerprint=fp,
        )
        self.assertEqual(decision, "deny")
        self.assertIn("Circuit breaker", reason)


if __name__ == "__main__":
    unittest.main()
