from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

VERSION = '0.0.1'
DESCRIPTION = 'Python package to idenitfy bias from a corpus'
LONG_DESCRIPTION = 'TR Bias is a superb packaged made by two associates of TR'

# Setting up
setup(
    name="TR_BIAS",
    version=VERSION,
    author="Brij & Ryan",
    author_email="Brij.Patel@thomsonreuters.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['sentence_transformers'],
    keywords=['python', 'bias', 'equality'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)