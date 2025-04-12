import unittest
import os
from autoreqgen import formatter

TEST_FILE = "examples/sample_project1/unformatted.py"

class TestFormatter(unittest.TestCase):

    def setUp(self):
        os.makedirs(os.path.dirname(TEST_FILE), exist_ok=True)
        with open(TEST_FILE, "w") as f:
            f.write("def    foo ():\n    print('hello')")

    def test_black_formatting(self):
        # Run formatter
        formatter.run_formatter("black", os.path.dirname(TEST_FILE))

        # Check if the formatting applied (black adds double quotes)
        with open(TEST_FILE, "r") as f:
            content = f.read()
            self.assertIn('print("hello")', content)

    def tearDown(self):
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)

if __name__ == "__main__":
    unittest.main()
