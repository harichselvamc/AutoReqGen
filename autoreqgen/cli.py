import typer
import json
import subprocess
import platform
import sys
import time
from pathlib import Path
from typing import List

from autoreqgen import scanner, requirements, formatter, docgen, utils

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = typer.Typer(
    help="🚀 AutoReqGen – Smarter Python dependency and tooling assistant.",
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
            typer.echo(f"📦 {imp}")
        typer.echo(f"\n✅ Found {len(imports)} unique imports.")


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
        typer.echo(f"✅ Wrote {output}")
    except Exception as e:
        echo_err(f"❌ Failed to generate {output}: {e}")
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
        echo_err("❌ No formatter provided.")
        raise typer.Exit(code=1)

    # Pre-check installation for each requested tool to give fast feedback
    for t in tools:
        if not utils.is_tool_installed(t):
            echo_err(f"❌ Error: `{t}` is not installed.")
            raise typer.Exit(code=1)

    for t in tools:
        typer.echo(f"🧹 Running {t} on {path} ...")
        try:
            formatter.run_formatter(t, str(path))
        except ValueError as e:
            # Unknown tool -> exit with clear message
            echo_err(f"❌ {e}")
            raise typer.Exit(code=1)
        except Exception as e:
            echo_err(f"❌ {t} failed: {e}")
            raise typer.Exit(code=1)
    typer.echo("✅ Formatting complete.")


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
        typer.echo(f"✅ Documentation saved to {output}")
    except Exception as e:
        echo_err(f"❌ Failed to generate docs: {e}")
        raise typer.Exit(code=1)


@app.command()
def add(
    package: str = typer.Argument(..., help='Package specifier, e.g. "requests" or "requests>=2.25.0"'),
    path: Path = typer.Option(Path("requirements.txt"), "--path", "-p", help="Path to requirements file"),
):
    """Install a package and add it to requirements.txt (without version pinning unless specified)."""
    utils.print_banner()
    typer.echo(f"📦 Installing {package} ...")
    result = run(pip_cmd("install", package))
    if result.returncode != 0:
        echo_err(f"❌ Failed to install {package}:\n{result.stderr.strip()}")
        raise typer.Exit(code=1)

    if not path.exists():
        typer.echo(f"📄 Creating {path} ...")
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

    typer.echo(f"✅ Added to {path} (sorted & deduplicated)")


@app.command()
def freeze(output: str = typer.Option("requirements.txt", "--output", "-o", help="Output requirements file")):
    """Freeze the current environment and write exact package versions to a file."""
    utils.print_banner()
    typer.echo(f"📄 Freezing environment to {output} ...")
    result = run(pip_cmd("freeze"))
    if result.returncode != 0:
        echo_err(f"❌ Failed to freeze environment:\n{result.stderr.strip()}")
        raise typer.Exit(code=1)

    frozen = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    frozen_sorted = sorted(frozen, key=str.lower)
    Path(output).write_text("\n".join(frozen_sorted) + "\n")
    typer.echo(f"✅ Environment frozen, sorted, and saved to {output}")


@app.command()
def start(
    python: str = typer.Option(None, "--python", help="Path to python executable to use"),
    name: str = typer.Option(None, "--name", "-n", help="Name for the virtual environment (default: .venv)"),
    packages: str = typer.Option(None, "--packages", "-r", help='Optional packages to install, e.g. "requests pandas"'),
):
    """Create a new virtual environment (non-Colab) and optionally install packages."""
    utils.print_banner()

    if "google.colab" in sys.modules:
        typer.echo("⚠️  Virtual environment creation is not supported in Google Colab.")
        raise typer.Exit(code=1)

    env_name = name or ".venv"

    # Resolve python executable
    selected_python = python
    if not selected_python:
        # List available pythons
        cmd = "where python" if platform.system() == "Windows" else "which -a python"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        python_paths = [line.strip() for line in result.stdout.splitlines() if "python" in line.lower()]
        if not python_paths:
            echo_err("❌ No Python executables found.")
            raise typer.Exit(code=1)

        typer.echo("\nAvailable Python executables:")
        for i, p in enumerate(python_paths, start=1):
            typer.echo(f"  [{i}] {p}")

        choice = typer.prompt("Choose Python (number)", type=int)
        try:
            selected_python = python_paths[choice - 1]
        except Exception:
            echo_err("❌ Invalid choice.")
            raise typer.Exit(code=1)

    typer.echo(f"\n🐍 Creating virtual environment `{env_name}` with {selected_python} ...")
    result = subprocess.run([selected_python, "-m", "venv", env_name], capture_output=True, text=True)
    if result.returncode != 0:
        echo_err(f"❌ Failed to create virtual environment:\n{result.stderr.strip()}")
        raise typer.Exit(code=1)

    typer.echo(f"✅ Virtual environment `{env_name}` created successfully.")
    if platform.system() == "Windows":
        typer.echo(f"💡 Activate: .\\{env_name}\\Scripts\\activate")
    else:
        typer.echo(f"💡 Activate: source ./{env_name}/bin/activate")

    if packages:
        typer.echo(f"📦 Installing packages into `{env_name}`: {packages}")
        # Use the venv's pip
        venv_python = Path(env_name) / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")
        install = subprocess.run([str(venv_python), "-m", "pip", "install", *packages.split()], capture_output=True, text=True)
        if install.returncode != 0:
            echo_err(f"⚠️  Packages install reported errors:\n{install.stderr.strip()}")
        else:
            typer.echo("✅ Packages installed.")


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
        typer.echo("⚠️  File watching is not supported in Google Colab.")
        raise typer.Exit(code=1)

    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        typer.echo("⚙️ Installing missing dependency: watchdog")
        install = run(pip_cmd("install", "watchdog"))
        if install.returncode != 0:
            echo_err(f"❌ Failed to install watchdog:\n{install.stderr.strip()}")
            raise typer.Exit(code=1)
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

    class ImportChangeHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if not event.is_directory and event.src_path.endswith(".py"):
                typer.echo(f"\n🔁 Change detected: {event.src_path}")
                imports = scanner.scan_project_for_imports(str(path))
                try:
                    requirements.generate_requirements(imports, output_file=requirements_file, with_versions=True)
                    typer.echo(f"✅ Updated {requirements_file}.")
                except Exception as e:
                    echo_err(f"❌ Failed to update {requirements_file}: {e}")
                if format_tool:
                    if utils.is_tool_installed(format_tool):
                        try:
                            formatter.run_formatter(format_tool, str(path))
                            typer.echo(f"🧹 Ran {format_tool}.")
                        except ValueError as e:
                            echo_err(f"❌ {e}")
                        except Exception as e:
                            echo_err(f"❌ Formatter error: {e}")
                    else:
                        echo_err(f"❌ `{format_tool}` is not installed.")

    observer = Observer()
    handler = ImportChangeHandler()
    observer.schedule(handler, str(path), recursive=True)
    observer.start()
    typer.echo(f"👀 Watching {path} for changes... (Ctrl+C to stop)")

    try:
        while observer.is_alive():
            time.sleep(interval)
    except KeyboardInterrupt:
        typer.echo("\n👋 Stopping...")
    finally:
        observer.stop()
        observer.join()
        typer.echo("✅ Stopped watching.")


if __name__ == "__main__":
    app()
