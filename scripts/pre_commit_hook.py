import subprocess
import sys
from autoreqgen import scanner, requirements

def run_auto_format():
    print("🔧 Auto-formatting with black and isort...")
    subprocess.run(["black", "."], check=True)
    subprocess.run(["isort", "."], check=True)

def check_requirements_sync():
    print("📦 Checking for outdated requirements...")
    current_imports = scanner.scan_project_for_imports(".")
    with open("requirements.txt", "r", encoding="utf-8") as f:
        req_lines = f.read().splitlines()

    req_pkgs = {line.split("==")[0] for line in req_lines if "==" in line}
    current_pkgs = set(current_imports)

    missing = current_pkgs - req_pkgs
    if missing:
        print("⚠️ WARNING: These packages are imported but missing in requirements.txt:")
        for pkg in sorted(missing):
            print(f"  - {pkg}")
        print("❗ Consider re-running: python -m autoreqgen.cli generate .")
        sys.exit(1)

def main():
    run_auto_format()
    check_requirements_sync()
    print("✅ Pre-commit checks passed.")

if __name__ == "__main__":
    main()
