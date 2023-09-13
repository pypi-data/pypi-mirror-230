#!/usr/bin/env python

from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python",
]

# http://bit.ly/2alyerp
with open("dataplicity/_version.py") as f:
    exec(f.read())

with open("README.md") as f:
    long_desc = f.read()

with open('requirements.txt') as f:
    requirements = [req.split(' ')[0] for req in f.read().splitlines()]

setup(
    name="dataplicity",
    version=__version__,
    description="Platform for connected devices",
    long_description=long_desc,
    author="WildFoundry",
    author_email="support@dataplicity.com",
    url="https://www.dataplicity.com",
    platforms=["any"],
    packages=find_packages(),
    classifiers=classifiers,
    entry_points={"console_scripts": ["dataplicity = dataplicity.app:main"]},
    install_requires=requirements,
    zip_safe=True,
)
