from setuptools import setup, find_packages
import os

# Long description from README.md or fallback
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
        "documentation from Python docstrings in Markdown format. Includes features like CLI support, aliases, file "
        "watching, virtualenv creation, .env loading, and freeze command. One tool to automate and optimize your Python workflow."
    )

setup(
    name="AutoReqGen",
    version="0.1.23",
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
        "Development Status :: 4 - Beta",
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
        "stdlib-list",
        "setuptools",
    ],
    entry_points={
        "console_scripts": [
            "autoreqgen=autoreqgen.cli:app",
        ],
    },
)
