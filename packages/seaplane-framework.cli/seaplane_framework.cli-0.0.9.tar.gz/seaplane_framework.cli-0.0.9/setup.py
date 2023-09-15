# coding: utf-8

"""
    Seaplane CLI

    Contact: support@seaplane.io
"""

from setuptools import setup, find_namespace_packages

NAME = "seaplane_framework.cli"
VERSION = "0.0.9"

REQUIRES = [
    "PyJWT==2.8.0",
    "PyYAML==6.0",
    "click==8.1.3",
    "requests==2.31.0",
    "seaplane_framework.api==0.0.10",
    "seaplane_framework.config==0.0.4",
    "sseclient==0.0.27",
    "tabulate",
]

setup(
    name=NAME,
    version=VERSION,
    author="Seaplane IO, Inc.",
    author_email="support@seaplane.io",
    url="",
    keywords=["Seaplane", "CLI"],
    python_requires=">=3.7",
    install_requires=REQUIRES,
    packages=find_namespace_packages(
        include=["seaplane_framework.*"], exclude=["test", "tests"]
    ),
    include_package_data=True,
    license="Apache 2.0",
    description="",
    long_description="",
    entry_points={
        "console_scripts": [
            "plane = seaplane_framework.cli.command:cli",
        ]
    },
)
