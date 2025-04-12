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
