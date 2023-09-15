#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path

from setuptools import find_packages, setup


def requirements(path):
    assert os.path.exists(path), "Missing requirements {}".format(path)
    with open(path) as f:
        return list(map(str.strip, f.read().splitlines()))


with open("VERSION") as f:
    VERSION = f.read()

with open("README.md") as f:
    README = f.read()

install_requires = requirements("requirements.txt")

setup(
    name="arkindex-cli",
    version=VERSION,
    description="Arkindex CLI client easy and sexy to use",
    author="Teklia",
    author_email="contact@teklia.com",
    url="https://arkindex.teklia.com",
    long_description=README,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    install_requires=install_requires,
    tests_require=[],
    extras_require={"export": requirements("requirements-export.txt")},
    packages=find_packages(),
    entry_points={"console_scripts": ["arkindex = arkindex_cli.cli:main"]},
)
