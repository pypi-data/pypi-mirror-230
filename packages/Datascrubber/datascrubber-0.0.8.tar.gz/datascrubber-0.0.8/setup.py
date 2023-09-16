from setuptools import setup, find_packages

PACKAGE_NAME = 'Datascrubber'
VERSION = '0.0.8'
AUTHOR = 'Charles Muganga'
AUTHOR_EMAIL = 'mugangacharle5@gmail.com'
URL = 'https://github.com/muganga-charles/dstrial'
LICENSE = 'MIT'
# Read content of Readme.md
with open("README.md", "r", encoding = 'utf-8') as f:
    long_description = f.read()
# List of required packages
INSTALL_REQUIRES = [
    'pandas',
    'numpy',
    'matplotlib',
    'seaborn',
    'scipy',
    'sklearn',
    'missingno'

]
setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description="A data cleaning package and visualisation tool for data science projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    license=LICENSE,
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    classifiers=[
           "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
)
