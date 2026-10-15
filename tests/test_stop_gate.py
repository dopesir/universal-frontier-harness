"""Tests for core.stop_gate completion gatekeeper."""

import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from core.contract import Contract, Criterion, save_contract
from core.evidence import EvidenceEntry, append_evidence
from core.stop_gate import evaluate_stop


class TestStopGate(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_missing_evidence_blocks_stop(self):
        contract = Contract(
            task_id="TEST-001",
            description="Test task",
            acceptance_criteria=[Criterion(id="AC1", statement="Unit tests pass")],
        )
        save_contract(self.test_dir, contract)

        res = evaluate_stop(self.test_dir)
        self.assertEqual(res.get("decision"), "continue")
        self.assertIn("Completion blocked", res.get("reason", ""))
        self.assertIn("AC1", res.get("reason", ""))

    def test_fresh_passing_evidence_allows_stop(self):
        contract = Contract(
            task_id="TEST-002",
            description="Test task with evidence",
            acceptance_criteria=[Criterion(id="AC1", statement="Unit tests pass")],
        )
        save_contract(self.test_dir, contract)

        entry = EvidenceEntry(
            criterion_id="AC1",
            validator_id="pytest",
            command="pytest tests/",
            exit_code=0,
            passed=True,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        append_evidence(self.test_dir, entry)

        res = evaluate_stop(self.test_dir)
        self.assertEqual(res.get("decision"), "allow")

    def test_circuit_breaker(self):
        contract = Contract(task_id="TEST-003", description="Task")
        save_contract(self.test_dir, contract)
        res = evaluate_stop(self.test_dir, cycle_count=3)
        self.assertEqual(res.get("decision"), "continue")
        self.assertIn("circuit breaker", res.get("reason", "").lower())


if __name__ == "__main__":
    unittest.main()
