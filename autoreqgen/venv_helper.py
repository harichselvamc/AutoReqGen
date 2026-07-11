# venv_helper.py
from __future__ import annotations
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class VenvResult:
    ok: bool
    env_path: Path
    message: str
    activate_hint: str = ""


def list_available_pythons() -> List[str]:
    """Discover Python executables on PATH (Windows: `where python`, POSIX: `which -a python`)."""
    cmd = "where python" if platform.system() == "Windows" else "which -a python"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return [line.strip() for line in result.stdout.splitlines() if "python" in line.lower()]


def venv_python_path(env_name: str) -> Path:
    """Path to the python executable inside a virtual environment."""
    return Path(env_name) / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")


def _activate_hint(env_name: str) -> str:
    if platform.system() == "Windows":
        return f".\\{env_name}\\Scripts\\activate"
    return f"source ./{env_name}/bin/activate"


def create_venv(python_exe: str, env_name: str) -> VenvResult:
    """Create a virtual environment using the given python executable."""
    env_path = Path(env_name)
    result = subprocess.run([python_exe, "-m", "venv", env_name], capture_output=True, text=True)
    if result.returncode != 0:
        return VenvResult(
            ok=False,
            env_path=env_path,
            message=f"Failed to create virtual environment:\n{result.stderr.strip()}",
        )
    return VenvResult(
        ok=True,
        env_path=env_path,
        message=f"Virtual environment `{env_name}` created successfully.",
        activate_hint=_activate_hint(env_name),
    )


def install_packages_into_venv(env_name: str, packages: List[str]) -> subprocess.CompletedProcess:
    """Install packages into an existing virtual environment using its own pip."""
    venv_python = venv_python_path(env_name)
    return subprocess.run([str(venv_python), "-m", "pip", "install", *packages], capture_output=True, text=True)
