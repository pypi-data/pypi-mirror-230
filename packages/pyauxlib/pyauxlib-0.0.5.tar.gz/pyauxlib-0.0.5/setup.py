#!/usr/bin/env python
import re
from pathlib import Path

from setuptools import find_packages, setup


def read(*names, **kwargs):
    with Path(__file__).parent.joinpath(*names).open(encoding=kwargs.get("encoding", "utf8")) as fh:
        return fh.read()


requirements = ["deprecated", "wrapt"]
test_requirements = [
    "pytest>=3",
]

setup(
    name="pyauxlib",
    version="0.0.5",
    license="BSD-3-Clause",
    description="Auxiliary library for python.",
    long_description="{}\n{}".format(
        re.compile("^.. start-badges.*^.. end-badges", re.M | re.S).sub("", read("README.rst")),
        re.sub(":[a-z]+:`~?(.*?)`", r"``\1``", read("CHANGELOG.rst")),
    ),
    author="Pablo Solís Fernández",
    author_email="pablosolisfernandez@gmail.com",
    url="https://github.com/psolsfer/pyauxlib",
    packages=find_packages("src"),
    package_data={"pyauxlib": ["py.typed"]},
    package_dir={"": "src"},
    py_modules=[path.stem for path in Path("src").glob("*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Utilities",
    ],
    project_urls={
        "Documentation": "https://pyauxlib.readthedocs.io/",
        "Changelog": "https://pyauxlib.readthedocs.io/en/latest/changelog.html",
        "Issue Tracker": "https://github.com/psolsfer/pyauxlib/issues",
    },
    keywords=[
        # eg: "keyword1", "keyword2", "keyword3",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        # eg:
        #   "rst": ["docutils>=0.11"],
        #   ":python_version=="2.6"": ["argparse"],
    },
    tests_require=test_requirements,
)
