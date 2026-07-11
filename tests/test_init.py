import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typer.testing import CliRunner

from autoreqgen.cli import app
from autoreqgen import utils

RUNNER = CliRunner()


class TestInitCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.cwd = os.getcwd()
        os.chdir(self.tmp_path)

    def tearDown(self):
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def test_init_non_interactive_defaults(self):
        result = RUNNER.invoke(app, ["init", "--yes"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue((self.tmp_path / "main.py").exists())
        self.assertTrue((self.tmp_path / "README.md").exists())
        self.assertTrue((self.tmp_path / ".gitignore").exists())
        self.assertTrue((self.tmp_path / "requirements.txt").exists())
        self.assertFalse((self.tmp_path / ".venv").exists())
        self.assertFalse((self.tmp_path / ".git").exists())

    def test_init_with_explicit_name_and_type(self):
        result = RUNNER.invoke(app, ["init", "--yes", "--name", "myapp", "--type", "cli"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("myapp", (self.tmp_path / "README.md").read_text(encoding="utf-8"))
        self.assertIn("typer", (self.tmp_path / "main.py").read_text(encoding="utf-8"))
        self.assertIn("typer", (self.tmp_path / "requirements.txt").read_text(encoding="utf-8"))

    def test_init_invalid_type_errors(self):
        result = RUNNER.invoke(app, ["init", "--yes", "--type", "not-a-real-type"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Unknown project type", result.output)

    def test_init_is_idempotent(self):
        first = RUNNER.invoke(app, ["init", "--yes"])
        self.assertEqual(first.exit_code, 0, first.output)
        second = RUNNER.invoke(app, ["init", "--yes"])
        self.assertEqual(second.exit_code, 0, second.output)
        self.assertIn("Skipped", second.output)

    def test_init_with_venv_flag(self):
        result = RUNNER.invoke(app, ["init", "--yes", "--venv", "--venv-name", "myvenv"])
        self.assertEqual(result.exit_code, 0, result.output)
        expected = self.tmp_path / "myvenv" / ("Scripts" if os.name == "nt" else "bin") / (
            "python.exe" if os.name == "nt" else "python"
        )
        self.assertTrue(expected.exists(), f"expected venv python at {expected}")

    def test_init_with_git_flag(self):
        if not utils.is_tool_installed("git"):
            self.skipTest("git not installed")
        result = RUNNER.invoke(app, ["init", "--yes", "--git"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue((self.tmp_path / ".git").exists())

    def test_init_prompts_when_flags_omitted(self):
        result = RUNNER.invoke(app, ["init"], input="myproject\nbasic\nn\nn\n")
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("myproject", (self.tmp_path / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
