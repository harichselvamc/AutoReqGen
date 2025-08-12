import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from autoreqgen import scanner

SRC = """\
import os
import sys
import numpy as np
from collections import defaultdict
"""

class TestScanner(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.project = self.tmp_path / "examples" / "sample_project1"
        self.project.mkdir(parents=True, exist_ok=True)
        (self.project / "sample.py").write_text(SRC, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_python_file_discovery(self):
        files = scanner.get_all_python_files(str(self.project))
        self.assertTrue(any(Path(f).name == "sample.py" for f in files))

    def test_scan_project_filters_stdlib(self):
        # Should include 3rd-party like numpy, but NOT stdlib imports
        imports = scanner.scan_project_for_imports(str(self.project))
        self.assertIn("numpy", imports)
        self.assertNotIn("os", imports)
        self.assertNotIn("sys", imports)
        self.assertNotIn("collections", imports)

    def test_extract_all_includes_stdlib(self):
        # Raw mode: includes stdlib too
        imports = scanner.extract_all_imports(str(self.project))
        for name in ["os", "sys", "numpy", "collections"]:
            self.assertIn(name, imports)

if __name__ == "__main__":
    unittest.main()
