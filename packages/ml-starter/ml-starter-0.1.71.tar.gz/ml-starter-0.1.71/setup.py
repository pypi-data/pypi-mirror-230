#!/usr/bin/env python
"""Setup script for the ml-starter project."""

import re

from setuptools import setup

REQUIREMENTS_DEV = [
    "black",
    "darglint",
    "mypy",
    "pytest",
    "pytest-timeout",
    "ruff",
]

REQUIREMENTS_DOCS = [
    "myst-parser",
    "sphinx==6.2.1",
    "sphinxcontrib-jquery",
    "sphinx-rtd-theme",
    "sphinx-autodoc-typehints",
]


with open("README.md", "r", encoding="utf-8") as f:
    long_description: str = f.read()


with open("ml/requirements.txt", "r", encoding="utf-8") as f:
    requirements: list[str] = f.read().splitlines()


with open("ml/__init__.py", "r", encoding="utf-8") as fh:
    version_re = re.search(r"^__version__ = \"([^\"]*)\"", fh.read(), re.MULTILINE)
assert version_re is not None, "Could not find version in ml/__init__.py"
version: str = version_re.group(1)


setup(
    name="ml-starter",
    version=version,
    description="ML project template repository",
    author="Benjamin Bolte",
    url="https://github.com/codekansas/ml-starter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    tests_require=REQUIREMENTS_DEV,
    extras_require={"dev": REQUIREMENTS_DEV, "docs": REQUIREMENTS_DOCS},
    package_data={"ml": ["py.typed", "requirements.txt"]},
)
