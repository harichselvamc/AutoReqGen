import unittest
import subprocess
import os
import sys

CLI_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEST_PATH = os.path.join(CLI_PATH, "examples", "sample_project1")
MAIN_FILE = os.path.join(TEST_PATH, "main.py")

# Python command that ensures autoreqgen is found
PYTHON_CMD = [
    sys.executable,
    "-c",
    (
        "import sys, os; "
        f"sys.path.insert(0, r'{CLI_PATH}'); "
        "from autoreqgen.cli import app; "
        "import typer; "
        "typer.run(app)"
    )
]

class TestCLI(unittest.TestCase):

    def setUp(self):
        os.makedirs(TEST_PATH, exist_ok=True)
        with open(MAIN_FILE, "w") as f:
            f.write('''
import os
import sys

def sample():
    print("Test")
''')

    def test_scan_command(self):
        result = subprocess.run(PYTHON_CMD + ["scan", TEST_PATH], capture_output=True, text=True)
        print("\nSCAN STDOUT:", result.stdout)
        print("SCAN STDERR:", result.stderr)
        self.assertEqual(result.returncode, 0)
        self.assertIn("📦", result.stdout)

    def test_generate_command(self):
        result = subprocess.run(PYTHON_CMD + ["generate", TEST_PATH, "--output", "cli_requirements.txt"], capture_output=True, text=True)
        print("\nGENERATE STDOUT:", result.stdout)
        print("GENERATE STDERR:", result.stderr)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists("cli_requirements.txt"))

    def test_docs_command(self):
        result = subprocess.run(PYTHON_CMD + ["docs", TEST_PATH, "--output", "cli_docs.md"], capture_output=True, text=True)
        print("\nDOCS STDOUT:", result.stdout)
        print("DOCS STDERR:", result.stderr)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists("cli_docs.md"))

    def tearDown(self):
        for file in ["cli_requirements.txt", "cli_docs.md", MAIN_FILE]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    unittest.main()
