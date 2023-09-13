# Copyright (C) 2023 twyleg
import versioneer
from pathlib import Path
from setuptools import find_packages, setup


def read(fname):
    return open(Path(__file__).parent / fname).read()


setup(
    name="ihk_ausbildungsnachweis_utilities",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Torsten Wylegala",
    author_email="mail@twyleg.de",
    description="Utilities to generate IHK Ausbildungsnachweise PDFs from human readable input format and sign them.",
    license="GPL 3.0",
    keywords="ihk ausbildungsnachweis pdf signature",
    url="https://github.com/twyleg/ausbildungsnachweis_utils",
    packages=find_packages(),
    include_package_data=True,
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    install_requires=[
        "swig~=4.1.1",
        "wheel~=0.41.2",
        "PyMuPDF~=1.23.3",
        "python-docx~=0.8.11",
        "cryptography~=41.0.3",
        "asn1crypto~=1.5.1",
        "certvalidator~=0.11.1",
        "lxml~=4.9.3",
        "pykcs11~=1.5.12",
        "Pillow~=10.0.0",
        "endesive~=2.0.16",
        "xmlschema~=2.3.1",
        "jsonschema~=4.18.4",
        "types-jsonschema~=4.17.0.10",
        "lxml-stubs~=0.4.0",
    ],
    entry_points={
        "console_scripts": [
            "ihk_ausbildungsnachweis_utilities = ihk_ausbildungsnachweis_utilities.starter:start",
        ]
    },
)
