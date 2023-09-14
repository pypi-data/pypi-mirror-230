#!/usr/bin/env python
# Filename: setup.py
"""
The km3compass setup script.

"""
from setuptools import setup
import os


def read_requirements(kind):
    """Return a list of stripped lines from a file"""
    with open(os.path.join("requirements", kind + ".txt")) as fobj:
        return [l.strip() for l in fobj.readlines()]


try:
    with open("README.rst") as fh:
        long_description = fh.read()
except UnicodeDecodeError:
    long_description = "Light weight package to read and exploit km3net compass data"

setup(
    name="km3compass",
    url="https://git.km3net.de/km3py/km3compass",
    description="Light weight package to read and exploit km3net compass data",
    long_description=long_description,
    author="Valentin Pestel",
    author_email="vpestel@km3net.de",
    packages=["km3compass"],
    include_package_data=True,
    platforms="any",
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    python_requires=">=3.8",
    install_requires=read_requirements("install"),
    extras_require={kind: read_requirements(kind) for kind in ["dev"]},
    entry_points={
        "console_scripts": [
            "compass_accepTest=km3compass.cli.acceptance_tests:cli_compass_accepTest",
            "compass_displayCSK=km3compass.cli.display_csk:cli_display_csk",
            "compass_print_calibration=km3compass.cli.print_calibration:cli_display_calibration",
            "compass_generate_calibration=km3compass.cli.generate_calibration:main",
        ],
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
    ],
)
