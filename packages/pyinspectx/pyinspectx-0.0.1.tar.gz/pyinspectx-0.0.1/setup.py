from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'A simple tool to help you debug and see all the final values of the variables in every scope.'
# Setting up
setup(
    name="pyinspectx",
    version=VERSION,
    author="Thoosje (Thomas Nelissen)",
    author_email="<thoosje2005@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(exclude="tests",),
    install_requires=[],
    keywords=['python', 'debugging', 'debugger', 'variables', 'scope', 'local'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)