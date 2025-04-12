import unittest
import os
from autoreqgen import scanner

TEST_DIR = "examples/sample_project1"

# Setup: create a mock project with imports
os.makedirs(TEST_DIR, exist_ok=True)
with open(f"{TEST_DIR}/sample.py", "w") as f:
    f.write("""
import os
import sys
import numpy as np
from collections import defaultdict
    """)

class TestScanner(unittest.TestCase):

    def test_python_file_discovery(self):
        files = scanner.get_all_python_files(TEST_DIR)
        self.assertTrue(any("sample.py" in file for file in files))

    def test_import_extraction(self):
        imports = scanner.scan_project_for_imports(TEST_DIR)
        self.assertIn("os", imports)
        self.assertIn("sys", imports)
        self.assertIn("numpy", imports)
        self.assertIn("collections", imports)

if __name__ == '__main__':
    unittest.main()
