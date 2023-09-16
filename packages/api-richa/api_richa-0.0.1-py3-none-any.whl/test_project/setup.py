from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'API wrapper for request libray for pytest framework'
LONG_DESCRIPTION = 'ApiRequest is a Pytest Framework library aimed to provide HTTP api testing functionalities by ' \
                   'wrapping the well known Python Requests Library.'

# Setting up
setup(
    name="api_richa",
    version=VERSION,
    author="Richa",
    author_email="richa.hope@in.verizon.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "pytest",
        "requests",
        "setuptools",
        "wheel",
        "twine",
    ]
)