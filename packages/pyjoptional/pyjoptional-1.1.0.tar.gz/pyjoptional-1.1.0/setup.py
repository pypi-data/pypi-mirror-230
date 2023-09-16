from setuptools import setup, find_packages


# All reusable metadata should go here.

with open("README.md") as f:
    long_description = f.read()

name: str = "pyjoptional"
description: str = "A Python module providing `PyOptional`, a Java-like `Optional` type for Python 3.8+."
author: str = "Emanuele Uliana"
license: str = "GNU3"
classifiers: list[str] = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3 :: Only",
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
]
dependencies: list[str] = ["wheel"]

# End of metadata

setup(
    name=name,
    version="1.1.0",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cloudstrife9999/pyjoptional",
    author=author,
    license=license,
    packages=find_packages(),
    include_package_data=True,
    install_requires=dependencies,
    classifiers=classifiers
)
