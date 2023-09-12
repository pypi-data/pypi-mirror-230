import codecs
import os
from setuptools import setup, find_packages


11# you need to change all these
VERSION = '1.0.0'
DESCRIPTION = 'pybind study test'
LONG_DESCRIPTION = 'pybind practice with the pybind11'

setup(
    name="pybindxmh",
   version=VERSION,
    author="clever chen",
    author_email="",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION ,
    packages=["pybingings"],
    install_requires=[],
    keywords=['python', 'pybindxmh', 'pybind','windows','mac'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Operating System :: Unix",
       "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)