import pkg_resources

def get_installed_version(pkg_name: str):
    """Get the installed version of a package."""
    try:
        dist = pkg_resources.get_distribution(pkg_name)
        return dist.version
    except pkg_resources.DistributionNotFound:
        return None

def generate_requirements(imports: list, output_file: str = "requirements.txt"):
    """Generate a requirements.txt file with versions."""
    lines = []
    for pkg in imports:
        version = get_installed_version(pkg)
        if version:
            lines.append(f"{pkg}=={version}")
        else:
            print(f"⚠️  Warning: Package '{pkg}' not found in current environment. Skipping...")

    with open(output_file, "w") as f:
        f.write("\n".join(sorted(lines)))

    print(f"✅ requirements.txt generated with {len(lines)} packages.")
