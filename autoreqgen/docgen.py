import os
import ast
from pathlib import Path

def extract_docstrings(file_path: str, include_private: bool = False) -> str:
    """
    Extract module, class, and function docstrings from a Python file.

    Args:
        file_path (str): Path to the Python file.
        include_private (bool): Whether to include private methods and classes (starting with "_").

    Returns:
        str: Markdown-formatted string of extracted docstrings.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        node = ast.parse(source, filename=file_path)
    except (SyntaxError, UnicodeDecodeError) as e:
        return f"<!-- Skipped {file_path} due to parsing error: {e} -->\n"

    docs = []
    rel_path = os.path.relpath(file_path)
    
    # Module docstring
    if (doc := ast.get_docstring(node)):
        docs.append(f"### 📄 Module: `{rel_path}`\n\n{doc.strip()}\n")

    for n in ast.walk(node):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = n.name
            if not include_private and name.startswith("_"):
                continue
            kind = "Function" if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) else "Class"
            docstring = ast.get_docstring(n)
            if docstring:
                docs.append(f"#### {kind}: `{name}`\n\n```python\n{docstring.strip()}\n```\n")

    return "\n".join(docs)


def generate_docs(path: str, output_file: str = "DOCUMENTATION.md", include_private: bool = False):
    """
    Generate Markdown documentation for all Python files in a directory recursively.

    Args:
        path (str): Directory path to scan.
        output_file (str): File path to write the Markdown output.
        include_private (bool): Include private functions/classes (default: False)
    """
    markdown = ["# 📚 Auto-Generated Documentation\n"]

    path = Path(path)
    if not path.exists():
        print(f"❌ Path not found: {path}")
        return

    for file_path in path.rglob("*.py"):
        doc = extract_docstrings(str(file_path), include_private=include_private)
        if doc:
            markdown.append(doc)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n---\n".join(markdown))

    print(f"✅ Documentation saved to `{output_file}`")


if __name__ == "__main__":
    generate_docs("./autoreqgen", include_private=False)
