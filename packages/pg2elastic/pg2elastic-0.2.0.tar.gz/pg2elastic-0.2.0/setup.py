#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import os
import re

from setuptools import find_packages, setup

HERE = os.path.dirname(os.path.abspath(__file__))


def get_version() -> str:
    filename: str = os.path.join(HERE, "pg2elastic", "__init__.py")
    with open(filename) as fp:
        contents = fp.read()
    pattern = r"^__version__ = \"(.*?)\"$"
    return re.search(pattern, contents, re.MULTILINE).group(1)


# Package meta-data.
NAME = "pg2elastic"
DESCRIPTION = "Enhanced PostgreSQL to Elasticsearch Data Synchronization"
URL = "https://github.com/robert-walters/pg2elastic"
AUTHOR = MAINTAINER = "Dorin Musteata RW"
AUTHOR_EMAIL = MAINTAINER_EMAIL = "dorin.musteata-contractor@robertwalters.com"
PYTHON_REQUIRES = ">=3.7.0"
VERSION = get_version()
INSTALL_REQUIRES = []
KEYWORDS = [
    "pg2elastic",
    "elasticsearch",
    "postgres",
    "change data capture",
]
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
]
SCRIPTS = [
    "bin/pg2elastic",
    "bin/bootstrap",
]
SETUP_REQUIRES = ["pytest-runner"]
TESTS_REQUIRE = ["pytest"]

# if building the source dist then add the sources
PACKAGES = find_packages(include=["pg2elastic"])

with open("README.md") as fp:
    README = fp.read()

with open("requirements/prod.txt") as fp:
    INSTALL_REQUIRES = fp.read()

setup(
    name=NAME,
    author=AUTHOR,
    license="LGPLv3",
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    author_email=AUTHOR_EMAIL,
    classifiers=CLASSIFIERS,
    python_requires=PYTHON_REQUIRES,
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown",
    install_requires=INSTALL_REQUIRES,
    include_package_data=True,
    keywords=KEYWORDS,
    packages=PACKAGES,
    setup_requires=SETUP_REQUIRES,
    scripts=SCRIPTS,
    test_suite="tests",
    tests_require=TESTS_REQUIRE,
    url=URL,
    version=VERSION,
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/robert-walters/pg2elastic/issues",
        "Source": URL,
    },
)
