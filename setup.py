# -*- coding: utf-8 -*-
"""
"""
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


Name = "apiaccesstoken"
ProjectUrl = ""
with open('VERSION') as fd:
    Version = fd.read().strip()
    Author = 'Oisin Mulvihill'
AuthorEmail = 'oisin mulvihill at gmail'
Maintainer = Author
Summary = 'Secure token access to Pyramid / wsgi based web applications.'
License = 'MIT License'
with open('README.rst') as fd:
    Description = fd.read()
ShortDescription = Summary


needed = [
    "tokenlib",
    "requests",
    "cmdln",
]

test_needed = []

test_suite = 'tests'

EagerResources = [
    'apiaccesstoken',
]

ProjectScripts = [
]

PackageData = {
    '': ['*.*'],
}


EntryPoints = {
    'console_scripts': [
        'tokenhelper = apiaccesstoken.scripts.tokenhelper:main'
    ],
}


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    url=ProjectUrl,
    name=Name,
    cmdclass={'test': PyTest},
    zip_safe=False,
    version=Version,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=Description,
    classifiers=[
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python",
    ],
    keywords='python',
    license=License,
    scripts=ProjectScripts,
    install_requires=needed,
    tests_require=test_needed,
    test_suite=test_suite,
    include_package_data=True,
    packages=find_packages(),
    package_data=PackageData,
    eager_resources=EagerResources,
    entry_points=EntryPoints,
)
