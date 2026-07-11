import typer
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import List

from autoreqgen import scanner, requirements, formatter, docgen, utils, venv_helper, descriptions, scaffold
from autoreqgen import doctor as doctor_mod

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Some terminals (notably the default Windows console codepage) can't encode
# the emoji used in command output; force UTF-8 so it never crashes on those.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure") and (_stream.encoding or "").lower() != "utf-8":
        try:
            _stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

app = typer.Typer(
    help="AutoReqGen – Smarter Python dependency and tooling assistant.",
    add_completion=True,
    pretty_exceptions_show_locals=False,
)

# ---------- helpers ----------

def run(cmd: List[str]) -> subprocess.CompletedProcess:
    """Run a subprocess and return the CompletedProcess (never raises)."""
    return subprocess.run(cmd, capture_output=True, text=True)

def pip_cmd(*args: str) -> List[str]:
    return [sys.executable, "-m", "pip", *args]

def echo_err(msg: str) -> None:
    typer.echo(msg, err=True)

# ---------- commands ----------

@app.command()
def scan(
    path: Path = typer.Argument(..., help="Path to your Python project"),
    all: bool = typer.Option(False, "--all", help="Include local and standard library modules"),
    as_json: bool = typer.Option(False, "--as-json", help="Output results in JSON format"),
):
    """Scan the project and list all imported packages."""
    utils.print_banner()
    imports = scanner.extract_all_imports(str(path)) if all else scanner.scan_project_for_imports(str(path))
    imports = sorted(set(imports))

    if as_json:
        typer.echo(json.dumps(imports, indent=2))
    else:
        for imp in imports:
            typer.echo(f"{imp}")
        typer.echo(f"\nFound {len(imports)} unique imports.")


@app.command()
def generate(
    path: Path = typer.Argument(..., help="Path to your Python project"),
    output: str = typer.Option("requirements.txt", "--output", "-o", help="Output file name"),
    with_versions: bool = typer.Option(True, "--with-versions/--no-versions", help="Include version numbers in requirements.txt"),
    as_json: bool = typer.Option(False, "--as-json", help="Print the discovered imports as JSON instead of writing a file"),
):
    """Generate requirements.txt with or without versions."""
    utils.print_banner()
    imports = scanner.scan_project_for_imports(str(path))
    if as_json:
        typer.echo(json.dumps(sorted(set(imports)), indent=2))
        raise typer.Exit(code=0)

    try:
        requirements.generate_requirements(imports, output_file=output, with_versions=with_versions)
        typer.echo(f"Wrote {output}")
    except Exception as e:
        echo_err(f"Failed to generate {output}: {e}")
        echo_err(f"Tip: check that '{path}' exists and that you have permission to write to '{output}'.")
        raise typer.Exit(code=1)


@app.command("format")
def format_cmd(
    tool: str = typer.Argument(..., help="Choose from: black, isort, autopep8 (comma-separated to chain)"),
    path: Path = typer.Argument(".", help="Target path for formatting"),
):
    """Format code using Black, isort, or autopep8. You can chain tools: 'black,isort'."""
    utils.print_banner()
    tools = [t.strip() for t in tool.split(",") if t.strip()]
    if not tools:
        echo_err(" No formatter provided.")
        raise typer.Exit(code=1)

    # Pre-check installation for each requested tool to give fast feedback
    for t in tools:
        if not utils.is_tool_installed(t):
            echo_err(f"'{t}' isn't installed yet. Run: pip install {t}")
            raise typer.Exit(code=1)

    for t in tools:
        typer.echo(f"Running {t} on {path} ...")
        try:
            formatter.run_formatter(t, str(path))
        except ValueError as e:
            # Unknown tool -> exit with clear message
            echo_err(f"{e}")
            raise typer.Exit(code=1)
        except Exception as e:
            echo_err(f"{t} failed: {e}")
            raise typer.Exit(code=1)
    typer.echo("Formatting complete.")


@app.command()
def docs(
    path: Path = typer.Argument(..., help="Path to your Python code"),
    output: str = typer.Option("DOCUMENTATION.md", help="Output Markdown file"),
    include_private: bool = typer.Option(False, "--include-private", help="Include private functions and classes"),
):
    """Generate documentation from docstrings."""
    utils.print_banner()
    try:
        docgen.generate_docs(str(path), output_file=output, include_private=include_private)
        typer.echo(f"Documentation saved to {output}")
    except Exception as e:
        echo_err(f"Failed to generate docs: {e}")
        raise typer.Exit(code=1)


@app.command()
def doctor(
    path: Path = typer.Argument(".", help="Path to your Python project"),
):
    """Run a beginner-friendly health check on your project."""
    utils.print_banner()
    labels = {"ok": "[OK]     ", "warn": "[WARNING]", "fail": "[FAILED] "}
    results = doctor_mod.run_all_checks(path)
    for r in results:
        typer.echo(f"{labels[r.status]} {r.name}: {r.message}")
        if r.fix_hint:
            typer.echo(f"    Try: {r.fix_hint}")

    if any(r.status == "fail" for r in results):
        raise typer.Exit(code=1)


