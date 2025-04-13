import os
import ast
import sys
from stdlib_list import stdlib_list

def get_all_python_files(directory: str):
    py_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))
    return py_files

def extract_imports_from_file(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            node = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            return set()  # skip files with syntax errors

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
    all_imports = set()
    py_files = get_all_python_files(path)

    # Local module names (file names without .py)
    local_modules = {
        os.path.splitext(os.path.basename(f))[0]
        for f in py_files
    }

    # Python stdlib for current version
    stdlib = set(stdlib_list(f"{sys.version_info.major}.{sys.version_info.minor}"))

    for file in py_files:
        all_imports.update(extract_imports_from_file(file))

    # Filter out local modules and standard library
    external_imports = sorted(all_imports - local_modules - stdlib)
    return external_imports
def extract_all_imports(path: str):
    """Return all raw imports without filtering (for --all mode)."""
    all_imports = set()
    py_files = get_all_python_files(path)
    for file in py_files:
        all_imports.update(extract_imports_from_file(file))
    return sorted(all_imports)
