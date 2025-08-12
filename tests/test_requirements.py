import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from autoreqgen import requirements

class TestRequirementsGenerator(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.out = self.tmp_path / "test_requirements.txt"
        # stdlib + one known 3rd-party + one fake
        self.test_imports = ["os", "sys", "typer", "nonexistentpackage"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_version_resolution(self):
        ver = requirements.get_installed_version("typer")
        self.assertIsNotNone(ver)
        self.assertTrue("." in ver)

    def test_requirements_file_creation(self):
        requirements.generate_requirements(self.test_imports, output_file=str(self.out))
        self.assertTrue(self.out.exists())
        content = self.out.read_text(encoding="utf-8")
        # third-party present
        self.assertIn("typer", content.lower())
        # unresolved import excluded (with_versions default True)
        self.assertNotIn("nonexistentpackage", content)

if __name__ == "__main__":
    unittest.main()
