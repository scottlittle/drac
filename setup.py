#!/usr/bin/env python

from distutils.core import setup

version = '0.0.2'

setup(
    name='hyperloglog',
    version=version,
    maintainer='Vasily Evseenko',
    maintainer_email='svpcom@gmail.com',
    packages=['hyperloglog', 'hyperloglog.test'],
    license='LGPL',
    long_description=\
"""
Python implementation of the Hyper LogLog cardinality counter 
algorithms.

http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.76.4286
""",
)
