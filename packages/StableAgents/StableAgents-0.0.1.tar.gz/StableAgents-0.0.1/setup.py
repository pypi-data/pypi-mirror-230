import os
import setuptools
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

setuptools.setup(
    name="StableAgents",
    version="0.0.1",
    author="Jordan Plows",
    description="Turn LLM's into stable general purpose computer agents",
    url="https://github.com/light-hq/stableagents.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)