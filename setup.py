from setuptools import setup, find_packages
from pathlib import Path

README = Path("README.md")
long_description = README.read_text(encoding="utf-8") if README.exists() else (
    "AutoReqGen is a smarter alternative to pipreqs that scans Python projects, "
    "generates accurate requirements.txt (optionally pinned), formats code, and "
    "builds Markdown docs from docstrings. One tool to automate and optimize your Python workflow."
)

setup(
    name="autoreqgen",
    version="0.1.26",
    description="Smarter pipreqs alternative with code formatting and documentation generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Harichselvam",
    author_email="harichselvamc@gmail.com",
    url="https://github.com/harichselvamc/AutoReqGen",
    project_urls={
        "Homepage": "https://github.com/harichselvamc/AutoReqGen",
        "Documentation": "https://github.com/harichselvamc/AutoReqGen#readme",
        "Source": "https://github.com/harichselvamc/AutoReqGen",
        "Repository": "https://github.com/harichselvamc/AutoReqGen",
        "Issues": "https://github.com/harichselvamc/AutoReqGen/issues",
        "Changelog": "https://github.com/harichselvamc/AutoReqGen/releases",
    },
    packages=find_packages(exclude=["tests*", "examples*", "scripts*", "docs*"]),
    include_package_data=True,
    license="MIT",
    python_requires=">=3.8",
    install_requires=[
        "typer>=0.9.0",
        "click>=8.1.0",
    ],
    extras_require={
        # pip install "autoreqgen[format]"
        "format": [
            "black>=23.0.0",
            "isort>=5.10.0",
            "autopep8>=2.0.0",
        ],
        # pip install "autoreqgen[watch]"
        "watch": [
            "watchdog>=2.1.0",
        ],
        # pip install "autoreqgen[dotenv]"
        "dotenv": [
            "python-dotenv>=1.0.0",
        ],
        # pip install "autoreqgen[dev]"
        "dev": [
            "pytest",
            "coverage",
            "mypy",
            "ruff",
            "types-setuptools",
        ],
    },
    entry_points={
        "console_scripts": [
            "autoreqgen=autoreqgen.cli:app",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
    keywords=["pipreqs", "automation", "requirements", "docgen", "formatter"],
)
