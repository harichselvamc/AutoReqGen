import typer
import json
from pathlib import Path

from autoreqgen import scanner, requirements, formatter, docgen, utils

app = typer.Typer(help="🚀 AutoReqGen – Smarter Python dependency and tooling assistant.")

@app.command()
def scan(
    path: Path = typer.Argument(..., help="Path to your Python project"),
    all: bool = typer.Option(False, "--all", help="Include local and standard library modules"),
    as_json: bool = typer.Option(False, "--as-json", help="Output results in JSON format")
):
    """Scan the project and list all imported packages."""
    utils.print_banner()

    if all:
        imports = scanner.extract_all_imports(str(path))
    else:
        imports = scanner.scan_project_for_imports(str(path))

    if as_json:
        typer.echo(json.dumps(imports, indent=2))
    else:
        for imp in imports:
            typer.echo(f"📦 {imp}")
        typer.echo(f"\n✅ Found {len(imports)} unique imports.")

@app.command()
def generate(
    path: Path = typer.Argument(..., help="Path to your Python project"),
    output: str = typer.Option("requirements.txt", help="Output file name"),
    with_versions: bool = typer.Option(True, help="Include version numbers in requirements.txt")
):
    """Generate requirements.txt with or without versions."""
    utils.print_banner()
    imports = scanner.scan_project_for_imports(str(path))
    requirements.generate_requirements(imports, output_file=output, with_versions=with_versions)

@app.command()
def format(
    tool: str = typer.Argument(..., help="Choose from: black, isort, autopep8"),
    path: Path = typer.Argument(".", help="Target path for formatting")
):
    """Format code using Black, isort, or autopep8."""
    utils.print_banner()
    if not utils.is_tool_installed(tool):
        typer.echo(f"❌ Error: `{tool}` is not installed.")
        raise typer.Exit(code=1)
    formatter.run_formatter(tool, str(path))

@app.command()
def docs(
    path: Path = typer.Argument(..., help="Path to your Python code"),
    output: str = typer.Option("DOCUMENTATION.md", help="Output Markdown file")
):
    """Generate documentation from docstrings."""
    utils.print_banner()
    docgen.generate_docs(str(path), output_file=output)

if __name__ == "__main__":
    app()