@app.command()
def explain(
    requirements_file: Path = typer.Option(Path("requirements.txt"), "--file", "-f", help="Requirements file to read"),
    scan: Path = typer.Option(None, "--scan", help="Scan a project path for imports instead of reading a requirements file"),
    as_json: bool = typer.Option(False, "--as-json", help="Output results in JSON format"),
):
    """Explain what each package in your requirements does, in plain English."""
    utils.print_banner()

    if scan is not None:
        names = [
            requirements.ALIAS_MAP.get(utils.pep503_normalize(imp), imp)
            for imp in scanner.scan_project_for_imports(str(scan))
        ]
    else:
        if not requirements_file.exists():
            echo_err(f"'{requirements_file}' not found. Run `autoreqgen generate .` first, or use --scan <path>.")
            raise typer.Exit(code=1)
        names = requirements.parse_requirements_file(requirements_file)

    if not names:
        typer.echo("No packages found to explain.")
        raise typer.Exit(code=0)

    entries = [(name, descriptions.describe(name)) for name in names]

    if as_json:
        typer.echo(json.dumps({name: desc for name, desc in entries}, indent=2))
    else:
        for name, desc in entries:
            typer.echo(f"{name} — {desc}")


@app.command()
def add(
    package: str = typer.Argument(..., help='Package specifier, e.g. "requests" or "requests>=2.25.0"'),
    path: Path = typer.Option(Path("requirements.txt"), "--path", "-p", help="Path to requirements file"),
):
    """Install a package and add it to requirements.txt (without version pinning unless specified)."""
    utils.print_banner()
    typer.echo(f"Installing {package} ...")
    result = run(pip_cmd("install", package))
    if result.returncode != 0:
        echo_err(f"Failed to install {package}:\n{result.stderr.strip()}")
        echo_err("Tip: double check the package name for typos, and make sure you're connected to the internet.")
        raise typer.Exit(code=1)

    if not path.exists():
        typer.echo(f"Creating {path} ...")
        path.touch()

    # Read existing lines, strip comments/empties, dedupe case-insensitively
    existing: dict[str, str] = {}
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        existing[s.lower()] = s

    existing[package.lower()] = package
    new_lines = [existing[k] for k in sorted(existing.keys(), key=str.lower)]
    path.write_text("\n".join(new_lines) + "\n")

    typer.echo(f"Added to {path} (sorted & deduplicated)")


@app.command()
def freeze(output: str = typer.Option("requirements.txt", "--output", "-o", help="Output requirements file")):
    """Freeze the current environment and write exact package versions to a file."""
    utils.print_banner()
    typer.echo(f"Freezing environment to {output} ...")
    result = run(pip_cmd("freeze"))
    if result.returncode != 0:
        echo_err(f"Failed to freeze environment:\n{result.stderr.strip()}")
        raise typer.Exit(code=1)

    frozen = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    frozen_sorted = sorted(frozen, key=str.lower)
    Path(output).write_text("\n".join(frozen_sorted) + "\n")
    typer.echo(f"Environment frozen, sorted, and saved to {output}")


