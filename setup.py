#!/usr/bin/env python

from distutils.core import setup

version = '0.1.4'

setup(
    name='drac',
    version=version,
    maintainer='Scott Little',
    maintainer_email='scott.alan.little@gmail.com',
    author='Scott Little',
    author_email='scott.alan.little@gmail.com',
    packages=['drac','drac.test'],
    description='HyperLogLog cardinality counter',
    url='https://github.com/scottlittle/drac',
    install_requires=[
        'mmh3>=3.0.0',
        'sortedcontainers>=2.4.0',
    ],
    setup_requires=[
        'mmh3>=3.0.0',
        'sortedcontainers>=2.4.0',
    ],
    license='LGPL 2.1 or later',
    classifiers=[
    'Development Status :: 3 - Alpha',     
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
    long_description=\
"""
Python implementation of the HyperLogLog cardinality estimation (counting 1..2..3, hahaha) with support for intersections.

Originally forked from svpcom/hyperloglog. See these references for math background:
http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf
http://research.google.com/pubs/pub40671.html
""",
)
