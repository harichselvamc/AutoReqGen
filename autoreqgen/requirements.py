# requirements.py
from __future__ import annotations
import sys
import sysconfig
import importlib.util
from importlib import metadata
from pathlib import Path
from typing import Iterable, Dict, List, Set
import re

# Common import-name -> distribution-name aliases
ALIAS_MAP: Dict[str, str] = {
    "sklearn": "scikit-learn",
    "cv2": "opencv-python",
    "pil": "Pillow",          # normalized
    "yaml": "PyYAML",
    "bs4": "beautifulsoup4",
    "crypto": "pycryptodome", # normalized
    "openssl": "pyOpenSSL",   # normalized
    "dateutil": "python-dateutil",
    "win32api": "pywin32",
    "win32con": "pywin32",
    "win32gui": "pywin32",
    "jinja2": "Jinja2",
    "google": "google",  # namespace meta, still useful sometimes
}

def get_installed_version(pkg_name: str) -> str | None:
    """
    Return the installed version of a distribution, or None if not installed.
    (Compat shim for tests and external usage.)
    """
    try:
        return metadata.version(pkg_name)
    except metadata.PackageNotFoundError:
        # try normalized name
        try:
            return metadata.version(_pep503_normalize(pkg_name))
        except metadata.PackageNotFoundError:
            return None

def _pep503_normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()

def _stdlib_names() -> Set[str]:
    names = set(getattr(sys, "stdlib_module_names", ()))
    # Add a few always-stdlib names across versions
    names.update({"__future__", "typing", "dataclasses"})
    return names

_STDLIB = _stdlib_names()
_STDLIB_PATH = sysconfig.get_paths().get("stdlib", "") or ""

def _is_stdlib(mod: str) -> bool:
    head = mod.split(".")[0]
    if head in _STDLIB:
        return True
    spec = importlib.util.find_spec(head)
    # If module resolves and isn't under site-packages/dist-packages, treat as stdlib
    if spec and getattr(spec, "origin", None):
        origin = spec.origin or ""
        if _STDLIB_PATH and origin.startswith(_STDLIB_PATH):
            return True
        if ("site-packages" in origin) or ("dist-packages" in origin):
            return False
    return False

def _module_to_dists() -> Dict[str, List[str]]:
    # top-level module -> distributions providing it
    try:
        return metadata.packages_distributions() or {}
    except Exception:
        return {}

_MOD_TO_DISTS = _module_to_dists()
# also build a normalized index for robustness
_MOD_TO_DISTS_NORM: Dict[str, List[str]] = { _pep503_normalize(k): v for k, v in _MOD_TO_DISTS.items() }

def _resolve_import_to_dists(import_name: str) -> List[str]:
    head_raw = import_name.split(".")[0]
    head_norm = _pep503_normalize(head_raw)

    # prefer exact mapping
    dists = _MOD_TO_DISTS.get(head_raw)
    if dists:
        return dists

    # case/normalized mapping
    dists = _MOD_TO_DISTS_NORM.get(head_norm)
    if dists:
        return dists

    # alias map (handles common mismatches)
    if head_norm in ALIAS_MAP:
        return [ALIAS_MAP[head_norm]]

    # heuristic fallback: try the head itself as a dist name
    return [head_raw]

def _get_version(dist_name: str) -> str | None:
    try:
        return metadata.version(dist_name)
    except metadata.PackageNotFoundError:
        # try normalized name
        try:
            return metadata.version(_pep503_normalize(dist_name))
        except metadata.PackageNotFoundError:
            return None

def generate_requirements(
    imports: Iterable[str],
    output_file: str = "requirements.txt",
    with_versions: bool = True,
    include_unresolved: bool = False,
) -> None:
    """
    Generate a requirements.txt from discovered imports.

    - Filters stdlib imports.
    - Maps import names to distributions using importlib.metadata.
    - Pins versions if installed and with_versions=True.
    - If with_versions=True, unresolved dists are skipped (unless include_unresolved=True).
    - If with_versions=False, unresolved dists are included unpinned.
    - Dedupe & sort (case-insensitive).
    """
    unresolved: Set[str] = set()
    lines_by_norm: Dict[str, str] = {}

    for imp in set(imports):
        if not imp:
            continue
        if _is_stdlib(imp):
            continue

        dists = _resolve_import_to_dists(imp)
        if not dists:
            unresolved.add(imp)
            continue

        for dist in dists:
            norm = _pep503_normalize(dist)
            if with_versions:
                ver = _get_version(dist)
                if ver is None and not include_unresolved:
                    # skip unresolved when pinning
                    unresolved.add(imp)
                    continue
                line = f"{dist}=={ver}" if ver else dist
            else:
                # no pinning; include even if not installed
                line = dist

            # Prefer pinned over unpinned if we see the same dist twice
            existing = lines_by_norm.get(norm)
            if existing is None or ("==" in line and (existing and "==" not in existing)):
                lines_by_norm[norm] = line

    lines = [lines_by_norm[k] for k in sorted(lines_by_norm.keys(), key=str.lower)]
    # Write file with trailing newline
    Path(output_file).write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    print(f"✅ {output_file} generated with {len(lines)} packages (excluding stdlib).")
    if unresolved:
        # Non-fatal, but helpful hint
        hint = ", ".join(sorted(unresolved))
        print(f"ℹ️  Some imports didn’t map cleanly to a distribution: {hint}")
        print("    You may need to add them manually or install the missing packages.")