@app.command()
def init(
    name: str = typer.Option(None, "--name", help="Project name (used for the folder name and README title)"),
    type: str = typer.Option(None, "--type", help="Project type: basic, cli, web, data"),
    dest: Path = typer.Option(Path("."), "--dest", help="Directory to scaffold into (created if missing)"),
    venv: bool = typer.Option(None, "--venv/--no-venv", help="Create a virtual environment"),
    venv_name: str = typer.Option(".venv", "--venv-name", help="Name for the virtual environment"),
    git: bool = typer.Option(None, "--git/--no-git", help="Run `git init`"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Never prompt; use flags/defaults for anything unspecified"),
):
    """Interactively scaffold a new beginner-friendly Python project."""
    utils.print_banner()

    resolved_dest = dest.resolve()

    resolved_name = name
    if resolved_name is None:
        resolved_name = resolved_dest.name if yes else typer.prompt("Project name", default=resolved_dest.name)

    resolved_type_raw = type
    if resolved_type_raw is None:
        resolved_type_raw = "basic" if yes else typer.prompt("Project type (basic, cli, web, data)", default="basic")

    try:
        resolved_type = scaffold.normalize_project_type(resolved_type_raw)
    except ValueError as e:
        echo_err(str(e))
        raise typer.Exit(code=1)

    resolved_venv = venv
    if resolved_venv is None:
        resolved_venv = False if yes else typer.confirm("Create a virtual environment?", default=False)

    resolved_git = git
    if resolved_git is None:
        resolved_git = False if yes else typer.confirm("Initialize a git repository?", default=False)

    notes = scaffold.scaffold_project(resolved_dest, resolved_name, resolved_type, venv_name=venv_name)
    for note in notes:
        typer.echo(note)

    if resolved_venv:
        typer.echo(f"\nCreating virtual environment `{venv_name}` ...")
        result = venv_helper.create_venv(sys.executable, str(resolved_dest / venv_name))
        if result.ok:
            typer.echo(result.message)
            typer.echo(f"Activate: {result.activate_hint}")
        else:
            echo_err(result.message)

    if resolved_git:
        if utils.is_tool_installed("git"):
            git_result = utils.run_cmd(["git", "init"], cwd=resolved_dest)
            if git_result.returncode == 0:
                typer.echo("Initialized a git repository.")
            else:
                echo_err(f"`git init` failed:\n{git_result.stderr.strip()}")
        else:
            typer.echo("Skipping git init: `git` isn't installed.")

    typer.echo(f"\n Project ready in {resolved_dest}")


@app.command()
def start(
    python: str = typer.Option(None, "--python", help="Path to python executable to use"),
    name: str = typer.Option(None, "--name", "-n", help="Name for the virtual environment (default: .venv)"),
    packages: str = typer.Option(None, "--packages", "-r", help='Optional packages to install, e.g. "requests pandas"'),
):
    """Create a new virtual environment (non-Colab) and optionally install packages."""
    utils.print_banner()

    if "google.colab" in sys.modules:
        typer.echo(" Virtual environment creation is not supported in Google Colab.")
        raise typer.Exit(code=1)

    env_name = name or ".venv"

    # Resolve python executable
    selected_python = python
    if not selected_python:
        python_paths = venv_helper.list_available_pythons()
        if not python_paths:
            echo_err(" No Python executables found.")
            raise typer.Exit(code=1)

        typer.echo("\nAvailable Python executables:")
        for i, p in enumerate(python_paths, start=1):
            typer.echo(f"  [{i}] {p}")

        choice = typer.prompt("Choose Python (number)", type=int)
        try:
            selected_python = python_paths[choice - 1]
        except Exception:
            echo_err("Invalid choice.")
            raise typer.Exit(code=1)

    typer.echo(f"\nCreating virtual environment `{env_name}` with {selected_python} ...")
    result = venv_helper.create_venv(selected_python, env_name)
    if not result.ok:
        echo_err(result.message)
        echo_err("Tip: make sure the Python path is correct and executable.")
        raise typer.Exit(code=1)

    typer.echo(result.message)
    typer.echo(f"Activate: {result.activate_hint}")

    if packages:
        typer.echo(f"Installing packages into `{env_name}`: {packages}")
        install = venv_helper.install_packages_into_venv(env_name, packages.split())
        if install.returncode != 0:
            echo_err(f"Packages install reported errors:\n{install.stderr.strip()}")
        else:
            typer.echo("Packages installed.")


@app.command()
def watch(
    path: Path = typer.Argument(".", help="Path to watch for changes"),
    requirements_file: Path = typer.Option("requirements.txt", "--requirements-file", "-r", help="Requirements file to update"),
    interval: float = typer.Option(1.0, "--interval", "-i", help="Polling interval seconds for event loop tidy-up"),
    format_tool: str = typer.Option(None, "--format", help="Optionally format with black/isort/autopep8 on change"),
):
    """Watch for changes in Python files and auto-update requirements (disabled in Colab)."""
    utils.print_banner()

    if "google.colab" in sys.modules:
        typer.echo(" File watching is not supported in Google Colab.")
        raise typer.Exit(code=1)

    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        typer.echo(" Installing missing dependency: watchdog")
        install = run(pip_cmd("install", "watchdog"))
        if install.returncode != 0:
            echo_err(f"Failed to install watchdog:\n{install.stderr.strip()}")
            raise typer.Exit(code=1)
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

    class ImportChangeHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if not event.is_directory and event.src_path.endswith(".py"):
                typer.echo(f"\nChange detected: {event.src_path}")
                imports = scanner.scan_project_for_imports(str(path))
                try:
                    requirements.generate_requirements(imports, output_file=requirements_file, with_versions=True)
                    typer.echo(f"Updated {requirements_file}.")
                except Exception as e:
                    echo_err(f"Failed to update {requirements_file}: {e}")
                if format_tool:
                    if utils.is_tool_installed(format_tool):
                        try:
                            formatter.run_formatter(format_tool, str(path))
                            typer.echo(f"Ran {format_tool}.")
                        except ValueError as e:
                            echo_err(f"{e}")
                        except Exception as e:
                            echo_err(f"Formatter error: {e}")
                    else:
                        echo_err(f"'{format_tool}' isn't installed yet. Run: pip install {format_tool}")

    observer = Observer()
    handler = ImportChangeHandler()
    observer.schedule(handler, str(path), recursive=True)
    observer.start()
    typer.echo(f"👀 Watching {path} for changes... (Ctrl+C to stop)")

    try:
        while observer.is_alive():
            time.sleep(interval)
    except KeyboardInterrupt:
        typer.echo("\nStopping...")
    finally:
        observer.stop()
        observer.join()
        typer.echo("Stopped watching.")


if __name__ == "__main__":
    app()
