from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'File validation with provided extensions'

# Setting up
setup(
    name="simple-file-validator",
    version=VERSION,
    author="James Kulu",
    author_email="<james.kulu@outcodesoftware.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['django',],
    keywords=['python', 'validator', 'extension',],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)