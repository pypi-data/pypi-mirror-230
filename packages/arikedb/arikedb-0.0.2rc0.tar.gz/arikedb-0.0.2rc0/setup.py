#!/usr/bin/python3
from setuptools import find_packages, setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()
    description = long_description.split('\n', 1)[0]

with open('arikedb/__init__.py', 'r') as f:
    version = list(
        filter(lambda line: "__version__ =" in line, f.readlines())
    )[0].split("\"")[1]

setup(
    name="arikedb",
    version=version,
    description=description,
    long_description=long_description,
    author="Alejandro Alfonso",
    author_email="alejandroalfonso1994@gmail.com",
    url="https://github.com/The-Gray-Hole/arikedb-py-cli",
    packages=find_packages(exclude=['tests', 'demo']),
    include_package_data=True,
    install_requires=[r.strip() for r in open("requirements.txt").readlines()]
)
