import unittest
import os
from autoreqgen import docgen

TEST_FILE = "examples/sample_project1/doc_test.py"
OUTPUT_DOC = "test_DOC.md"

class TestDocGen(unittest.TestCase):

    def setUp(self):
        os.makedirs(os.path.dirname(TEST_FILE), exist_ok=True)
        with open(TEST_FILE, "w") as f:
            f.write('''"""
This is the module docstring.
"""

def my_function():
    """This function does something."""
    pass

class MyClass:
    """This is a test class."""
    def method(self):
        """This is a method."""
        pass
''')

    def test_documentation_output(self):
        docgen.generate_docs("examples/sample_project1", output_file=OUTPUT_DOC)
        self.assertTrue(os.path.exists(OUTPUT_DOC))

        with open(OUTPUT_DOC, "r") as f:
            content = f.read()
            self.assertIn("my_function", content)
            self.assertIn("This is a test class", content)

    def tearDown(self):
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)
        if os.path.exists(OUTPUT_DOC):
            os.remove(OUTPUT_DOC)

if __name__ == "__main__":
    unittest.main()
