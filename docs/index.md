# 🧠 AutoReqGen Documentation

Welcome to the official documentation for **AutoReqGen** — a smarter alternative to `pipreqs` that scans your Python project, auto-generates `requirements.txt`, formats your code, and builds documentation — all through a beautiful CLI.

---

## 🔍 Overview

AutoReqGen is designed to solve common frustrations with `pipreqs`:
- ❌ Wrong version numbers
- ❌ Skips deeply nested files
- ❌ No code formatting or doc generation

Instead, AutoReqGen gives you:
- ✅ Accurate import detection and version resolution
- ✅ Recursive directory traversal
- ✅ Code formatting (Black, isort, autopep8)
- ✅ Auto-generated Markdown docs from docstrings
- ✅ Clean CLI with `typer`

---

## 📦 Key Features

- **Import Scanner**: Detects all Python imports using AST
- **Requirements Generator**: Creates version-pinned `requirements.txt`
- **Formatter**: Cleans up your code using your tool of choice
- **Doc Generator**: Extracts docstrings into human-readable Markdown
- **CLI**: Run all of it through a simple command-line interface

---

## 📁 Structure

```bash
AutoReqGen/
├── autoreqgen/       # Core logic
├── tests/            # Unit tests
├── examples/         # Sample apps for testing
├── docs/             # Documentation (this folder)
├── setup.py          # Packaging
├── pyproject.toml    # Build config
