#!/usr/bin/env python3
"""
Setup script for Code Project Launcher
Creates a distributable package
"""

from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="code-project-launcher",
    version="1.0.0",
    author="Eduardo",
    description="A GTK-based project launcher for VSCode and Kiro",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/code-launcher",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications :: GTK",
    ],
    python_requires=">=3.6",
    install_requires=[
        "PyGObject>=3.30.0",
    ],
    entry_points={
        "console_scripts": [
            "code-launcher=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json.example", "*.desktop"],
    },
    data_files=[
        ("share/applications", ["launcher/code-launcher.desktop"]),
    ],
)
