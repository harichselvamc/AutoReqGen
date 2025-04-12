import os
import ast

def extract_docstrings(file_path: str):
    """Extract module, class, and function docstrings from a Python file."""
    with open(file_path, "r", encoding="utf-8") as f:
        node = ast.parse(f.read(), filename=file_path)

    docs = []
    
    # Module docstring
    if (doc := ast.get_docstring(node)):
        docs.append(f"# Module: `{os.path.basename(file_path)}`\n\n{doc}\n")

    for n in ast.walk(node):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = n.name
            docstring = ast.get_docstring(n)
            if docstring:
                kind = "Function" if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) else "Class"
                docs.append(f"## {kind}: `{name}`\n\n{docstring}\n")

    return "\n".join(docs)


def generate_docs(path: str, output_file: str = "DOCUMENTATION.md"):
    """Generate Markdown documentation for all Python files in a path."""
    markdown = ["# 📚 Auto-Generated Documentation\n"]

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                doc = extract_docstrings(full_path)
                if doc:
                    markdown.append(doc)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(markdown))

    print(f"✅ Documentation saved to `{output_file}`")

# Optional run
if __name__ == "__main__":
    generate_docs("./autoreqgen")
