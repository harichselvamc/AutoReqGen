import pkg_resources
from stdlib_list import stdlib_list
import sys

def get_installed_version(pkg_name: str):
    try:
        dist = pkg_resources.get_distribution(pkg_name)
        return dist.version
    except pkg_resources.DistributionNotFound:
        return None

def generate_requirements(imports: list, output_file: str = "requirements.txt", with_versions: bool = True):
    stdlib = set(stdlib_list(f"{sys.version_info.major}.{sys.version_info.minor}"))

    lines = []
    for pkg in imports:
        if pkg in stdlib:
            continue  # Skip standard library modules

        version = get_installed_version(pkg)
        if version and with_versions:
            lines.append(f"{pkg}=={version}")
        else:
            lines.append(pkg)

    with open(output_file, "w") as f:
        f.write("\n".join(sorted(lines)))

    print(f"✅ {output_file} generated with {len(lines)} packages (excluding stdlib).")
