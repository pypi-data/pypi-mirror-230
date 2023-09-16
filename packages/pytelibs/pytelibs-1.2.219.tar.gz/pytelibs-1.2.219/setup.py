from setuptools import setup, find_packages
from pytelibs import __version__
import os
import re

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.rst"), encoding="utf-8") as rd:
    long_description = rd.read()

setup(
    name="pytelibs",
    version=__version__,
    author="Unknown",
    author_email="unknownkz@outlook.co.id",
    description="Client library for Pytel",
    url="https://github.com/kastaid/pytelibs",
    license="AGPL",
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['pyrogram', 'tgcrypto'],
    python_requires=">3.8",
    keywords=['pypi', 'pytelibs', 'python', 'pyrogram', 'telebot'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: Unix",
    ]
)
