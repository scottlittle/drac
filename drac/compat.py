import sys

if sys.version_info[0] >= 3:
    long = int
    xrange = range
    unicode = str
