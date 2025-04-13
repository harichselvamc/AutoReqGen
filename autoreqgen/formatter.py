import subprocess
import os

def run_formatter(tool: str, path: str = "."):
    """Run the specified formatter tool on the given path."""
    cmd = []

    if tool == "black":
        cmd = ["black", path]
    elif tool == "isort":
        cmd = ["isort", path]
    elif tool == "autopep8":
        cmd = ["autopep8", "--in-place", "--aggressive", "--recursive", path]
    else:
        raise ValueError("Unsupported formatter. Choose from: black, isort, autopep8.")

    print(f"🧹 Running {tool} on {path}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ {tool} formatting completed.")
    else:
        print(f"❌ {tool} failed:\n{result.stderr}")

# Optional direct run
if __name__ == "__main__":
    run_formatter("black", "./examples/sample_project1")
import subprocess
import shutil
import os

def run_formatter(tool: str, path: str = "."):
    """
    Run a formatter (black, isort, autopep8) on the specified path.

    Args:
        tool (str): The formatting tool to use ('black', 'isort', or 'autopep8').
        path (str): Directory or file to format.
    """
    tool = tool.lower()
    if shutil.which(tool) is None:
        print(f"⚠️  '{tool}' is not installed. Please run 'pip install {tool}' first.")
        return

    # Command mapping
    commands = {
        "black": ["black", path],
        "isort": ["isort", path],
        "autopep8": ["autopep8", "--in-place", "--aggressive", "--recursive", path]
    }

    if tool not in commands:
        print("❌ Unsupported formatter. Please choose from: black, isort, autopep8.")
        return

    cmd = commands[tool]
    print(f"🧹 Running '{tool}' formatter on '{path}'...")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ Successfully formatted using {tool}.")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ {tool} failed with error:")
        print(result.stderr)

# Optional direct test run
if __name__ == "__main__":
    run_formatter("black", "./examples/sample_project1")
