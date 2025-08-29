#!/usr/bin/env python
import sys
import subprocess
import tempfile
import re
from pathlib import Path
from typing import Iterable, List, Set

from autoreqgen import scanner, requirements

NAME_RE = re.compile(r"^\s*([A-Za-z0-9._-]+)")

def pep503(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()

def py_files(args: List[str]) -> List[str]:
    files = [a for a in args if a.endswith(".py") and Path(a).exists()]
    # if pre-commit passes nothing (pass_filenames: false), default to repo
    return files or ["."]
    
def run_tool(mod_name: str, args: List[str]) -> int:
    cmd = [sys.executable, "-m", mod_name, *args]
    proc = subprocess.run(cmd, text=True)
    return proc.returncode

def run_auto_format_check(files: List[str]) -> bool:
    print("Checking code style with black and isort...")
    ok = True
    # black --check
    if run_tool("black", ["--check", "--diff", *files]) != 0:
        print(" black found issues.")
        ok = False
    # isort --check-only
    if run_tool("isort", ["--check-only", "--diff", *files]) != 0:
        print(" isort found issues.")
        ok = False
    if ok:
        print("Formatting checks passed.")
    return ok

def parse_req_names(lines: Iterable[str]) -> Set[str]:
    names: Set[str] = set()
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # strip markers/extras/version constraints: take first token before [ ; <=> !
        m = NAME_RE.match(line)
        if not m:
            continue
        names.add(pep503(m.group(1)))
    return names

def read_requirements_file(path: Path) -> Set[str]:
    if not path.exists():
        return set()
    return parse_req_names(path.read_text(encoding="utf-8").splitlines())

def expected_requirements_names(project_root: Path) -> Set[str]:
    # Use your resolver to generate the expected set without versions,
    # then parse names from the temp file for robust comparison.
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        imports = scanner.scan_project_for_imports(str(project_root))
        requirements.generate_requirements(imports, output_file=str(tmp_path), with_versions=False)
        expected = read_requirements_file(tmp_path)
        return expected
    finally:
        try:
            tmp_path.unlink(missing_ok=True)  # type: ignore[attr-defined]
        except Exception:
            pass

def check_requirements_sync(project_root: Path, req_path: Path = Path("requirements.txt")) -> bool:
    print(" Checking requirements drift...")
    expected = expected_requirements_names(project_root)
    current = read_requirements_file(req_path)

    missing = expected - current
    # optionally warn about extras in file that aren't imported:
    extra = current - expected

    ok = True
    if missing:
        ok = False
        print("Packages imported but missing from requirements.txt:")
        for name in sorted(missing):
            print(f"  - {name}")
        print("   → run: autoreqgen generate .")

    # Not failing on extras by default (dev/test tools), just inform:
    if extra:
        print("ℹ  Packages present in requirements.txt but not currently imported:")
        for name in sorted(extra):
            print(f"  - {name}")

    if ok:
        print(" requirements.txt is in sync.")
    return ok

def main(argv: List[str]) -> int:
    files = py_files(argv)
    fmt_ok = run_auto_format_check(files)
    req_ok = check_requirements_sync(Path("."))
    if not (fmt_ok and req_ok):
        return 1
    print(" Pre-commit checks passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
