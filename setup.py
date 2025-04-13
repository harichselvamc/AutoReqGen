from setuptools import setup, find_packages
import os

long_description = ""
if os.path.exists("README.md"):
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = (
        "AutoReqGen is a smarter alternative to pipreqs that recursively scans Python projects to extract import "
        "statements and generates accurate `requirements.txt` files with or without version numbers. "
        "It filters out standard libraries and local modules, ensuring clean installable requirements. "
        "Additionally, AutoReqGen supports Python code formatting using Black, isort, and autopep8, and can generate "
        "documentation from Python docstrings in Markdown format. It includes a CLI powered by Typer, along with "
        "options like `--all` to show full import sets, `--as-json` to export structured output for dev tools, "
        "`add` to install and register packages, `freeze` to lock dependencies, `start` to create virtual environments, "
        "and automatic `.env` and file watching support."
    )

setup(
    name="AutoReqGen",
    version="0.1.20",
    description="Smarter pipreqs alternative with code formatting and documentation generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Harichselvam",
    author_email="harichselvamc@gmail.com",
    url="https://github.com/harichselvamc/AutoReqGen",
    project_urls={
        "Documentation": "https://github.com/harichselvamc/AutoReqGen",
        "Source": "https://github.com/harichselvamc/AutoReqGen",
        "Issues": "https://github.com/harichselvamc/AutoReqGen/issues",
    },
    packages=find_packages(
        exclude=["tests*", "examples*", "scripts*", "docs*"]
    ),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    python_requires=">=3.8",
    install_requires=[
        "typer[all]",
        "black",
        "isort",
        "autopep8",
        "watchdog",        
        "python-dotenv",   
        "stdlib_list"      
    ],
    entry_points={
        "console_scripts": [
            "autoreqgen=autoreqgen.cli:app",
            "autoreqgen-generate=autoreqgen.cli:generate",
            "autoreqgen-g=autoreqgen.cli:generate"
        ],
    },
)
