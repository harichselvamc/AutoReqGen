import unittest
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typer.testing import CliRunner

from autoreqgen.cli import app

RUNNER = CliRunner()

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        # sample project layout
        self.project = self.tmp_path / "sample_project1"
        self.project.mkdir(parents=True, exist_ok=True)
        (self.project / "main.py").write_text(
            "import os\nimport sys\n\ndef sample():\n    print('Test')\n",
            encoding="utf-8",
        )
        # run commands from tmp
        self.cwd = os.getcwd()
        os.chdir(self.tmp_path)

    def tearDown(self):
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def test_scan_command(self):
        result = RUNNER.invoke(app, ["scan", str(self.project)])
        # Debug on failure
        if result.exit_code != 0:
            print("\nSCAN OUTPUT:", result.output)
        self.assertEqual(result.exit_code, 0)
        # Avoid strict emoji assertion; just check summary line
        self.assertIn("Found", result.output)

    def test_generate_command(self):
        out_file = self.tmp_path / "cli_requirements.txt"
        result = RUNNER.invoke(app, ["generate", str(self.project), "--output", str(out_file)])
        if result.exit_code != 0:
            print("\nGENERATE OUTPUT:", result.output)
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(out_file.exists())
        # file should be newline-terminated and text
        content = out_file.read_text(encoding="utf-8")
        self.assertTrue(content == "" or content.endswith("\n"))

    def test_docs_command(self):
        out_file = self.tmp_path / "cli_docs.md"
        result = RUNNER.invoke(app, ["docs", str(self.project), "--output", str(out_file)])
        if result.exit_code != 0:
            print("\nDOCS OUTPUT:", result.output)
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(out_file.exists())
        text = out_file.read_text(encoding="utf-8")
        self.assertIn("Auto-Generated Documentation", text)

if __name__ == "__main__":
    unittest.main()
