#!/usr/bin/python3
# -*- coding: utf-8 -*-

from setuptools import setup

with open('requirements.txt') as fp:
    install_requires = fp.read()
setup(
    name="kot_secret",
    version="0.1.0",
    description="""The cloud secret save system for your python applications !""",
    long_description="".join(open("README.md", encoding="utf-8").readlines()),
    long_description_content_type="text/markdown",
    url="https://github.com/KOT-database/KOT-Secret",
    secretor="Onur Atakan ULUSOY",
    secretor_email="atadogan06@gmail.com",
    license="MIT",
    packages=["kot_secret",],
    install_requires=install_requires,
    python_requires=">= 3",
    zip_safe=False,
)

