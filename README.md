# 🧛 drac

A Python implementation of HyperLogLog with intersection support. 

## About

This implementation of HyperLogLog is extended from `svpcom/hyperloglog` to include functionality such as intersections between multiple HyperLogLog objects and serialization of HyperLogLog objects for persistence. My goal is to modify this package to be able to look explore relationships in data, say through a dashboard app, even when the dataset is large (aka big data). This was explored within Dask, a Python based map-reduce architecture, which is demonstrated for a large divvy dataset in `examples/hll intersection with dask.ipynb`.  See [my blog post](http://scottlittle.org/Cardinality-estimation-in-Parallel/) for more info, such as how this might be used in a realtime app.

## Installation

To install from PyPI, simply use: <br>
```bash
pip install drac
```
which only requires `mmh3`, a Python wrapper for the very fast MurmurHash3 C++ implementation; and also `sortedcontainers`, a pure Python (but still very quick) implementation for sorted sets. <br>
<br>
For the development installation, use: <br>
`git clone https://github.com/scottlittle/drac` <br>
`cd drac` <br>
`pip install -e . -r requirements.txt` <br>

## Usage
### Adding unique elements to HLL objects

```python
import drac

hll = drac.HyperLogLog()  # accept default of 1% counting error rate
hll.add("hello")
print( len(hll) )  # 1
hll.add("hello")
print( len(hll) )  # 1 as items aren't added more than once
hll.add("hello again")
print( len(hll) )  # 2
```
If we add a further 1000 random strings (giving a total of 1002 strings) we'll have a count roughly within 1% of the true value, in this case it counts 1007 (within +/- 10.2 of the true value)

```python
# add 1000 random 30 char strings to hll
import random
import string
[hll.add("".join([string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)] for n in range(30)])) for m in range(1000)]  
print( len(hll)  )# ~1000
```

### Serialization
```python
import drac

hll = drac.HyperLogLog()  # accept default of 1% counting error rate
hll.add("hello")

hll_string = hll.serialize() # create serialization string

with open('hll_string.txt', 'w') as f:  # persist string to disk
    f.write( hll_string )
    
with open('hll_string.txt', 'r') as f:  # read string back in
    hll_string_copy = f.read()
    
hll_empty = drac.HyperLogLog() # create new empty object
hll_empty.setstate_from_serialization( hll_string_copy )

assert hll == hll_empty  # copy is same as original
```

### Intersection statistics
```python
import drac

h1 = drac.HyperLogLog()
h2 = drac.HyperLogLog()
h3 = drac.HyperLogLog()

[ h1.add( str(i) ) for i in range(0,1000) ];
[ h2.add( str(i) ) for i in range(0,500) ];
[ h3.add( str(i) ) for i in range(250,750) ];

print( drac.HyperLogLog.get_corrected_jaccard( [h1,h2] ) ) # 0.5
print( drac.HyperLogLog.get_corrected_jaccard( [h2,h3] ) ) # 0.33...
print( drac.HyperLogLog.get_corrected_jaccard( [h1,h3] ) ) # 0.5
print( drac.HyperLogLog.get_corrected_jaccard( [h1,h2,h3] ) ) # 0.25
```

## Updates
### Changes:

- Added intersection support
- Added serialization support
- Removed Python 2 support

From `svpcom/hyperloglog`:
- Added bias correction from HLL++
- Add convenience functions for serialization and deserialization
- Add examples for serialization and deserialization

### To-do:
- Add dashboard example
- Clean up odds and ends

## References:
### HLL
1. http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf
2. http://research.google.com/pubs/pub40671.html
### Intersections
1. https://arxiv.org/pdf/1710.08436.pdf
2. http://infolab.stanford.edu/%7Eullman/mmds/ch3.pdf
