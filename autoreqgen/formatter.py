import subprocess
import shutil
import sys
from pathlib import Path
from typing import List, Union

SUPPORTED = {"black", "isort", "autopep8"}

def run_formatter(tool: str, path: str = ".") -> None:
    """
    Run a formatter (black, isort, autopep8) on the specified path.

    Raises:
        ValueError: if tool is not one of the supported names.
    """
    tool = tool.lower().strip()
    if tool not in SUPPORTED:
        raise ValueError("Unsupported formatter. Choose from: black, isort, autopep8.")

    # Check presence; don't auto-install here (keep function pure for tests)
    if shutil.which(tool) is None:
        print(f"'{tool}' is not installed. Please run 'pip install {tool}' first.")
        return

    commands = {
        "black": [sys.executable, "-m", "black", path],
        "isort": [sys.executable, "-m", "isort", path],
        "autopep8": [sys.executable, "-m", "autopep8", "--in-place", "--aggressive", "--recursive", path],
    }

    cmd = commands[tool]
    print(f"🧹 Running {tool} on {path} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout.strip():
        print(result.stdout)
    if result.stderr.strip():
        print(result.stderr)

    if result.returncode == 0:
        print(f" {tool} formatting completed.")
    else:
        print(f" {tool} failed with exit code {result.returncode}.")
