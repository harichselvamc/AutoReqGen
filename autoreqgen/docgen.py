import os
import ast
from pathlib import Path
from typing import Iterable, Optional, List, Tuple

IGNORED_DIRS_DEFAULT = {".venv", "venv", "env", ".git", "__pycache__", "build", "dist"}


def _md_escape(text: str) -> str:
    # Basic escaping for Markdown headings/inline code contexts
    return text.replace("<", "&lt;").replace(">", "&gt;")


def _unparse(node: Optional[ast.AST]) -> str:
    if node is None:
        return ""
    # Python 3.9+ ast.unparse; fallback to best-effort repr
    unparse = getattr(ast, "unparse", None)
    if callable(unparse):
        try:
            return unparse(node)
        except Exception:
            pass
    return _md_escape(ast.dump(node))


def _default_repr(node: ast.AST) -> str:
    # Try to produce a human-ish default value for signatures
    try:
        if isinstance(node, ast.Constant):
            return repr(node.value)
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, (ast.List, ast.Tuple, ast.Set, ast.Dict)):
            return _unparse(node)
        return _unparse(node)
    except Exception:
        return _unparse(node)


def _format_args(args: ast.arguments) -> str:
    parts: List[str] = []
    # pos-only (3.8+)
    posonly = getattr(args, "posonlyargs", [])
    all_pos = list(posonly) + list(args.args)
    defaults = list(args.defaults or [])
    # Right-align defaults to the last N positional args
    pos_defaults_start = len(all_pos) - len(defaults)
    for i, a in enumerate(all_pos):
        s = a.arg
        if a.annotation:
            s += f": {_unparse(a.annotation)}"
        if i >= pos_defaults_start:
            d = defaults[i - pos_defaults_start]
            s += f" = {_default_repr(d)}"
        parts.append(s)
        if i == len(posonly) - 1 and posonly:
            parts.append("/")  # marker for pos-only
    # vararg
    if args.vararg:
        s = "*" + args.vararg.arg
        if args.vararg.annotation:
            s += f": {_unparse(args.vararg.annotation)}"
        parts.append(s)
    # kw-only separator if needed
    if args.kwonlyargs and not args.vararg:
        parts.append("*")
    # kw-only with defaults
    for a, d in zip(args.kwonlyargs, args.kw_defaults or [None] * len(args.kwonlyargs)):
        s = a.arg
        if a.annotation:
            s += f": {_unparse(a.annotation)}"
        if d is not None:
            s += f" = {_default_repr(d)}"
        parts.append(s)
    # kwarg
    if args.kwarg:
        s = "**" + args.kwarg.arg
        if args.kwarg.annotation:
            s += f": {_unparse(args.kwarg.annotation)}"
        parts.append(s)
    return ", ".join(parts)


def _signature(node: ast.AST) -> str:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        sig = f"({_format_args(node.args)})"
        ret = _unparse(node.returns) if getattr(node, "returns", None) else ""
        if ret:
            sig += f" -> {ret}"
        return sig
    if isinstance(node, ast.ClassDef):
        # Try __init__ signature if present
        init_fn = next(
            (b for b in node.body if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)) and b.name == "__init__"),
            None,
        )
        if init_fn:
            sig = _signature(init_fn)
            # strip self/cls first param from display for class constructor
            if sig.startswith("(") and "," in sig:
                inside = sig[1 : sig.index(")")]
                params = [p.strip() for p in inside.split(",")]
                if params:
                    params = params[1:]  # drop self
                sig = "(" + ", ".join(params) + ")"
            return sig
        return "()"
    return ""


def _is_property(fn: ast.FunctionDef) -> bool:
    for d in fn.decorator_list:
        name = getattr(d, "id", None) or getattr(d, "attr", None) or ""
        if name == "property":
            return True
    return False


def _is_private(name: str) -> bool:
    return name.startswith("_")


def _summary_and_body(doc: str) -> Tuple[str, str]:
    lines = (doc or "").strip().splitlines()
    if not lines:
        return "", ""
    summary = lines[0].strip()
    body = "\n".join(lines[1:]).strip()
    return summary, body


def _safe_relpath(path: str | Path, start: str | Path = ".") -> str:
    """
    Return a relative path where possible; if paths are on different drives
    (Windows), fall back to basename.
    """
    try:
        return os.path.relpath(path, start=start)
    except ValueError:
        # Different drives; use filename for a stable doc title
        return os.path.basename(os.fspath(path))


