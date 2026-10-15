"""Tests for core.fast_lint AST and delimiter validator."""

import tempfile
import unittest
from pathlib import Path

from core.fast_lint import check_delimiter_balance, lint_file


class TestFastLint(unittest.TestCase):
    def test_python_valid(self):
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("def foo():\n    return 42\n")
            f_path = f.name
        try:
            res = lint_file(f_path)
            self.assertTrue(res.valid)
            self.assertEqual(len(res.errors), 0)
            self.assertLess(res.duration_ms, 50)
        finally:
            Path(f_path).unlink(missing_ok=True)

    def test_python_syntax_error(self):
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("def foo(\n    broken code\n")
            f_path = f.name
        try:
            res = lint_file(f_path)
            self.assertFalse(res.valid)
            self.assertGreater(len(res.errors), 0)
        finally:
            Path(f_path).unlink(missing_ok=True)

    def test_json_valid(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write('{"name": "test", "items": [1, 2, 3]}')
            f_path = f.name
        try:
            res = lint_file(f_path)
            self.assertTrue(res.valid)
        finally:
            Path(f_path).unlink(missing_ok=True)

    def test_json_invalid(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write('{"name": "test", "unclosed": }')
            f_path = f.name
        try:
            res = lint_file(f_path)
            self.assertFalse(res.valid)
        finally:
            Path(f_path).unlink(missing_ok=True)

    def test_delimiter_scanner(self):
        # Valid JS
        js_valid = "function test() { const a = [1, (2 + 3)]; }"
        self.assertEqual(len(check_delimiter_balance(js_valid)), 0)

        # Unclosed bracket
        js_invalid = "function test() { const a = [1, 2; }"
        errs = check_delimiter_balance(js_invalid)
        self.assertGreater(len(errs), 0)


if __name__ == "__main__":
    unittest.main()
