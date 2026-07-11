# scaffold.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, List

TYPE_ALIASES = {
    "basic": "basic",
    "script": "basic",
    "cli": "cli",
    "web": "web",
    "webapp": "web",
    "flask": "web",
    "data": "data",
    "data-science": "data",
    "datascience": "data",
}

TEMPLATES: Dict[str, Dict[str, object]] = {
    "basic": {
        "main_filename": "main.py",
        "main_content": '''def main():
    print("Hello, world!")


if __name__ == "__main__":
    main()
''',
        "requirements": [],
    },
    "cli": {
        "main_filename": "main.py",
        "main_content": '''import typer

app = typer.Typer()


@app.command()
def hello(name: str = "world"):
    """Say hello."""
    typer.echo(f"Hello, {name}!")


if __name__ == "__main__":
    app()
''',
        "requirements": ["typer"],
    },
    "web": {
        "main_filename": "app.py",
        "main_content": '''from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello, world!"


if __name__ == "__main__":
    app.run(debug=True)
''',
        "requirements": ["flask"],
    },
    "data": {
        "main_filename": "main.py",
        "main_content": '''import pandas as pd


def main():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    print(df)


if __name__ == "__main__":
    main()
''',
        "requirements": ["pandas", "numpy"],
    },
}


def normalize_project_type(value: str) -> str:
    key = (value or "").strip().lower()
    if key in TYPE_ALIASES:
        return TYPE_ALIASES[key]
    valid = ", ".join(sorted(set(TYPE_ALIASES.values())))
    raise ValueError(f"Unknown project type '{value}'. Choose from: {valid}")


def default_gitignore_content(venv_name: str = ".venv") -> str:
    return (
        f"{venv_name}/\n"
        "__pycache__/\n"
        "*.pyc\n"
        ".env\n"
    )


def default_readme_content(project_name: str, project_type: str) -> str:
    return (
        f"# {project_name}\n\n"
        f"A {project_type} Python project, scaffolded with AutoReqGen.\n\n"
        "## Getting started\n\n"
        "```bash\n"
        "pip install -r requirements.txt\n"
        "```\n"
    )


def scaffold_project(
    dest: Path,
    project_name: str,
    project_type: str,
    venv_name: str = ".venv",
) -> List[str]:
    """
    Create a starter project layout in `dest`. Never overwrites existing files;
    returns a list of human-readable notes (one per file: "Created X" or "Skipped X (already exists)").
    """
    template = TEMPLATES[project_type]
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    notes: List[str] = []

    def write_if_absent(filename: str, content: str) -> None:
        path = dest / filename
        if path.exists():
            notes.append(f"Skipped {filename} (already exists)")
            return
        path.write_text(content, encoding="utf-8")
        notes.append(f"Created {filename}")

    write_if_absent(str(template["main_filename"]), str(template["main_content"]))
    write_if_absent("README.md", default_readme_content(project_name, project_type))
    write_if_absent(".gitignore", default_gitignore_content(venv_name))

    req_path = dest / "requirements.txt"
    if not req_path.exists():
        reqs = template["requirements"]
        req_path.write_text("\n".join(reqs) + ("\n" if reqs else ""), encoding="utf-8")
        notes.append("Created requirements.txt")
    else:
        notes.append("Skipped requirements.txt (already exists)")

    return notes
