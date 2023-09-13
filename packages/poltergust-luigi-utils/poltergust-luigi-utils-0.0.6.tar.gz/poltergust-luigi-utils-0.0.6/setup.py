#!/usr/bin/env python

import setuptools

setuptools.setup(
    name='poltergust-luigi-utils',
    version='0.0.6',
    description='Luigi utils',
    long_description='''Luigi utils for use together with Poltergust
''',
    long_description_content_type="text/markdown",
    author='Egil Moeller',
    author_email='em@emrld.no',
    url='https://github.com/emerald-geomodelling/poltergust-luigi-utils',
    packages=setuptools.find_packages(),
    install_requires=[
        "luigi",
        "requests",
        "google-auth",
        "google-api-python-client",
    ],
)
