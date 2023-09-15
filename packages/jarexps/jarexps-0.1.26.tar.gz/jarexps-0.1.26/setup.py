#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)

import os
from io import open
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

requires = []
with open(os.path.join(here, "requirements.txt"), "r", encoding="utf-8") as fobj:
    requires += [x.strip() for x in fobj.readlines() if x.strip()]

setup(
    name="jarexps",
    version="0.1.26",
    description="Setup a simple orpc server to export services from a jar file.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="De Hao",
    author_email="dehao@zencore.cn",
    maintainer="De Hao",
    maintainer_email="dehao@zencore.cn",
    license="MIT",
    license_files=("LICENSE",),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["jarexps", "jarexpsd"],
    install_requires=requires,
    packages=find_packages("."),
    zip_safe=False,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "jarexpsd = jarexps.cli:app_ctrl",
        ]
    },
)
