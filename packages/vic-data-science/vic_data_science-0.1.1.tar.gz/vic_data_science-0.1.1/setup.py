import setuptools
from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1.1'
DESCRIPTION = 'Manages data by converting them to dataframes'
LONG_DESCRIPTION = ''' A package that provides a convenient way to manage and 
    manipulate different types of data sources and convert them to Pandas 
    DataFrames.
    '''

# Setting up
setup(
    name="vic_data_science",
    version=VERSION,
    author="vicLim88 (Vic Lim)",
    author_email="<vic.lim@icloud.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(where="src"),
    package_dir={'': 'src'},
    install_requires=[
    ],
    keywords=[
        'python',
        'data science'
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
