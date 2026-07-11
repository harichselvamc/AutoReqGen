# doctor.py
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from autoreqgen import scanner, utils

VENV_NAME_HINTS = (".venv", "venv", "env")


@dataclass
class CheckResult:
    name: str
    status: str  # "ok" | "warn" | "fail"
    message: str
    fix_hint: str = ""


def check_venv_active() -> CheckResult:
    if utils.in_venv():
        return CheckResult("Virtual environment", "ok", "A virtual environment is active.")
    return CheckResult(
        "Virtual environment",
        "warn",
        "No virtual environment is active. Beginners should isolate project dependencies.",
        fix_hint="autoreqgen start",
    )


def check_requirements_exists(path: Path) -> CheckResult:
    req = Path(path) / "requirements.txt"
    if req.exists():
        return CheckResult("requirements.txt", "ok", "requirements.txt found.")
    return CheckResult(
        "requirements.txt",
        "fail",
        "No requirements.txt found. Others won't know what packages to install.",
        fix_hint="autoreqgen generate .",
    )


def check_imports_installed(path: Path) -> CheckResult:
    imports = scanner.scan_project_for_imports(str(path))
    missing = [name for name in imports if not utils.is_module_installed(name)]
    if not missing:
        return CheckResult("Installed imports", "ok", "All imported packages are installed.")
    listed = ", ".join(sorted(missing))
    return CheckResult(
        "Installed imports",
        "fail",
        f"These imported packages aren't installed in this environment: {listed}",
        fix_hint="pip install -r requirements.txt",
    )


def check_unpinned_versions(path: Path) -> CheckResult:
    req = Path(path) / "requirements.txt"
    if not req.exists():
        return CheckResult("Pinned versions", "warn", "Can't check versions, requirements.txt is missing.")

    lines = [
        line.strip()
        for line in req.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    unpinned = [line for line in lines if "==" not in line]
    if not unpinned:
        return CheckResult("Pinned versions", "ok", "All packages have pinned versions.")
    listed = ", ".join(unpinned)
    return CheckResult(
        "Pinned versions",
        "warn",
        f"Some packages aren't pinned to an exact version: {listed}",
        fix_hint="autoreqgen freeze",
    )


def check_gitignore(path: Path, venv_name: str = ".venv") -> CheckResult:
    gi = Path(path) / ".gitignore"
    if not gi.exists():
        return CheckResult(
            ".gitignore",
            "warn",
            "No .gitignore found. You might accidentally commit your virtual environment.",
            fix_hint="autoreqgen init",
        )
    content = gi.read_text(encoding="utf-8")
    names_to_check = {venv_name, *VENV_NAME_HINTS}
    if any(name in content for name in names_to_check):
        return CheckResult(".gitignore", "ok", ".gitignore exists and ignores your virtual environment.")
    return CheckResult(
        ".gitignore",
        "warn",
        f".gitignore exists but doesn't seem to ignore a virtual environment folder (e.g. `{venv_name}`).",
        fix_hint=f"Add `{venv_name}/` to your .gitignore",
    )


def run_all_checks(path: Path, venv_name: str = ".venv") -> List[CheckResult]:
    path = Path(path)
    return [
        check_venv_active(),
        check_requirements_exists(path),
        check_imports_installed(path),
        check_unpinned_versions(path),
        check_gitignore(path, venv_name=venv_name),
    ]
