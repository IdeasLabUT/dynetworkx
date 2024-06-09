from os import path

from setuptools import setup

pwd = path.abspath(path.dirname(__file__))
with open(path.join(pwd, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dynetworkx",
    version="0.4.2",
    author="Makan Arastuie",
    author_email="makan.arastuie@gmail.com",
    packages=[
        "dynetworkx",
        "dynetworkx.algorithms",
        "dynetworkx.classes",
        "dynetworkx.tests",
    ],
    license="Released under the 3-Clause BSD license.",
    url="https://github.com/IdeasLabUT/dynetworkx",
    description="DyNetworkX is a Python package for the study of dynamic network analysis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "networkx",
        "sortedcontainers",
        "numpy",
    ],
    python_requires=">=3.4",
)