def extract_docstrings(file_path: str, include_private: bool = False) -> str:
    """
    Extract module, class, and function docstrings from a Python file,
    grouped by module and classes with signatures.

    Returns Markdown.
    """
    try:
        source = Path(file_path).read_text(encoding="utf-8")
        node = ast.parse(source, filename=file_path)
    except (SyntaxError, UnicodeDecodeError) as e:
        return f"<!-- Skipped {file_path} due to parsing error: {e} -->\n"

    rel_path = _safe_relpath(file_path)
    out: List[str] = []

    # Module header
    mod_doc = ast.get_docstring(node) or ""
    mod_summary, mod_body = _summary_and_body(mod_doc)
    out.append(f"##  Module: `{_md_escape(rel_path)}`")
    if mod_summary:
        out.append(f"\n> {_md_escape(mod_summary)}\n")
    if mod_body:
        out.append(f"\n{_md_escape(mod_body)}\n")

    # Collect top-level functions and classes
    functions: List[ast.AST] = []
    classes: List[ast.ClassDef] = []
    for n in node.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if include_private or not _is_private(n.name):
                functions.append(n)
        elif isinstance(n, ast.ClassDef):
            if include_private or not _is_private(n.name):
                classes.append(n)

    # Functions section
    if functions:
        out.append("\n### Functions\n")
        for fn in sorted(functions, key=lambda x: x.name):  # type: ignore[attr-defined]
            name = fn.name  # type: ignore[attr-defined]
            doc = ast.get_docstring(fn) or ""
            summary, body = _summary_and_body(doc)
            sig = _signature(fn)
            async_prefix = "async " if isinstance(fn, ast.AsyncFunctionDef) else ""
            out.append(f"#### `{async_prefix}{name}{sig}`\n")
            if summary:
                out.append(f"{_md_escape(summary)}\n")
            if body:
                out.append("\n```python\n" + body.strip() + "\n```\n")

    # Classes section
    if classes:
        out.append("\n### Classes\n")
        for cls in sorted(classes, key=lambda c: c.name):
            cls_sig = _signature(cls)
            out.append(f"#### `class {cls.name}{cls_sig}`\n")
            cdoc = ast.get_docstring(cls) or ""
            csum, cbody = _summary_and_body(cdoc)
            if csum:
                out.append(f"{_md_escape(csum)}\n")
            if cbody:
                out.append("\n```python\n" + cbody.strip() + "\n```\n")

            # Methods/properties
            methods: List[ast.FunctionDef] = []
            for n in cls.body:
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if include_private or not _is_private(n.name):
                        methods.append(n)

            if methods:
                # mini-TOC
                out.append(
                    "\n**Members:** " + ", ".join(f"`{m.name}`" for m in sorted(methods, key=lambda m: m.name)) + "\n"
                )
                for m in sorted(methods, key=lambda m: m.name):
                    doc = ast.get_docstring(m) or ""
                    msum, mbody = _summary_and_body(doc)
                    prop_prefix = "@property " if _is_property(m) else ""
                    msig = _signature(m)
                    async_prefix = "async " if isinstance(m, ast.AsyncFunctionDef) else ""
                    out.append(f"\n##### `{prop_prefix}{async_prefix}{m.name}{msig}`\n")
                    if msum:
                        out.append(f"{_md_escape(msum)}\n")
                    if mbody:
                        out.append("\n```python\n" + mbody.strip() + "\n```\n")

    return "\n".join(out).strip() + "\n"


def _iter_py_files(root: Path, ignored_dirs: Iterable[str]) -> Iterable[Path]:
    ignored = set(ignored_dirs)
    for p in root.rglob("*.py"):
        # skip if any part is in the ignored set
        if any(part in ignored for part in p.parts):
            continue
        yield p


def generate_docs(
    path: str,
    output_file: str = "DOCUMENTATION.md",
    include_private: bool = False,
    ignore_dirs: Optional[Iterable[str]] = None,
):
    """
    Generate Markdown documentation for all Python files in a directory recursively.

    Args:
        path: Directory or file path to scan.
        output_file: Markdown file to write.
        include_private: Include names starting with '_' if True.
        ignore_dirs: Iterable of directory names to ignore (exact matches).
    """
    root = Path(path)
    if not root.exists():
        print(f" Path not found: {root}")
        return

    if root.is_file() and root.suffix == ".py":
        files: List[Path] = [root]
    else:
        files = sorted(_iter_py_files(root, ignore_dirs or IGNORED_DIRS_DEFAULT), key=lambda p: str(p).lower())

    sections: List[str] = ["#  Auto-Generated Documentation\n"]
    toc: List[str] = ["\n## Table of Contents\n"]

    for fp in files:
        sec = extract_docstrings(str(fp), include_private=include_private)
        if not sec.strip():
            continue
        sections.append(sec)
        # ToC entry with drive-safe relative path
        rel = _safe_relpath(fp)
        toc.append(f"- `{rel}`")

    # Join with separators; put ToC right after title
    content = "\n".join([sections[0], *toc, "\n---\n", "\n---\n".join(sections[1:])]).strip() + "\n"

    Path(output_file).write_text(content, encoding="utf-8")
    print(f" Documentation saved to `{output_file}`")


if __name__ == "__main__":
    generate_docs("./autoreqgen", include_private=False)
