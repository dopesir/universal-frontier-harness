"""Tests for cross-platform resilience (Windows cp1252, POSIX paths, UTF-8)."""

import tempfile
import unittest
from pathlib import Path

from core.fast_lint import lint_file


class TestCrossPlatform(unittest.TestCase):
    def test_unicode_utf8_handling(self):
        # Ensure unicode strings with emojis, non-ascii characters do not crash
        unicode_content = """# 🚀 Universal Frontier Harness
def calculate_π():
    \"\"\"Calculates π using François Viète's formula: √½ · √(½ + ½√½)...\"\"\"
    text = "こんにちは世界 · Привет мир · مرحبا بالعالم"
    return 3.141592653589793
"""
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(unicode_content)
            f_path = f.name
        try:
            res = lint_file(f_path)
            self.assertTrue(res.valid)
            self.assertEqual(len(res.errors), 0)
        finally:
            Path(f_path).unlink(missing_ok=True)

    def test_pathlib_posix_windows_normalization(self):
        # Check that mixed separators resolve cleanly
        p1 = Path("src/core/test.py")
        p2 = Path(r"src\core\test.py")
        self.assertEqual(p1.parts, p2.parts)


if __name__ == "__main__":
    unittest.main()
