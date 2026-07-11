import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typer.testing import CliRunner

from autoreqgen.cli import app
from autoreqgen import descriptions, requirements

RUNNER = CliRunner()


class TestDescriptions(unittest.TestCase):
    def test_curated_lookup(self):
        self.assertIn("HTTP", descriptions.describe("requests"))

    def test_curated_lookup_is_case_and_separator_insensitive(self):
        self.assertIn("HTTP", descriptions.describe("Requests"))
        self.assertEqual(descriptions.describe("scikit_learn"), descriptions.describe("scikit-learn"))

    def test_unknown_package_fallback(self):
        self.assertEqual(descriptions.describe("totally-not-a-real-package-xyz"), "No description available.")


class TestParseRequirementsFile(unittest.TestCase):
    def test_strips_versions_and_comments(self):
        with TemporaryDirectory() as tmp:
            req = Path(tmp) / "requirements.txt"
            req.write_text("requests==2.31.0\n# a comment\n\nnumpy>=1.20\nblack\n", encoding="utf-8")
            names = requirements.parse_requirements_file(req)
            self.assertEqual(names, ["requests", "numpy", "black"])


class TestExplainCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.cwd = os.getcwd()
        os.chdir(self.tmp_path)

    def tearDown(self):
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def test_explain_reads_requirements_file(self):
        (self.tmp_path / "requirements.txt").write_text("requests==2.31.0\n", encoding="utf-8")
        result = RUNNER.invoke(app, ["explain"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("requests", result.output)
        self.assertIn("HTTP", result.output)

    def test_explain_missing_file_errors(self):
        result = RUNNER.invoke(app, ["explain"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("not found", result.output)

    def test_explain_scan_mode(self):
        # Use a package name that is guaranteed to be neither stdlib nor installed,
        # so the result doesn't depend on what happens to be installed in the test env.
        project = self.tmp_path / "proj"
        project.mkdir()
        (project / "main.py").write_text("import totallyfakepkg123\n", encoding="utf-8")
        result = RUNNER.invoke(app, ["explain", "--scan", str(project)])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("totallyfakepkg123", result.output)

    def test_explain_as_json(self):
        (self.tmp_path / "requirements.txt").write_text("requests==2.31.0\nblack==24.0.0\n", encoding="utf-8")
        result = RUNNER.invoke(app, ["explain", "--as-json"])
        self.assertEqual(result.exit_code, 0)
        json_text = result.output[result.output.index("{"):]
        data = json.loads(json_text)
        self.assertEqual(set(data.keys()), {"requests", "black"})


if __name__ == "__main__":
    unittest.main()
