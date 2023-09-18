#!/usr/bin/env python

# Copyright 2021 Benjamin Winger
# Distributed under the terms of the GNU General Public License v3


import os

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as file:
    long_description = file.read()


setup(
    name="roundtripini",
    version="0.4.0",
    author="Benjamin Winger",
    author_email="bmw@disroot.org",
    description="A round-trip parser for ini files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPLv3",
    url="https://gitlab.com/bmwinger/roundtripini",
    download_url="https://gitlab.com/bmwinger/roundtripini/-/releases",
    py_modules=["roundtripini"],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
    ],
)
