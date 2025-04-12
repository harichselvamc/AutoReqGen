import os
import ast

def get_all_python_files(directory: str):
    """Recursively fetch all Python files in a directory."""
    py_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))
    return py_files

def extract_imports_from_file(filepath: str):
    """Extract import statements from a Python file using AST."""
    with open(filepath, "r", encoding="utf-8") as f:
        node = ast.parse(f.read(), filename=filepath)

    imports = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Import):
            for alias in n.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(n, ast.ImportFrom):
            if n.module:
                imports.add(n.module.split('.')[0])
    return imports

def scan_project_for_imports(path: str):
    """Scan all Python files in a path and return unique imports."""
    all_imports = set()
    py_files = get_all_python_files(path)
    for file in py_files:
        all_imports.update(extract_imports_from_file(file))
    return sorted(all_imports)
