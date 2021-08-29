#!/usr/bin/env python

from distutils.core import setup

version = '0.1.1'

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
    license='LGPL 2.1 or later',
    long_description=\
"""
Python implementation of the HyperLogLog cardinality estimation (counting 1..2..3, hahaha) with support for intersections.

Originally forked from svpcom/hyperloglog. See these references for math background:
http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf
http://hal.archives-ouvertes.fr/docs/00/46/53/13/PDF/sliding_HyperLogLog.pdf
http://research.google.com/pubs/pub40671.html
""",
)
