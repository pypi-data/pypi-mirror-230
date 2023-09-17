from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Basic calculator class'
LONG_DESCRIPTION = 'A package that contains a simple calculator, equiped with basic arithmetic operations'

# Setting up
setup(
    name="calculatorjw",
    version=VERSION,
    author="Jan Wyczawski",
    author_email="<mail@template.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'calculator'],
    classifiers=[]
)