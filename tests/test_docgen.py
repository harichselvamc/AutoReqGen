import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from autoreqgen import docgen

MODULE_SRC = '''"""
This is the module docstring.
"""

def my_function():
    """This function does something."""
    pass

def _private_fn():
    """Private function should be hidden by default."""
    pass

class MyClass:
    """This is a test class."""
    def method(self):
        """This is a method."""
        pass

    def _private_method(self):
        """Private method should be hidden by default."""
        pass
'''

class TestDocGen(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.project = self.tmp_path / "examples" / "sample_project1"
        self.project.mkdir(parents=True, exist_ok=True)
        (self.project / "doc_test.py").write_text(MODULE_SRC, encoding="utf-8")
        self.out_md = self.tmp_path / "test_DOC.md"

    def tearDown(self):
        self.tmp.cleanup()

    def test_documentation_output_public_only(self):
        docgen.generate_docs(str(self.project), output_file=str(self.out_md), include_private=False)
        self.assertTrue(self.out_md.exists(), "Output markdown file should be created")
        text = self.out_md.read_text(encoding="utf-8")

        # basic structure present
        self.assertIn("Auto-Generated Documentation", text)
        self.assertIn("Module:", text)

        # public items included
        self.assertIn("my_function", text)
        self.assertIn("This function does something.", text)
        self.assertIn("class MyClass", text)
        self.assertIn("This is a test class.", text)
        self.assertIn("method", text)
        self.assertIn("This is a method.", text)

        # private items excluded by default
        self.assertNotIn("_private_fn", text)
        self.assertNotIn("_private_method", text)

        # file should end with newline
        self.assertTrue(text.endswith("\n"))

    def test_documentation_output_including_private(self):
        docgen.generate_docs(str(self.project), output_file=str(self.out_md), include_private=True)
        text = self.out_md.read_text(encoding="utf-8")

        # now private items appear
        self.assertIn("_private_fn", text)
        self.assertIn("_private_method", text)

if __name__ == "__main__":
    unittest.main()
