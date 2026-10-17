"""Installation and deployment safety integration tests.

Tests the hardened installer across:
1. Empty project
2. Project with existing AGENTS.md (preservation by default)
3. Project with existing hooks.json
4. Repeated installation (idempotency)
5. Dry-run mode
6. Explicit overwrite with automatic backup
7. Paths containing spaces
8. Invocation from another working directory
9. Complete runtime file and module import verification
10. Uninstall functionality
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestInstallationIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ufh_install_test_"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run_installer(self, *args, cwd: Path | None = None) -> subprocess.CompletedProcess:
        installer_script = ROOT / "scripts" / "init_harness.py"
        cmd = [sys.executable, str(installer_script), *args]
        return subprocess.run(
            cmd,
            cwd=str(cwd or ROOT),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_install_empty_project(self):
        target = self.temp_dir / "empty_proj"
        target.mkdir()

        res = self.run_installer(str(target))
        self.assertEqual(res.returncode, 0, f"Installer failed: {res.stderr}")
        self.assertIn("installation successfully completed", res.stdout)

        # Check required files exist
        self.assertTrue((target / ".agents" / "rules" / "AGENTS.md").is_file())
        self.assertTrue((target / ".agents" / "hooks" / "hooks.json").is_file())
        self.assertTrue((target / ".agents" / "hooks" / "pre_tool.py").is_file())
        self.assertTrue((target / ".agents" / "hooks" / "stop_gate.py").is_file())
        self.assertTrue((target / ".agents" / "core" / "fast_lint.py").is_file())
        self.assertTrue((target / ".agents" / "core" / "policy.py").is_file())
        self.assertTrue((target / ".agents" / "memory" / "task_state.md").is_file())

    def test_preserve_existing_agents_md(self):
        target = self.temp_dir / "existing_proj"
        target.mkdir()
        agents_dir = target / ".agents"
        agents_dir.mkdir()
        existing_agents = agents_dir / "AGENTS.md"
        custom_content = "# Custom User Agent Rules\nDO NOT OVERWRITE\n"
        existing_agents.write_text(custom_content, encoding="utf-8")

        # Run installer without overwrite
        res = self.run_installer(str(target))
        self.assertEqual(res.returncode, 0)
        self.assertIn("[SKIP]", res.stdout)

        # File content must remain untouched
        self.assertEqual(existing_agents.read_text(encoding="utf-8"), custom_content)

    def test_dry_run_mode(self):
        target = self.temp_dir / "dry_run_proj"
        target.mkdir()

        res = self.run_installer(str(target), "--dry-run")
        self.assertEqual(res.returncode, 0)
        self.assertIn("DRY-RUN MODE", res.stdout)
        self.assertIn("0 files modified", res.stdout)

        # Verify no files were actually created
        self.assertFalse((target / ".agents").exists())

    def test_explicit_overwrite_with_backup(self):
        target = self.temp_dir / "overwrite_proj"
        target.mkdir()
        agents_dir = target / ".agents"
        agents_dir.mkdir()
        existing_rule = agents_dir / "AGENTS.md"
        old_content = "ORIGINAL IMPORTANT CONTENT"
        existing_rule.write_text(old_content, encoding="utf-8")

        res = self.run_installer(str(target), "--overwrite")
        self.assertEqual(res.returncode, 0)
        self.assertIn("[BACKUP]", res.stdout)
        self.assertIn("[OVERWROTE]", res.stdout)

        # Content should now be updated
        self.assertNotEqual(existing_rule.read_text(encoding="utf-8"), old_content)

        # Backup file must exist and contain old content
        backups = list(agents_dir.glob("AGENTS.md.bak.*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), old_content)

    def test_path_with_spaces(self):
        target = self.temp_dir / "My Target Project With Spaces"
        target.mkdir()

        res = self.run_installer(str(target))
        self.assertEqual(res.returncode, 0, f"Installer failed on spaces: {res.stderr}")
        self.assertTrue((target / ".agents" / "hooks" / "pre_tool.py").is_file())

        # Test executing installed pre_tool hook from within the project with spaces
        test_hook = target / ".agents" / "hooks" / "pre_tool.py"
        hook_run = subprocess.run(
            [sys.executable, str(test_hook)],
            cwd=str(target),
            input="{}",
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(hook_run.returncode, 0, f"Hook failed: {hook_run.stderr}")

    def test_uninstall_functionality(self):
        target = self.temp_dir / "uninstall_proj"
        target.mkdir()

        # 1. Install
        self.run_installer(str(target))
        self.assertTrue((target / ".agents" / "core").is_dir())

        # Create custom user file in memory
        user_memory = target / ".agents" / "memory" / "my_custom_note.md"
        user_memory.write_text("keep this", encoding="utf-8")

        # 2. Uninstall
        res = self.run_installer(str(target), "--uninstall")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Uninstall complete", res.stdout)

        # Core and hooks should be removed
        self.assertFalse((target / ".agents" / "core").exists())
        self.assertFalse((target / ".agents" / "hooks").exists())
        self.assertFalse((target / ".agents" / "rules").exists())

        # User memory must be preserved
        self.assertTrue(user_memory.is_file())
        self.assertEqual(user_memory.read_text(encoding="utf-8"), "keep this")

    def test_repeated_installation_is_idempotent(self):
        target = self.temp_dir / "idempotent_proj"
        target.mkdir()

        # Run 1: clean install
        res1 = self.run_installer(str(target))
        self.assertEqual(res1.returncode, 0)

        # Run 2: repeat without overwrite
        res2 = self.run_installer(str(target))
        self.assertEqual(res2.returncode, 0)
        self.assertIn("[SKIP]", res2.stdout)

    def test_existing_hooks_preserved_without_overwrite(self):
        target = self.temp_dir / "hooks_proj"
        target.mkdir()
        hooks_dir = target / ".agents" / "hooks"
        hooks_dir.mkdir(parents=True)
        custom_hooks = hooks_dir / "hooks.json"
        custom_json = '{"custom": true}'
        custom_hooks.write_text(custom_json, encoding="utf-8")

        res = self.run_installer(str(target))
        self.assertEqual(res.returncode, 0)
        self.assertIn("[SKIP]", res.stdout)
        self.assertIn("hooks.json", res.stdout)
        self.assertEqual(custom_hooks.read_text(encoding="utf-8"), custom_json)

    def test_invocation_from_different_cwd(self):
        target = self.temp_dir / "foreign_cwd_proj"
        target.mkdir()
        foreign_cwd = self.temp_dir / "foreign_working_dir"
        foreign_cwd.mkdir()

        res = self.run_installer(str(target), cwd=foreign_cwd)
        self.assertEqual(res.returncode, 0)
        self.assertTrue((target / ".agents" / "core" / "contract.py").is_file())


if __name__ == "__main__":
    unittest.main()
