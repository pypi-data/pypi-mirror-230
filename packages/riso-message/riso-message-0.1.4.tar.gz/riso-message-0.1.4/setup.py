#!/usr/bin/env python
from distutils.util import convert_path

from setuptools import find_packages, setup

main_ns = {}
ver_path = convert_path("message/__init__.py")
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

with open("README.md") as readme_file:
    long_description = readme_file.read()

setup(
    name="riso-message",
    version=main_ns["__version__"],
    description="Django Message",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Bin Nguyen",
    author_email="tu.nguyen@risotech.vn",
    url="https://github.com/RisoTech-Hub/one-message",
    packages=find_packages(exclude=["*tests*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    include_package_data=True,
    python_requires=">=3.11",
    install_requires=[
        "Django>=4.2,<=5",
    ],
)
