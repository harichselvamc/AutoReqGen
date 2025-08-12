import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util

from autoreqgen import formatter

SRC = "def    foo ():\n    print('hello')\n"

def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None

class TestFormatter(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.project = self.tmp_path / "examples" / "sample_project1"
        self.project.mkdir(parents=True, exist_ok=True)
        self.file = self.project / "unformatted.py"
        self.file.write_text(SRC, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    @unittest.skipUnless(has_module("black"), "black not installed")
    def test_black_formatting(self):
        # 1) run formatter
        formatter.run_formatter("black", str(self.project))

        # 2) verify content formatted (black prefers double quotes, fixes spacing)
        text = self.file.read_text(encoding="utf-8")
        self.assertIn('print("hello")', text)
        self.assertIn("def foo():", text)

        # 3) idempotence: running again should keep same content
        before = text
        formatter.run_formatter("black", str(self.project))
        after = self.file.read_text(encoding="utf-8")
        self.assertEqual(before, after)

    def test_unsupported_formatter_raises(self):
        with self.assertRaises(ValueError):
            formatter.run_formatter("not-a-tool", str(self.project))
