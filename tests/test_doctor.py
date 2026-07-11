import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typer.testing import CliRunner

from autoreqgen.cli import app
from autoreqgen import doctor

RUNNER = CliRunner()


class TestDoctorChecks(unittest.TestCase):
    """Unit tests against the doctor module functions directly."""

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_requirements_missing_fails(self):
        result = doctor.check_requirements_exists(self.tmp_path)
        self.assertEqual(result.status, "fail")

    def test_requirements_present_ok(self):
        (self.tmp_path / "requirements.txt").write_text("requests==2.31.0\n", encoding="utf-8")
        result = doctor.check_requirements_exists(self.tmp_path)
        self.assertEqual(result.status, "ok")

    def test_uninstalled_import_detected(self):
        (self.tmp_path / "main.py").write_text("import notarealpackage123\n", encoding="utf-8")
        result = doctor.check_imports_installed(self.tmp_path)
        self.assertEqual(result.status, "fail")
        self.assertIn("notarealpackage123", result.message)

    def test_no_external_imports_ok(self):
        (self.tmp_path / "main.py").write_text("import os\nimport sys\n", encoding="utf-8")
        result = doctor.check_imports_installed(self.tmp_path)
        self.assertEqual(result.status, "ok")

    def test_unpinned_versions_warns(self):
        (self.tmp_path / "requirements.txt").write_text("requests\nnumpy==1.26.0\n", encoding="utf-8")
        result = doctor.check_unpinned_versions(self.tmp_path)
        self.assertEqual(result.status, "warn")
        self.assertIn("requests", result.message)

    def test_all_pinned_ok(self):
        (self.tmp_path / "requirements.txt").write_text("requests==2.31.0\n", encoding="utf-8")
        result = doctor.check_unpinned_versions(self.tmp_path)
        self.assertEqual(result.status, "ok")

    def test_gitignore_missing_warns(self):
        result = doctor.check_gitignore(self.tmp_path)
        self.assertEqual(result.status, "warn")

    def test_gitignore_covers_venv_ok(self):
        (self.tmp_path / ".gitignore").write_text(".venv/\n__pycache__/\n", encoding="utf-8")
        result = doctor.check_gitignore(self.tmp_path)
        self.assertEqual(result.status, "ok")

    def test_gitignore_missing_venv_warns(self):
        (self.tmp_path / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
        result = doctor.check_gitignore(self.tmp_path)
        self.assertEqual(result.status, "warn")


class TestDoctorCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.cwd = os.getcwd()
        os.chdir(self.tmp_path)

    def tearDown(self):
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def test_doctor_fails_on_missing_requirements(self):
        result = RUNNER.invoke(app, ["doctor", "."])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("requirements.txt", result.output)

    def test_doctor_warn_only_does_not_fail(self):
        # requirements.txt present + pinned, no external imports -> only the
        # no-active-venv / missing-gitignore warnings should appear, exit 0.
        (self.tmp_path / "requirements.txt").write_text("", encoding="utf-8")
        (self.tmp_path / "main.py").write_text("import os\n", encoding="utf-8")
        result = RUNNER.invoke(app, ["doctor", "."])
        self.assertEqual(result.exit_code, 0)
        self.assertNotIn("[FAILED]", result.output)

    def test_doctor_detects_uninstalled_import(self):
        (self.tmp_path / "requirements.txt").write_text("", encoding="utf-8")
        (self.tmp_path / "main.py").write_text("import notarealpackage123\n", encoding="utf-8")
        result = RUNNER.invoke(app, ["doctor", "."])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("notarealpackage123", result.output)


if __name__ == "__main__":
    unittest.main()
