# descriptions.py
from __future__ import annotations
from importlib import metadata

from autoreqgen.utils import pep503_normalize

# Keys are PEP-503-normalized distribution names.
CURATED: dict[str, str] = {
    # Web frameworks & servers
    "flask": "build small web applications and APIs",
    "django": "build full-featured web applications",
    "fastapi": "build fast, modern web APIs with automatic docs",
    "starlette": "a lightweight toolkit for building async web apps (used by FastAPI)",
    "uvicorn": "run async Python web apps (an ASGI server)",
    "gunicorn": "run Python web apps in production (a WSGI server)",
    "aiohttp": "make HTTP requests and build web servers asynchronously",
    "tornado": "build asynchronous web servers and network apps",
    "werkzeug": "low-level utilities for building web apps (used by Flask)",
    "jinja2": "generate text/HTML from templates",
    "markdown": "convert Markdown text into HTML",
    # HTTP / networking
    "requests": "send and receive HTTP requests easily",
    "httpx": "send HTTP requests, with support for async code",
    "urllib3": "low-level HTTP client used under the hood by requests",
    "websockets": "build real-time apps using WebSockets",
    "certifi": "provides a bundle of trusted SSL certificates",
    "idna": "handle internationalized domain names for networking libraries",
    "charset-normalizer": "detect text encoding for HTTP libraries",
    # Data & scientific computing
    "numpy": "fast numerical arrays and math operations",
    "pandas": "work with tabular data (like spreadsheets) in Python",
    "scipy": "scientific computing tools (stats, optimization, signal processing)",
    "matplotlib": "create charts and plots",
    "seaborn": "create nicer-looking statistical charts (built on matplotlib)",
    "plotly": "create interactive charts and dashboards",
    "sympy": "do symbolic math (algebra, calculus) in Python",
    "openpyxl": "read and write Excel (.xlsx) files",
    "xlrd": "read older Excel (.xls) files",
    # Machine learning / deep learning
    "scikit-learn": "build and evaluate machine learning models",
    "torch": "build and train deep learning (neural network) models",
    "tensorflow": "build and train machine learning models at scale",
    "keras": "build neural networks with a simple, high-level API",
    "xgboost": "train fast, accurate gradient-boosted tree models",
    "lightgbm": "train fast gradient-boosted tree models, optimized for large data",
    "transformers": "use pretrained AI language models (from Hugging Face)",
    "datasets": "load and process machine learning datasets (Hugging Face)",
    "nltk": "process and analyze human language text (NLP)",
    "spacy": "fast, production-ready natural language processing",
    # Jupyter / notebooks
    "jupyter": "run interactive notebooks that mix code, text, and charts",
    "notebook": "the classic Jupyter Notebook web interface",
    "ipython": "an enhanced interactive Python shell (powers Jupyter)",
    "ipykernel": "the Python engine that runs code inside Jupyter notebooks",
    # Testing
    "pytest": "write and run automated tests",
    "pytest-cov": "measure how much of your code is covered by tests",
    "tox": "run your tests against multiple Python versions/environments",
    "nose": "an older test discovery and running tool",
    "hypothesis": "generate randomized test cases to find edge-case bugs",
    "mock": "create fake ('mock') objects for testing",
    "coverage": "measure how much of your code is exercised by tests",
    "faker": "generate realistic fake data (names, emails, etc.) for tests",
    # Formatting / linting / typing
    "black": "automatically format Python code to a standard style",
    "isort": "automatically sort and organize import statements",
    "autopep8": "automatically reformat code to follow PEP 8 style",
    "ruff": "quickly lint (find issues in) and format Python code",
    "flake8": "check Python code for style issues and simple bugs",
    "pylint": "analyze Python code for errors and style problems",
    "mypy": "check your code for type errors before running it",
    "pre-commit": "run automated checks on your code before each git commit",
    # CLI tooling
    "typer": "build command-line interfaces (CLI apps) easily",
    "click": "build command-line interfaces (used under the hood by many CLI tools)",
    "argparse": "the standard library tool for building command-line interfaces",
    "rich": "print colorful, nicely formatted text and tables in the terminal",
    "colorama": "add colored text output in the terminal (cross-platform)",
    "tqdm": "add progress bars to loops and long-running tasks",
    "questionary": "build interactive command-line prompts and menus",
    # Data validation / config
    "pydantic": "validate and parse data using Python type hints",
    "python-dotenv": "load configuration from a .env file into your environment",
    "pyyaml": "read and write YAML configuration files",
    "toml": "read and write TOML configuration files",
    "attrs": "reduce boilerplate when writing Python classes",
    "marshmallow": "validate and convert data to/from Python objects (serialization)",
    "cerberus": "validate data against a defined schema",
    # Databases
    "sqlalchemy": "talk to databases using Python objects instead of raw SQL",
    "alembic": "manage database schema changes (migrations) for SQLAlchemy",
    "psycopg2-binary": "connect to and query PostgreSQL databases",
    "pymongo": "connect to and query MongoDB databases",
    "redis": "talk to a Redis in-memory database/cache",
    "sqlite3": "the standard library tool for working with SQLite databases",
    "peewee": "a small, simple ORM for working with databases",
    # Async / background tasks
    "celery": "run background/async tasks outside your main app",
    "asyncio": "the standard library toolkit for writing asynchronous code",
    "apscheduler": "schedule Python functions to run later or on a recurring basis",
    # Cloud / infra
    "boto3": "interact with Amazon Web Services (AWS) from Python",
    "botocore": "low-level AWS functionality used under the hood by boto3",
    "google-cloud-storage": "read and write files in Google Cloud Storage",
    "azure-storage-blob": "read and write files in Azure Blob Storage",
    "docker": "control Docker containers from Python",
    "paramiko": "connect to remote servers over SSH",
    # Scraping / parsing
    "beautifulsoup4": "parse and extract data from HTML/XML (web scraping)",
    "scrapy": "a full framework for large-scale web scraping",
    "selenium": "automate and control a real web browser from Python",
    "lxml": "fast XML/HTML parsing library",
    # Images / media
    "pillow": "open, edit, and save images",
    "opencv-python": "process images and video (computer vision)",
    "pydub": "edit and convert audio files",
    "moviepy": "edit and process video files",
    # Security / auth
    "cryptography": "encrypt data and work with security certificates/keys",
    "pyjwt": "create and verify JSON Web Tokens (JWTs) for authentication",
    "bcrypt": "securely hash passwords",
    "passlib": "hash and verify passwords using multiple algorithms",
    "oauthlib": "implement OAuth authentication flows",
    # File / date utils
    "watchdog": "watch files/folders for changes and react automatically",
    "python-dateutil": "parse and work with dates and times more flexibly",
    "pytz": "work with timezones",
    "arrow": "a friendlier way to work with dates and times",
    "click-completion": "add shell autocomplete to command-line tools",
    # Packaging / distribution
    "setuptools": "the standard tool for packaging Python projects",
    "wheel": "build Python packages into an installable format",
    "build": "build Python source and wheel distributions",
    "twine": "upload Python packages to PyPI",
    "packaging": "parse and compare version numbers and package metadata",
    "six": "help code run on both Python 2 and 3 (legacy compatibility)",
}


def describe(package_name: str) -> str:
    """
    Return a short, plain-English description of a package.

    Lookup order: curated dictionary -> installed package's PyPI summary -> fallback.
    Never raises and never makes a network call.
    """
    normalized = pep503_normalize(package_name)
    if normalized in CURATED:
        return CURATED[normalized]

    try:
        summary = metadata.metadata(package_name).get("Summary")
        if summary:
            return summary.strip()
    except Exception:
        pass

    return "No description available."
