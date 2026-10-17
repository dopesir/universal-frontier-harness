"""Tests for core.graph_intel zero-dependency dependency & blast-radius engine."""

import json
from pathlib import Path
import tempfile
import time
import unittest

from core.graph_intel import (
    DependencyGraph,
    _load_graphify_graph,
    check_blast_radius_safety,
    evaluate_blast_radius,
    get_dependency_graph,
)
from core.policy import Action, evaluate_action


class TestGraphIntel(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_native_ast_dependency_extraction(self):
        """Verify native AST scanner extracts imports without any external tools."""
        file_a = self.root / "base.py"
        file_b = self.root / "service.py"
        file_c = self.root / "controller.py"

        file_a.write_text("class BaseService:\n    def execute(self):\n        pass\n", encoding="utf-8")
        file_b.write_text("from base import BaseService\nclass AppService(BaseService):\n    pass\n", encoding="utf-8")
        file_c.write_text("import base\nimport service\n", encoding="utf-8")

        graph = get_dependency_graph(self.root, force_refresh=True)

        self.assertEqual(graph.source, "native_ast")
        # base.py is imported by service.py and controller.py
        br_base = graph.compute_blast_radius("base.py")
        self.assertEqual(br_base.score, 2)
        self.assertEqual(br_base.level, "LOW")
        self.assertIn("service.py", br_base.direct_dependents)
        self.assertIn("controller.py", br_base.direct_dependents)

        # controller.py has no dependents
        br_ctrl = graph.compute_blast_radius("controller.py")
        self.assertEqual(br_ctrl.score, 0)
        self.assertEqual(br_ctrl.level, "NONE")

    def test_graphify_auto_detection_and_ingestion(self):
        """Verify Graphify graph.json is automatically consumed when present."""
        graphify_dir = self.root / "graphify-out"
        graphify_dir.mkdir(parents=True, exist_ok=True)
        graph_json = graphify_dir / "graph.json"

        payload = {
            "nodes": [
                {"id": "mod_a", "label": "auth.py", "source_file": "src/auth.py", "community": 1},
                {"id": "mod_b", "label": "api.py", "source_file": "src/api.py", "community": 1},
                {"id": "mod_c", "label": "worker.py", "source_file": "src/worker.py", "community": 2},
            ],
            "links": [
                {"source": "mod_b", "target": "mod_a", "relation": "imports_from"},
                {"source": "mod_c", "target": "mod_a", "relation": "calls"},
            ],
        }
        graph_json.write_text(json.dumps(payload), encoding="utf-8")

        graph = get_dependency_graph(self.root, force_refresh=True)
        self.assertEqual(graph.source, "graphify")

        br_auth = graph.compute_blast_radius("auth.py")
        self.assertEqual(br_auth.score, 2)
        self.assertEqual(br_auth.source, "graphify")
        self.assertIn("src/api.py", br_auth.direct_dependents)
        self.assertIn("src/worker.py", br_auth.direct_dependents)

    def test_standalone_no_graphify_required(self):
        """Verify the harness does NOT require Graphify to be initialized."""
        # Clean directory with zero Graphify files
        py_file = self.root / "util.py"
        py_file.write_text("def helper():\n    return 42\n", encoding="utf-8")

        graph = get_dependency_graph(self.root, force_refresh=True)
        self.assertEqual(graph.source, "native_ast")
        br = graph.compute_blast_radius("util.py")
        self.assertEqual(br.score, 0)
        self.assertEqual(br.level, "NONE")

    def test_blast_radius_safety_thresholds(self):
        """Verify advisory is generated when uninspected high-blast-radius targets are touched."""
        # Create a hub module with 5 dependents
        hub = self.root / "hub.py"
        hub.write_text("def core_fn(): pass\n", encoding="utf-8")
        for i in range(5):
            client = self.root / f"client_{i}.py"
            client.write_text("import hub\n", encoding="utf-8")

        graph = get_dependency_graph(self.root, force_refresh=True)
        br = graph.compute_blast_radius("hub.py")
        self.assertEqual(br.level, "HIGH")
        self.assertEqual(br.score, 5)

        # Uninspected callers -> warning
        is_safe, adv = check_blast_radius_safety("hub.py", inspected_paths=set(), root_dir=self.root)
        self.assertFalse(is_safe)
        self.assertIn("BLAST RADIUS WARNING", adv)

        # Inspected callers -> safe
        is_safe, adv = check_blast_radius_safety("hub.py", inspected_paths={"client_0.py"}, root_dir=self.root)
        self.assertTrue(is_safe)

    def test_performance_sub_25ms(self):
        """Assert cached lookup latency is well within interactive threshold (<25ms)."""
        f = self.root / "sample.py"
        f.write_text("def sample(): pass\n", encoding="utf-8")
        get_dependency_graph(self.root, force_refresh=True)

        t0 = time.perf_counter()
        for _ in range(20):
            evaluate_blast_radius("sample.py", self.root)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        avg_latency_ms = elapsed_ms / 20
        self.assertLess(avg_latency_ms, 25.0, f"Latency {avg_latency_ms:.2f}ms exceeds 25ms threshold")

    def test_strict_mode_policy_integration(self):
        """Verify strict-blast-radius mode in evaluate_action denies uninspected high blast mutations."""
        hub = self.root / "hub.py"
        hub.write_text("def core_fn(): pass\n", encoding="utf-8")
        for i in range(5):
            client = self.root / f"c_{i}.py"
            client.write_text("import hub\n", encoding="utf-8")

        action = Action(kind="write", tool="write_to_file", paths=[str(hub)])

        # Read hub itself so read-before-write passes
        reads = {str(hub)}

        # In strict-blast-radius mode with callers unread -> denied
        decision, reason = evaluate_action(
            action=action,
            mode="strict-blast-radius",
            reads=reads,
            root_dir=self.root,
        )
        self.assertEqual(decision, "deny")
        self.assertIn("Blast radius gate violation", reason)

        # In standard implement mode -> allowed (asymmetric silence / non-blocking)
        decision, _ = evaluate_action(
            action=action,
            mode="implement",
            reads=reads,
            root_dir=self.root,
        )
        self.assertEqual(decision, "allow")


if __name__ == "__main__":
    unittest.main()
