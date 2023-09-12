#!/usr/bin/env python
import io
import re

from setuptools import setup, find_packages
from collections import OrderedDict

DESCRIPTION = "Database connector."
with open("README.rst") as f:
    LONG_DESCRIPTION = f.read()

with io.open("dbcc/__init__.py", "rt", encoding="utf8") as f:
    VERSION = re.search(r"__version__ = \"(.*?)\"", f.read()).group(1)

INSTALL_REQUIRES = [
    "pymongo==4.5.0",
    "asyncio==3.4.3",
    "motor==3.3.1",
    "mongomock-motor==0.0.21",
]

EXTRAS_REQUIRE = {
    "docs": ["sphinx", "alabaster", "doc8"],
    "tests": ["testfixtures", "pytest", "tox", "black"],
}
EXTRAS_REQUIRE["dev"] = EXTRAS_REQUIRE["tests"] + EXTRAS_REQUIRE["docs"]

setup(
    name="dbcc",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    author="Stepan Starovoitov",
    author_email="stepan.startech@gmail.com",
    url="https://github.com/Profi-Devs/dbcc",
    project_urls=OrderedDict(
        (
            # ("Documentation", "http://teev.startech.live"),
            ("Code", "https://github.com/Profi-Devs/dbcc"),
            ("Issue tracker", "https://github.com/Profi-Devs/dbcc/issues"),
        )
    ),
    license="BSD",
    platforms=["any"],
    packages=find_packages(),
    test_suite="dbcc.tests",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
    ],
)
