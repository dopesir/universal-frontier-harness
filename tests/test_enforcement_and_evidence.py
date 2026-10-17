"""Adversarial and policy enforcement tests for evidence validity and completion gates.

Verifies:
1. Successful command creates valid evidence.
2. Failing command (exit_code != 0) is strictly rejected as passing evidence.
3. Missing exit code is rejected.
4. Non-integer exit code (e.g. string "0") is rejected.
5. Contradictory claims ("All tests passed" text with non-zero exit code) are rejected.
6. Stale evidence (acquired before latest mutation) is rejected.
7. Evidence from a different task_id is rejected.
8. Malformed evidence lines in JSONL are skipped without crashing.
9. Corrupted contract.json causes stop gate to fail closed (decision: continue).
"""

import json
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from core.contract import Contract, Criterion, save_contract
from core.evidence import EvidenceEntry, append_evidence, is_fresh, owned_validator_pass
from core.stop_gate import evaluate_stop


class TestEnforcementAndEvidence(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="ufh_evidence_test_"))

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_valid_evidence_passes(self):
        entry = {
            "criterion_id": "AC1",
            "validator_id": "pytest",
            "command": "pytest tests/",
            "exit_code": 0,
            "passed": True,
            "task_id": "TASK-100",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.assertTrue(owned_validator_pass(entry, task_id="TASK-100"))

    def test_failing_exit_code_rejected(self):
        entry = {
            "criterion_id": "AC1",
            "validator_id": "pytest",
            "command": "pytest tests/",
            "exit_code": 1,
            "passed": False,
            "task_id": "TASK-100",
        }
        self.assertFalse(owned_validator_pass(entry, task_id="TASK-100"))

    def test_missing_exit_code_rejected(self):
        entry = {
            "criterion_id": "AC1",
            "validator_id": "pytest",
            "command": "pytest tests/",
            "passed": True,
            # exit_code omitted entirely
        }
        self.assertFalse(owned_validator_pass(entry))

    def test_string_exit_code_rejected(self):
        entry = {
            "criterion_id": "AC1",
            "validator_id": "pytest",
            "command": "pytest tests/",
            "exit_code": "0",  # String instead of int
            "passed": True,
        }
        self.assertFalse(owned_validator_pass(entry))

    def test_contradictory_claims_rejected(self):
        # Passed set to True, but exit code is 2
        entry = {
            "criterion_id": "AC1",
            "validator_id": "pytest",
            "command": "pytest tests/",
            "exit_code": 2,
            "passed": True,
            "stdout_summary": "10 passed, 1 failed. Verified.",
        }
        self.assertFalse(owned_validator_pass(entry))

    def test_empty_command_rejected(self):
        # Claiming pass without an executable command
        entry = {
            "criterion_id": "AC1",
            "validator_id": "pytest",
            "command": "   ",
            "exit_code": 0,
            "passed": True,
        }
        self.assertFalse(owned_validator_pass(entry))

    def test_mismatched_task_id_rejected(self):
        contract = Contract(
            task_id="TASK-ACTIVE",
            description="Active Task",
            acceptance_criteria=[Criterion(id="AC1", statement="Passing tests")],
        )
        save_contract(self.test_dir, contract)

        # Evidence belongs to an older task
        entry = EvidenceEntry(
            criterion_id="AC1",
            validator_id="pytest",
            command="pytest tests/",
            exit_code=0,
            passed=True,
            task_id="TASK-PREVIOUS",
        )
        append_evidence(self.test_dir, entry)

        res = evaluate_stop(self.test_dir)
        self.assertEqual(res["decision"], "continue")
        self.assertIn("lack fresh passing evidence", res["reason"])

    def test_stale_evidence_rejected_by_mutation(self):
        contract = Contract(
            task_id="TASK-STALE",
            description="Stale Task",
            acceptance_criteria=[Criterion(id="AC1", statement="Passing tests")],
        )
        save_contract(self.test_dir, contract)

        past_time = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
        newer_mutation_time = (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat()

        # Evidence timestamp is older than latest mutation
        entry = EvidenceEntry(
            criterion_id="AC1",
            validator_id="pytest",
            command="pytest tests/",
            exit_code=0,
            passed=True,
            task_id="TASK-STALE",
            timestamp=past_time,
        )
        append_evidence(self.test_dir, entry)

        # Record mutation after evidence
        mutations_file = self.test_dir / "mutations.jsonl"
        with open(mutations_file, "w", encoding="utf-8") as f:
            f.write(json.dumps({"path": "src/app.py", "timestamp": newer_mutation_time}) + "\n")

        res = evaluate_stop(self.test_dir)
        self.assertEqual(res["decision"], "continue")
        self.assertIn("lack fresh passing evidence", res["reason"])

    def test_corrupted_contract_fails_closed(self):
        # Write corrupted JSON to contract.json
        contract_file = self.test_dir / "contract.json"
        contract_file.write_text("{ this is corrupted json }}}", encoding="utf-8")

        res = evaluate_stop(self.test_dir)
        self.assertEqual(res["decision"], "continue")
        self.assertIn("Contract enforcement failure", res["reason"])

    def test_malformed_evidence_lines_skipped_safely(self):
        evidence_file = self.test_dir / "evidence.jsonl"
        with open(evidence_file, "w", encoding="utf-8") as f:
            f.write("{ corrupt json line 1\n")
            f.write('{"criterion_id": "AC1", "passed": true, "exit_code": 0, "command": "pytest", "timestamp": "2026-10-17T00:00:00Z"}\n')
            f.write("another bad line\n")

        contract = Contract(
            task_id="TASK-RESILIENT",
            description="Task",
            acceptance_criteria=[Criterion(id="AC1", statement="Passing tests")],
        )
        save_contract(self.test_dir, contract)

        # Should parse valid line and accept
        res = evaluate_stop(self.test_dir)
        self.assertEqual(res["decision"], "allow")


if __name__ == "__main__":
    unittest.main()
