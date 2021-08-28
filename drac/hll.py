"""
This module implements probabilistic data structure which is able to calculate the cardinality of large multisets in a single pass using little auxiliary memory
"""

import math
from hashlib import sha1
from .const import rawEstimateData, biasData, tresholdData
from .compat import *
import mmh3
import zlib
import pickle
import base64
from sortedcontainers import SortedSet

def max_min(x):
    return sum(x) - min(x)

def bit_length(w):
    return w.bit_length()

def bit_length_emu(w):
    return len(bin(w)) - 2 if w > 0 else 0

# Workaround for python < 2.7
if not hasattr(int, 'bit_length'):
    bit_length = bit_length_emu

def get_treshold(p):
    return tresholdData[p - 4]

def estimate_bias(E, p):
    bias_vector = biasData[p - 4]
    nearest_neighbors = get_nearest_neighbors(E, rawEstimateData[p - 4])
    return sum([float(bias_vector[i]) for i in nearest_neighbors]) / len(nearest_neighbors)

def get_nearest_neighbors(E, estimate_vector):
    distance_map = [((E - float(val)) ** 2, idx) for idx, val in enumerate(estimate_vector)]
    distance_map.sort()
    return [idx for dist, idx in distance_map[:6]]

def get_alpha(p):
    if not (4 <= p <= 16):
        raise ValueError("p=%d should be in range [4 : 16]" % p)

    if p == 4:
        return 0.673

    if p == 5:
        return 0.697

    if p == 6:
        return 0.709

    return 0.7213 / (1.0 + 1.079 / (1 << p))

def get_rho(w, max_width):
    rho = max_width - bit_length(w) + 1

    if rho <= 0:
        raise ValueError('w overflow')

    return rho


class HyperLogLog(object):
    """
    HyperLogLog cardinality counter
    """

    __slots__ = ('alpha', 'p', 'm', 'M', 'k', 'k_len', 'error_rate')

    def __init__(self, error_rate, minhash_counter_len=2**16):
        """
        Implementes a HyperLogLog

        error_rate = abs_err / cardinality
        """

        if not (0 < error_rate < 1):
            raise ValueError("Error_Rate must be between 0 and 1.")

        # error_rate = 1.04 / sqrt(m)
        # m = 2 ** p
        # M(1)... M(m) = 0

        p = int(math.ceil(math.log((1.04 / error_rate) ** 2, 2)))

        self.alpha = get_alpha(p)
        self.p = p
        self.m = 1 << p
        self.M = [ 0 for i in range(self.m) ]
        self.k = SortedSet( range( 2**64, 2**64 + minhash_counter_len ) ) #every register gets a unique placeholder value
        self.k_len = minhash_counter_len
        self.error_rate = error_rate

    def __getstate__(self):
        return dict([x, getattr(self, x)] for x in self.__slots__)

    def __setstate__(self, d):
        for key in d:
            setattr(self, key, d[key])

    def add(self, value):
        """
        Adds the item to the HyperLogLog
        """
        # h: D -> {0,1} ** 64
        # x = h(v)
        # j = <x_0x_1..x_{p-1}>
        # w = <x_{p}x_{p+1}..>
        # M[j] = max(M[j], rho(w))

        x = mmh3.hash64(value, signed=False)[0]
        j = x & (self.m - 1)
        w = x >> self.p

        self.M[j] = max(self.M[j], get_rho(w, 64 - self.p))

        # add to minhash counter too (k):

        if x < self.k[-1]:
            self.k.add(x)
            self.k.pop();

    def update(self, *others):
        """
        Merge other counters
        """

        for item in others:
            if self.m != item.m:
                raise ValueError('Counters precisions should be equal')

        self.M = [max(*items) for items in zip(*([ item.M for item in others ] + [ self.M ]))]

        self.k = SortedSet( SortedSet( [ *self.k, *[ i for item in others for i in item.k ] ] )[0:self.k_len] )

    def __eq__(self, other):
        if self.m != other.m:
            raise ValueError('Counters precisions should be equal')

        return self.M == other.M

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return round(self.card())

    def _Ep(self):
        E = self.alpha * float(self.m ** 2) / sum(math.pow(2.0, -x) for x in self.M)
        return (E - estimate_bias(E, self.p)) if E <= 5 * self.m else E

    def card(self):
        """
        Returns the estimate of the cardinality
        """

        #count number or registers equal to 0
        V = self.M.count(0)

        if V > 0:
            H = self.m * math.log(self.m / float(V))
            return H if H <= get_treshold(self.p) else self._Ep()
        else:
            return self._Ep()

    def serialize(self):
        '''
        Serializes hll object as dictionary using compressed bytes string
        '''
        return base64.b64encode( zlib.compress( pickle.dumps( dict([x, getattr(self, x)] for x in self.__slots__) ) ) ).decode('utf-8')

    @staticmethod
    def deserialize( x ):
        '''
        Get back the dictionary saved by the serialize method
        '''
        return pickle.loads( zlib.decompress( base64.b64decode( x ) ) )

    @staticmethod
    def jaccard(ks):
        '''
        Gets jaccard index of several minhash counters
        '''
        ks = [set(i) for i in ks]
        return len( set.intersection(*ks) ) / len( set.union(*ks) )

    @staticmethod
    def get_min_card(x):
        '''
        Calculates min cardinality of several hlls
        '''
        return min([ hll.card() for hll in x])
    
    @staticmethod
    def get_max_card(x):
        '''
        Calculates max cardinality of several hlls
        '''
        return max([ hll.card() for hll in x])

    @staticmethod
    def get_corrected_ks(x):
        '''
        Returns the corrected minhash counters to reflect a "normalized" k density (i.e., hll.k_len / hll.card() )
        '''
        max_card = HyperLogLog.get_max_card( x )
        k_len = x[0].k_len
        return [ [i for i in hll.k if i<2**64][ 0:int( k_len * hll.card() / max_card ) ] for hll in x  ]

    @staticmethod
    def get_corrected_jaccard(x):
        '''
        Gets the jaccard index after correcting the minhash counter density
        '''
        return HyperLogLog.jaccard( HyperLogLog.get_corrected_ks(x) )

    @staticmethod
    def get_intersection_card(x):
        '''
        Gets the cardinality of the intersection of multiple hlls
        '''
        hll_temp = HyperLogLog( x[0].error_rate )
        [hll_temp.update(hll) for hll in x]
        return int( HyperLogLog.get_corrected_jaccard( x ) * hll_temp.card() )

    @staticmethod
    def containment(x):
        '''
        Input: list of hll objects
        Output: list of containment of all objects to each hll object
        '''
        int_card = HyperLogLog.get_intersection_card(x)
        return [int_card / len(i) for i in x]
