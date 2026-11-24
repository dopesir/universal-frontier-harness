"""Tests for scripts.asset_inspector multimodal diagnostic engine."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.asset_inspector import inspect_svg


class TestAssetInspector(unittest.TestCase):
    def test_inspect_svg(self):
        sample_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
            <circle cx="50" cy="50" r="40" fill="red" />
            <path d="M 10 10 L 90 90" stroke="black" />
            <rect x="20" y="20" width="60" height="60" fill="blue" />
        </svg>"""
        with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False, encoding="utf-8") as f:
            f.write(sample_svg)
            f_path = f.name
        try:
            info = inspect_svg(f_path)
            self.assertEqual(info["type"], "SVG_VECTOR")
            self.assertEqual(info["viewBox"], "0 0 100 100")
            self.assertEqual(info["element_counts"]["circles"], 1)
            self.assertEqual(info["element_counts"]["paths"], 1)
            self.assertEqual(info["element_counts"]["rectangles"], 1)
            self.assertIn("red", info["color_fills"])
            self.assertIn("blue", info["color_fills"])
            self.assertIn("black", info["color_strokes"])
        finally:
            Path(f_path).unlink(missing_ok=True)

    def test_cli_execution_svg(self):
        sample_svg = """<svg viewBox="0 0 50 50"><circle cx="25" cy="25" r="20" /></svg>"""
        with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False, encoding="utf-8") as f:
            f.write(sample_svg)
            f_path = f.name
        try:
            script_path = str(Path(__file__).parent.parent / "scripts" / "asset_inspector.py")
            res = subprocess.run([sys.executable, script_path, f_path], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0)
            data = json.loads(res.stdout)
            self.assertEqual(data["type"], "SVG_VECTOR")
            self.assertEqual(data["element_counts"]["circles"], 1)
        finally:
            Path(f_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
