from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'largets'
DESCRIPTION = 'A time series library powered by large models.'
URL = 'https://github.com/liaoyuhua/largets'
EMAIL = 'ml.liaoyuhua@gmail.com'
AUTHOR = 'Yuhua Liao'
REQUIRES_PYTHON = '>=3.8.0'
VERSION = '0.1.0'

with open("README.md", "r") as f:
  long_description = f.read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)