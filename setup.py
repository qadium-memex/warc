#! /usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="warc",
    version="0.2.0",
    description="Python library to work with ARC and WARC files",
    long_description=open('Readme.rst').read(),
    license='GPLv2',
    author="Internet Archive",
    author_email="info@archive.org",
    url="http://github.com/internetarchive/warc",
    packages=find_packages(exclude=['*tests']),
    test_requires=[
        'py.test',
        'six',
        'jsonschema',
    ],
    platforms=["any"],
    package_data={'': ["LICENSE", "README.rst"]},
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
