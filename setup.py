from setuptools import setup, find_packages

setup(
    name="AutoReqGen",
    version="0.1.4",
    description="Smarter pipreqs alternative with code formatting and documentation generation",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Harichselvam",
    author_email="harichselvamc@gmail.com",
    url="https://github.com/harichselvam/AutoReqGen",
    project_urls={
        "Documentation": "https://github.com/harichselvam/AutoReqGen",
        "Source": "https://github.com/harichselvam/AutoReqGen",
        "Issues": "https://github.com/harichselvam/AutoReqGen/issues",
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
    python_requires=">=3.7",
    install_requires=[
        "typer[all]",
        "black",
        "isort",
        "autopep8"
    ],
    entry_points={
        "console_scripts": [
            "autoreqgen=autoreqgen.cli:app",
        ],
    },
)
