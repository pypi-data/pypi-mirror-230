from setuptools import find_packages, setup

PACKAGE_NAME = "pforacle"

setup(
    name="pforacle",
    version="0.0.3",
    description="This package contains promptflow tools for querying Oracle databases.",
    packages=find_packages(),
    entry_points={
        "package_tools": ["query = oracle.tools.utils:list_package_tools"],
    },
    include_package_data=True,   # This line tells setuptools to include files from MANIFEST.in
)