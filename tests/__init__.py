"""
AutoReqGen Test Suite
=====================

This package contains unit tests for all modules in AutoReqGen.

You can run all tests with:

    pytest

Or with unittest discovery:

    python -m unittest discover -s tests

Modules exposed via __all__ for explicit imports.
"""

import importlib
import pkgutil

__all__ = [
    "test_scanner",
    "test_requirements",
    "test_formatter",
    "test_docgen",
    "test_cli",
]

# Auto-import all modules in __all__ for unittest discovery if run as `python -m tests`
for name in __all__:
    importlib.import_module(f"{__name__}.{name}")

# Optional: support running tests directly with `python -m tests`
if __name__ == "__main__":
    import unittest
    unittest.main(module=None)
