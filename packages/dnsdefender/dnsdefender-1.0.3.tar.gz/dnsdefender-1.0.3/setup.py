#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is used to create the package we'll publish to PyPI.

.. currentmodule:: setup.py
.. moduleauthor:: pradhuman_baid 
"""

import importlib.util
import os
from pathlib import Path
from setuptools import setup, find_packages
from codecs import open  # Use a consistent encoding.
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

# Get the base version from the library.  (We'll find it in the `version.py`
# file in the src directory, but we'll bypass actually loading up the library.)
vspec = importlib.util.spec_from_file_location(
    "version", str(Path(__file__).resolve().parent / "dnsdefender" / "version.py")
)
vmod = importlib.util.module_from_spec(vspec)
vspec.loader.exec_module(vmod)
version = getattr(vmod, "__version__")

# If the environment has a build number set...
if os.getenv("buildnum") is not None:
    # ...append it to the version.
    version = f"{version}.{os.getenv('buildnum')}"

setup(
    name="dnsdefender",
    description="Eliminate dangling elastic IPs by performing analysis on your resources within all your AWS accounts.",
    long_description=long_description,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    version=version,
    install_requires=[
        # Include dependencies here
        "click<9.0,>=8.0.3",
        "boto3==1.23.10",
        "cloudflare",
        "awsipranges",
        "slack_sdk",
        "botocore<1.26.102",
        "ipaddress",
    ],
    entry_points="""
    [console_scripts]
    dnsdefender=dnsdefender.cli:cli
    """,
    python_requires=">=0.0.1",
    license="Apache Software License 2.0",  # noqa
    author="pradhumanbaid",
    author_email="pradhumansinghbaid@gmail.com",
    # Use the URL to the github repo.
    url="https://gitlab.urbanclap.com/urbanclap/dangling-dns-service",
    download_url=(
        f"https://github.com/assetnote/" f"dnsdefender/archive/{version}.tar.gz"
    ),
    keywords=[
        # Add package keywords here.
    ],
    # See https://PyPI.python.org/PyPI?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for.
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        # Pick your license.  (It should match "license" above.)
        # noqa
        # noqa
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3.8",
    ],
    package_data={"dnsdefender": ["aws/*.py", "cloudFlare/*.py", "utils/*.py"]},
    include_package_data=True,
)
