# utils.py
from __future__ import annotations
import os
import sys
import shutil
import subprocess
import importlib.util
from importlib import metadata
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Optional
import re

# -------- Environment & platform helpers --------

@lru_cache(maxsize=None)
def is_windows() -> bool:
    return os.name == "nt"

@lru_cache(maxsize=None)
def is_colab() -> bool:
    return "google.colab" in sys.modules

@lru_cache(maxsize=None)
def in_venv() -> bool:
    # Works for venv, virtualenv, poetry, etc.
    return (
        hasattr(sys, "real_prefix")
        or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
        or bool(os.environ.get("VIRTUAL_ENV"))
        or bool(os.environ.get("CONDA_PREFIX"))
        or bool(os.environ.get("POETRY_ACTIVE"))
    )

@lru_cache(maxsize=None)
def project_root(start: str | Path = ".") -> Path:
    """
    Heuristic project root:
    - Nearest ancestor with one of: pyproject.toml, setup.cfg, setup.py, requirements.txt, .git
    - Else absolute of start
    """
    p = Path(start).resolve()
    markers = {"pyproject.toml", "setup.cfg", "setup.py", "requirements.txt", ".git"}
    for parent in [p, *p.parents]:
        if any((parent / m).exists() for m in markers):
            return parent
    return p

def load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except Exception:
        pass

# -------- Name normalization --------

def pep503_normalize(name: str) -> str:
    """PEP 503 normalized distribution name."""
    return re.sub(r"[-_.]+", "-", name).lower()

def clean_package_name(name: str) -> str:
    """Clean up a package/import name (keeps your existing API)."""
    return name.strip().split(".")[0]

def normalize_import_name(name: str) -> str:
    """Normalize an import name to its top-level, PEP 503-ish form."""
    return pep503_normalize(clean_package_name(name))

# -------- Installation / presence checks --------

@lru_cache(maxsize=None)
def is_module_installed(module_name: str) -> bool:
    """Check if a Python module is importable in the current environment."""
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ModuleNotFoundError, ImportError, ValueError):
        return False

@lru_cache(maxsize=None)
def is_tool_installed(tool_name: str) -> bool:
    """
    Check if a CLI tool is available.
    - First: looks up executable on PATH.
    - Then: tries `python -m <tool>` heuristic for module-based CLIs.
    """
    if shutil.which(tool_name) is not None:
        return True
    # Some tools (black, isort, autopep8) can be run as modules.
    try:
        spec = importlib.util.find_spec(tool_name.replace("-", "_"))
        return spec is not None
    except Exception:
        return False

def ensure_tool(tool_name: str, attempt_install: bool = False) -> bool:
    """
    Ensure a tool is available. Optionally attempt install via pip.
    Returns True if available at the end.
    """
    if is_tool_installed(tool_name):
        return True
    if attempt_install:
        print(f"⚙️  Installing missing dependency: {tool_name}")
        pip_install(tool_name)
        return is_tool_installed(tool_name)
    return False

# -------- Subprocess helpers --------

def run_cmd(args: List[str], cwd: Optional[str | Path] = None) -> subprocess.CompletedProcess:
    """
    Run a subprocess command, capturing output. Does not raise on nonzero.
    """
    return subprocess.run(
        [str(a) for a in args],
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )

def pip_install(*packages: str) -> subprocess.CompletedProcess:
    """
    Install packages with the current interpreter's pip.
    """
    return run_cmd([sys.executable, "-m", "pip", "install", *packages])

# -------- Presentation --------

def _read_version() -> str:
    try:
        return metadata.version("autoreqgen")
    except Exception:
        return ""

def print_banner() -> None:
    """Print a welcome banner (shows version if installed)."""
    ver = _read_version()
    ver_str = f" v{ver}" if ver else ""
    # Keep it simple/portable (no color codes)
    print(
        rf"""
 AutoReqGen{ver_str}
"""
    )

# -------- Misc. helpers --------

def parse_comma_list(value: str | None) -> List[str]:
    """Parse a comma-separated string into a clean list."""
    if not value:
        return []
    return [x.strip() for x in value.split(",") if x.strip()]

def ensure_newline(path: Path) -> None:
    """Ensure file ends with a newline (POSIX-friendly)."""
    try:
        txt = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return
    if not txt.endswith("\n"):
        path.write_text(txt + "\n", encoding="utf-8")
