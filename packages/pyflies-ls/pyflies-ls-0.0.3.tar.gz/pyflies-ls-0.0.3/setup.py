# flake8: noqa
import codecs
import os

from setuptools import find_packages, setup

PACKAGE_NAME = "pyflies-ls"
VERSION = "0.0.3"
AUTHOR = "Dejan Sorgic"
AUTHOR_EMAIL = "dejans1224@gmail.com"
DESCRIPTION = "a language server for pyFlies language"
KEYWORDS = "pyFlies DSL python domain specific languages language server protocol pygls"
LICENSE = "MIT"
URL = "https://github.com/DejanS24/pyflies-LS"

packages = find_packages()

print("packages:", packages)

README = codecs.open(
    os.path.join(os.path.dirname(__file__), "README.md"), "r", encoding="utf-8"
).read()

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown",
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    keywords=KEYWORDS,
    packages=packages,
    include_package_data=True,
    install_requires=["pygls==1.0.2", "textx", "pyflies"],
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ]
)
