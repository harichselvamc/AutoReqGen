## Core Badges


[![PyPI version](https://badge.fury.io/py/autoreqgen.svg)](https://badge.fury.io/py/autoreqgen)
[![PyPI Downloads](https://static.pepy.tech/badge/autoreqgen/week)](https://pepy.tech/projects/autoreqgen)
[![PyPI Downloads](https://static.pepy.tech/badge/autoreqgen/month)](https://pepy.tech/projects/autoreqgen)
[![PyPI Downloads](https://static.pepy.tech/badge/autoreqgen)](https://pepy.tech/projects/autoreqgen)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

# AutoReqGen

> A smarter alternative to pipreqs — AutoReqGen scans your entire project recursively, accurately generates requirements.txt with exact versions, formats your code using tools like Black or isort, and even auto-generates documentation from your docstrings. One tool to automate and optimize your Python workflow.

## What's New in v0.1.29

Three new commands aimed at making AutoReqGen easier to pick up for beginners and students:

```bash
# Scaffold a brand-new project in one step (main file, README, .gitignore, requirements.txt)
autoreqgen init --yes --name my-first-app --type cli --venv --git

# Get a plain-language health check of an existing project
autoreqgen doctor .
[OK]      requirements.txt: requirements.txt found.
[WARNING] Pinned versions: Some packages aren't pinned to an exact version: typer
    Try: autoreqgen freeze

# Find out what a package actually does before you install it
autoreqgen explain --scan .
requests — send and receive HTTP requests easily
```

See [Project Scaffolding (`init`)](#project-scaffolding-init), [Health Check (`doctor`)](#health-check-doctor), and [Plain-English Package Explain (`explain`)](#plain-english-package-explain-explain) below for full usage.

##  Activity & Maintenance

[![GitHub last commit](https://img.shields.io/github/last-commit/harichselvamc/autoreqgen.svg)](https://github.com/harichselvamc/autoreqgen/commits/main)
[![GitHub issues](https://img.shields.io/github/issues/harichselvamc/autoreqgen.svg)](https://github.com/harichselvamc/autoreqgen/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/harichselvamc/autoreqgen.svg)](https://github.com/harichselvamc/autoreqgen/pulls)
[![Contributors](https://img.shields.io/github/contributors/harichselvamc/autoreqgen.svg)](https://github.com/harichselvamc/autoreqgen/graphs/contributors)

## Repo Stats

[![GitHub stars](https://img.shields.io/github/stars/harichselvamc/autoreqgen.svg)](https://github.com/harichselvamc/autoreqgen/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/harichselvamc/autoreqgen.svg)](https://github.com/harichselvamc/autoreqgen/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/harichselvamc/autoreqgen.svg)](https://github.com/harichselvamc/autoreqgen/watchers)

## Features

- Auto-generate requirements.txt with or without version numbers
- Filters standard library & local modules
- Format code using black, isort, or autopep8
- Auto-generate DOCUMENTATION.md from your codebase docstrings
- Live import watching with autoreqgen watch
- Add packages with autoreqgen add (auto-installs and appends)
- autoreqgen freeze to lock all installed packages (sorted & deduplicated)
- autoreqgen start to create a new virtual environment using system Pythons
- autoreqgen init to scaffold a new beginner-friendly project (with optional venv + git init)
- autoreqgen doctor to run a friendly health check on your project
- autoreqgen explain to describe what each package in your requirements does, in plain English
- --as-json and --all flag support
- Auto detects .env files for configuration
- CLI aliases like g for generate, f for format, etc.

## Quickstart

### Install the package

```bash
pip install autoreqgen
```

### Scan your project

```bash
autoreqgen scan .
```

### Generate requirements.txt with version numbers

```bash
autoreqgen generate .
```

### Add a package and update requirements.txt

```bash
autoreqgen add requests
```

### Format the code using black

```bash
autoreqgen format black .
```

### Generate documentation

```bash
autoreqgen docs . --output docs.md
```

### Watch your project and update requirements.txt on change

```bash
autoreqgen watch .
```

### Start a new project virtual environment

```bash
autoreqgen start
```

### Freeze your current environment into a clean requirements.txt

```bash
autoreqgen freeze
```

### Scaffold a new beginner-friendly project

```bash
autoreqgen init
```

### Check your project's health

```bash
autoreqgen doctor .
```

### Explain what your dependencies do, in plain English

```bash
autoreqgen explain
```

## Example Structure

```
myproject/
├── main.py
├── utils/
│   └── helper.py
├── requirements.txt
├── DOCUMENTATION.md
```

## Detailed Usage

### Scanning Projects

Scan a project to identify all Python imports:

```bash
autoreqgen scan /path/to/project
```

### Generating Requirements

Generate a requirements.txt file with all necessary packages:

```bash
# Default (with version numbers)
autoreqgen generate /path/to/project

# Without version numbers
autoreqgen generate /path/to/project --no-versions

# Output as JSON
autoreqgen generate /path/to/project --as-json

# Include all imports (even standard library)
autoreqgen generate /path/to/project --all
```

### Dependency Management

Add packages to your project and requirements.txt:

```bash
# Add single package
autoreqgen add requests

# Add multiple packages
autoreqgen add requests pandas numpy

# Add with specific version
autoreqgen add "requests>=2.25.0"
```

Freeze your environment to create a reproducible requirements.txt:

```bash
autoreqgen freeze
```

### Code Formatting

Format your code using different tools:

```bash
# Format with black
autoreqgen format black /path/to/project

# Format with isort
autoreqgen format isort /path/to/project

# Format with autopep8
autoreqgen format autopep8 /path/to/project

# Chain formatters
autoreqgen format black,isort /path/to/project
```

### Documentation Generation

Generate documentation from your docstrings:

```bash
# Basic usage
autoreqgen docs /path/to/project

# Specify output file
autoreqgen docs /path/to/project --output API.md

# Generate for specific modules
autoreqgen docs /path/to/project --modules main.py,utils
```

### Live Watching

Watch your project for changes and automatically update requirements.txt:

```bash
# Watch project
autoreqgen watch /path/to/project

# Watch with specific interval (in seconds)
autoreqgen watch /path/to/project --interval 5

# Watch and format on change
autoreqgen watch /path/to/project --format black
```

### Virtual Environment Setup (`start`)

Start a new Python project with a virtual environment:

```bash
# Create a new virtual environment in the current directory
autoreqgen start

# Specify Python version
autoreqgen start --python 3.10

# Create with specific packages
autoreqgen start --packages "requests pandas"
```

### Project Scaffolding (`init`)

Scaffold a new beginner-friendly project — great for students starting from scratch:

```bash
# Interactive wizard (asks for name, type, venv, git)
autoreqgen init

# Fully non-interactive, using flags/defaults
autoreqgen init --yes --name myapp --type cli --venv --git

# Project types: basic, cli, web, data
autoreqgen init --yes --type web
```

Creates a starter main file, `README.md`, `.gitignore`, and `requirements.txt`. Re-running `init` in the same folder is safe — it never overwrites existing files.

### Health Check (`doctor`)

Run a friendly check for common beginner project issues:

```bash
autoreqgen doctor .
```

Checks for: an active virtual environment, a `requirements.txt` file, imports that aren't installed, unpinned versions, and a `.gitignore` that covers your venv. Each check prints an `[OK]` / `[WARNING]` / `[FAILED]` line with a suggested fix; the command exits non-zero only when something is actually broken (`[FAILED]`).

### Plain-English Package Explain (`explain`)

Find out what a package actually does before you install it:

```bash
# Explain everything in requirements.txt
autoreqgen explain

# Explain imports found by scanning a project directly
autoreqgen explain --scan .

# Machine-readable output
autoreqgen explain --as-json
```

## Configuration

AutoReqGen can be configured using environment variables or `.env` files:

```
AUTOREQGEN_DEFAULT_FORMAT=black
AUTOREQGEN_IGNORE_DIRS=tests,examples
AUTOREQGEN_INCLUDE_DEV=true
AUTOREQGEN_VERBOSE=true
```
# Google Colab Compatibility Disclaimer

**AutoReqGen** is designed to run in standard Python environments (local, virtualenv, Conda, etc.). While many features work fine in Google Colab, there are some important limitations to be aware of:

## Features that **work in Colab**:
| Feature             | Status  | Description |
|---------------------|---------|-------------|
| `scan`              | Yes     | Scans Python files or projects to detect external imports. |
| `generate`          | Yes     | Generates `requirements.txt` from scanned imports. |
| `add <package>`     | Yes     | Installs a package and appends it to `requirements.txt`. |
| `freeze`            | Yes     | Freezes the current environment (via `pip freeze`) into `requirements.txt`. |
| `docs`              | Yes     | Extracts module, class, and function docstrings and generates markdown docs. |

##  Features that **do NOT work in Colab**:
| Feature             | Status  | Reason |
|---------------------|---------|--------|
| `start` (virtualenv creation) | No      | Google Colab does not allow creating or managing virtual environments. |
| `watch` (live import updates) | No      | `watchdog` cannot run in sandboxed Colab environments due to limited file system access and event monitoring. |

##  Colab-Specific Handling
When you run `AutoReqGen` inside Google Colab:
- The `start` command is **disabled** to prevent errors.
- A clear warning will be shown to the user:
  ```
  Warning: Virtual environment creation is not supported in Google Colab.
  ```

## Tip
You can still install `AutoReqGen` in Colab and use it like this:

```bash
!pip install autoreqgen
!autoreqgen scan .
!autoreqgen generate .
!autoreqgen freeze
```

---

For full functionality, we recommend running **AutoReqGen** in a local or server-based Python environment (outside Colab).
## Integration Examples

### Pre-commit Integration

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
-   repo: local
    hooks:
    -   id: autoreqgen
        name: AutoReqGen
        entry: autoreqgen generate .
        language: system
        pass_filenames: false
```

### GitHub Actions Workflow

```yaml
name: Update Requirements

on:
  push:
    paths:
      - '**.py'

jobs:
  update-requirements:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install AutoReqGen
        run: pip install autoreqgen
      - name: Update requirements.txt
        run: autoreqgen generate .
      - name: Commit changes
        uses: EndBug/add-and-commit@v9
        with:
          message: 'chore: update requirements.txt'
          add: 'requirements.txt'
```

### Docker Usage

Example Dockerfile:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install autoreqgen
RUN autoreqgen generate .
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
```


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=harichselvamc/AutoReqGen&type=date&legend=top-left)](https://www.star-history.com/#harichselvamc/AutoReqGen&type=date&legend=top-left)
