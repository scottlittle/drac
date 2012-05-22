#!/usr/bin/env python

from distutils.core import setup

version = '0.0.1'

setup(
    name='hyperloglog',
    version=version,
    maintainer='Vasily Evseenko',
    maintainer_email='svpcom@gmail.com',
    packages=['hyperloglog'],
    license='LGPL',
    long_description=open('README.rst').read(),
)
