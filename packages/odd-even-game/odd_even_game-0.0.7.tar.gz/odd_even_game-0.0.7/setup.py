from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.7'
DESCRIPTION = 'A simple python game'
with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

# Setting up
setup(
    name="odd_even_game",
    version=VERSION,
    author="Siddharth Yadav",
    author_email="siddharthdis3432@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/siddharthdis/odd_even_game",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['game', 'odd even', 'odd even game', 'siddharth', 'siddharth yadav'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)