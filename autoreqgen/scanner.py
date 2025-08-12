# scanner.py
from __future__ import annotations
import os
import ast
import sys
import sysconfig
import importlib.util
from pathlib import Path
from typing import Iterable, Set, List

# Defaults to reduce noise
IGNORED_DIRS = {".venv", "venv", "env", ".git", "__pycache__", "build", "dist", ".mypy_cache", ".pytest_cache", "site-packages"}
ALWAYS_STDLIB = {"__future__"}

def _stdlib_names() -> Set[str]:
    names = set(getattr(sys, "stdlib_module_names", ()))
    # Backfill a few common ones across versions
    names.update(ALWAYS_STDLIB)
    return names

_STDLIB = _stdlib_names()
_STDLIB_PATH = sysconfig.get_paths().get("stdlib", "") or ""

def _is_stdlib(mod: str) -> bool:
    head = mod.split(".")[0]
    if head in _STDLIB:
        return True
    # Fallback heuristic via import location
    try:
        spec = importlib.util.find_spec(head)
    except (ImportError, ValueError):
        return False
    if not spec or not getattr(spec, "origin", None):
        return False
    origin = spec.origin or ""
    # treat anything in stdlib path as stdlib; exclude site/dist-packages
    if _STDLIB_PATH and origin.startswith(_STDLIB_PATH):
        return True
    if ("site-packages" in origin) or ("dist-packages" in origin):
        return False
    return False

def _iter_py_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        # prune ignored dirs in-place for performance
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for fn in filenames:
            if fn.endswith(".py"):
                yield Path(dirpath) / fn

def _discover_local_toplevels(root: Path) -> Set[str]:
    """
    Identify local/importable top-level names in the project:
    - module files (foo.py -> foo)
    - packages with __init__.py (pkg/ -> pkg)
    - namespace packages (directories with .py files, even without __init__.py)
    """
    locals_: Set[str] = set()
    for p in _iter_py_files(root):
        # module name
        if p.name.endswith(".py"):
            locals_.add(p.stem)
        # package/namespace (dir name)
        parent = p.parent
        if parent != root and parent.is_dir():
            locals_.add(parent.name)
    # also include the project root dir name (often used in imports for monorepos)
    locals_.add(root.name)
    return locals_

def _parse_directives(text: str) -> tuple[Set[str], Set[str]]:
    """
    Support inline directives inside source files:
      # autoreqgen: include pkgA,pkgB
      # autoreqgen: ignore moduleX,moduleY
    These are merged into the final result (include adds, ignore removes).
    """
    include: Set[str] = set()
    ignore: Set[str] = set()
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("# autoreqgen:"):
            rest = s[len("# autoreqgen:"):].strip()
            if rest.startswith("include"):
                items = rest[len("include"):].strip().lstrip(":").strip()
                include.update(x.strip().split(".")[0] for x in items.split(",") if x.strip())
            elif rest.startswith("ignore"):
                items = rest[len("ignore"):].strip().lstrip(":").strip()
                ignore.update(x.strip().split(".")[0] for x in items.split(",") if x.strip())
    return include, ignore

def _extract_imports_from_source(source: str, filename: str, include_type_checking: bool = False) -> Set[str]:
    try:
        node = ast.parse(source, filename=filename)
    except SyntaxError:
        return set()

    imports: Set[str] = set()
    inside_type_checking = [False]  # stack for If exp with typing.TYPE_CHECKING

    class Visitor(ast.NodeVisitor):
        def visit_If(self, n: ast.If):
            def is_type_checking(expr: ast.AST) -> bool:
                # matches: if TYPE_CHECKING: or if typing.TYPE_CHECKING:
                if isinstance(expr, ast.Name) and expr.id == "TYPE_CHECKING":
                    return True
                if isinstance(expr, ast.Attribute) and getattr(expr.value, "id", "") == "typing" and expr.attr == "TYPE_CHECKING":
                    return True
                return False

            is_tc = is_type_checking(n.test)
            inside_type_checking.append(is_tc or inside_type_checking[-1])
            self.generic_visit(n)
            inside_type_checking.pop()

        def visit_Import(self, n: ast.Import):
            if inside_type_checking[-1] and not include_type_checking:
                return
            for alias in n.names:
                head = alias.name.split(".")[0]
                imports.add(head)

        def visit_ImportFrom(self, n: ast.ImportFrom):
            if inside_type_checking[-1] and not include_type_checking:
                return
            # relative imports (from . or ..) are local; skip
            if getattr(n, "level", 0):
                return
            if n.module:
                head = n.module.split(".")[0]
                imports.add(head)

    Visitor().visit(node)
    return imports

def extract_imports_from_file(filepath: str, include_type_checking: bool = False) -> Set[str]:
    try:
        text = Path(filepath).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()
    imports = _extract_imports_from_source(text, filepath, include_type_checking=include_type_checking)
    inc, ign = _parse_directives(text)
    imports |= inc
    imports -= ign
    return imports

def get_all_python_files(directory: str) -> List[str]:
    return [str(p) for p in _iter_py_files(Path(directory))]

def scan_project_for_imports(path: str) -> List[str]:
    """
    Return external (non-stdlib, non-local) imports as sorted list of top-level names.
    - Filters stdlib using sys.stdlib_module_names / location heuristic.
    - Filters local modules/packages (incl. namespace packages).
    - Skips relative imports.
    - Honors inline directives.
    """
    root = Path(path).resolve()
    all_imports: Set[str] = set()
    local_names = _discover_local_toplevels(root)

    for file in _iter_py_files(root):
        all_imports |= extract_imports_from_file(str(file))

    # filter stdlib and locals
    external = {name for name in all_imports if not _is_stdlib(name) and name not in local_names}
    # never include empty and builtins marker
    external -= {""}
    return sorted(external, key=str.lower)

def extract_all_imports(path: str) -> List[str]:
    """
    Return all raw imports (top-level names) without stdlib/local filtering.
    Relative imports are omitted (since they are not top-level names).
    Honors inline include/ignore directives.
    """
    root = Path(path).resolve()
    all_imports: Set[str] = set()
    for file in _iter_py_files(root):
        all_imports |= extract_imports_from_file(str(file))
    all_imports -= {""}
    return sorted(all_imports, key=str.lower)
