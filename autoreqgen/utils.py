import shutil
import importlib.util

def is_tool_installed(tool_name: str) -> bool:
    """Check if a CLI tool is installed and available in PATH."""
    return shutil.which(tool_name) is not None

def is_module_installed(module_name: str) -> bool:
    """Check if a Python module is installed in the environment."""
    spec = importlib.util.find_spec(module_name)
    return spec is not None

def clean_package_name(name: str) -> str:
    """Clean up a package name if needed (e.g., remove submodules)."""
    return name.strip().split('.')[0]

def print_banner():
    """Print a welcome banner."""
    print(r"""
     🚀 AutoReqGen 
    """)

# Test banner
if __name__ == "__main__":
    print_banner()
