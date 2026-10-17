import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

from core.fast_lint import check_delimiter_balance, lint_file

ROOT = Path(__file__).resolve().parent.parent

# Dynamically import repo_map from hyphenated skill path
_repo_map_path = ROOT / "skills" / "ast-repo-mapper" / "scripts" / "repo_map.py"
_spec = importlib.util.spec_from_file_location("repo_map", _repo_map_path)
_repo_map = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_repo_map)
generate_repo_map = _repo_map.generate_repo_map


class TestLanguageValidation(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ufh_lang_test_"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_python_ast_level_reported(self):
        py_file = self.temp_dir / "test.py"
        py_file.write_text("class Calculator:\n    def add(self, a, b):\n        return a + b\n", encoding="utf-8")

        res = lint_file(py_file)
        self.assertTrue(res.valid)
        self.assertEqual(res.validation_level, "ast_parse")
        self.assertEqual(res.file_type, "py")

    def test_python_syntax_error_detected(self):
        py_file = self.temp_dir / "broken.py"
        py_file.write_text("def missing_colon()\n    pass", encoding="utf-8")

        res = lint_file(py_file)
        self.assertFalse(res.valid)
        self.assertEqual(res.validation_level, "ast_parse")
        self.assertTrue(any("SyntaxError" in err for err in res.errors))

    def test_json_full_parse_reported(self):
        json_file = self.temp_dir / "config.json"
        json_file.write_text('{"name": "harness", "active": true, "count": 42}', encoding="utf-8")

        res = lint_file(json_file)
        self.assertTrue(res.valid)
        self.assertEqual(res.validation_level, "full_json_parse")

    def test_json_decode_error_detected(self):
        json_file = self.temp_dir / "bad.json"
        json_file.write_text('{"name": "harness", trailing_comma: }', encoding="utf-8")

        res = lint_file(json_file)
        self.assertFalse(res.valid)
        self.assertEqual(res.validation_level, "full_json_parse")
        self.assertTrue(any("JSONDecodeError" in err for err in res.errors))

    def test_js_ts_delimiter_level_reported(self):
        js_file = self.temp_dir / "app.tsx"
        js_file.write_text("export const Button = () => { return <button>Click</button>; };", encoding="utf-8")

        res = lint_file(js_file)
        self.assertTrue(res.valid)
        self.assertEqual(res.validation_level, "delimiter_balance")
        self.assertEqual(res.file_type, "tsx")

    def test_delimiter_comments_ignored_correctly(self):
        # Brackets inside comments should not affect delimiter stack
        code = """
        // Unclosed ( in single-line comment
        /* Unclosed { in multi-line comment */
        function calculate() {
            return 10 * (2 + 3);
        }
        """
        errs = check_delimiter_balance(code)
        self.assertEqual(len(errs), 0)

    def test_delimiter_unclosed_template_literal(self):
        code = "const str = `unclosed template literal;"
        errs = check_delimiter_balance(code)
        self.assertTrue(any("Unterminated template literal" in e for e in errs))

    def test_missing_file_handled(self):
        missing = self.temp_dir / "nonexistent.py"
        res = lint_file(missing)
        self.assertFalse(res.valid)
        self.assertEqual(res.validation_level, "none")

    def test_repo_mapper_symbols_and_ignores(self):
        # Create nested modules and ignored dir
        src = self.temp_dir / "src"
        src.mkdir()
        (src / "service.py").write_text("class AuthService:\n    def login(self, user, pwd):\n        pass\n", encoding="utf-8")
        (src / "util.ts").write_text("export function formatName(first, last) { return first + last; }\n", encoding="utf-8")

        ignored = self.temp_dir / "node_modules" / "pkg"
        ignored.mkdir(parents=True)
        (ignored / "index.js").write_text("function bad() {", encoding="utf-8")

        repomap = generate_repo_map(self.temp_dir)
        self.assertIn("service.py", repomap)
        self.assertIn("class AuthService", repomap)
        self.assertIn("def login", repomap)
        self.assertIn("util.ts", repomap)
        self.assertIn("function formatName", repomap)
        # Ignored node_modules must NOT appear
        self.assertNotIn("node_modules", repomap)


if __name__ == "__main__":
    unittest.main()
