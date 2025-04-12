import unittest
import os
from autoreqgen import requirements

class TestRequirementsGenerator(unittest.TestCase):

    def setUp(self):
        self.test_output = "test_requirements.txt"
        self.test_imports = ["os", "sys", "typer", "nonexistentpackage"]

    def test_version_resolution(self):
        version = requirements.get_installed_version("typer")
        self.assertIsNotNone(version)
        self.assertTrue(version.count(".") >= 1)

    def test_requirements_file_creation(self):
        requirements.generate_requirements(self.test_imports, output_file=self.test_output)
        self.assertTrue(os.path.exists(self.test_output))

        with open(self.test_output, "r") as f:
            content = f.read()
            self.assertIn("typer", content)
            self.assertNotIn("nonexistentpackage", content)

    def tearDown(self):
        if os.path.exists(self.test_output):
            os.remove(self.test_output)

if __name__ == "__main__":
    unittest.main()
