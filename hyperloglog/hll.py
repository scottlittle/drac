"""
This module implements probabilistic data structure which is able to calculate the cardinality of large multisets in a single pass using little auxiliary memory
"""

import math
from hashlib import sha1            
from bisect import bisect_right

class HyperLogLog(object):
    """
    HyperLogLog cardinality counter
    """

    def __init__(self, error_rate):
        """
        Implementes a HyperLogLog
        
        error_rate = abs_err / cardinality
        """
            
        if not (0 < error_rate < 1):
            raise ValueError("Error_Rate must be between 0 and 1.")

        # error_rate = 1.04 / sqrt(m)
        # m = 2 ** b
        # M(1)... M(m) = 0

        b = int(math.ceil(math.log((1.04 / error_rate) ** 2, 2)))

        self.alpha = self._get_alpha(b)
        self.b = b
        self.m = 1 << b
        self.M = [ 0 for i in range(self.m) ]
        self.bitcount_arr = [ 1L << i for i in range(160 - b + 1) ]

    @staticmethod
    def _get_alpha(b):
        if not (4 <= b <= 16):
            raise ValueError("b=%d should be in range [4 : 16]" % b)

        if b == 4:
            return 0.673

        if b == 5:
            return 0.697

        if b == 6:
            return 0.709

        return 0.7213 / (1.0 + 1.079 / (1 << b))

    @staticmethod
    def _get_rho(w, arr):
        rho = len(arr) - bisect_right(arr, w)
        if rho == 0:
            raise ValueError('w overflow')
        return rho

    def add(self, value):
        """
        Adds the item to the HyperLogLog
        """
        # h: D -> {0,1} ** 160
        # x = h(v)
        # j = <x_1x_2..x_b>
        # w = <x_{b+1}x_{b+2}..>
        # M[j] = max(M[j], rho(w))

        x = long(sha1(value).hexdigest(), 16)
        j = x & ((1 << self.b) - 1)
        w = x >> self.b

        self.M[j] = max(self.M[j], self._get_rho(w, self.bitcount_arr))


    def update(self, *others):
        """
        Merge other counters
        """

        for item in others:
            if self.m != item.m:
                raise ValueError('Counters precisions should be equal')

        self.M = list(max(*items) for items in zip(*([ item.M for item in others ] + [ self.M ])))

    
    def __eq__(self, other):
        if self.m != other.m:
            raise ValueError('Counters precisions should be equal')

        return self.M == other.M


    def __ne__(self, other):
        return not self.__eq__(other)


    def __len__(self): 
        """
        Returns the estimate of the cardinality
        """

        E = self.alpha * float(self.m ** 2) / sum(math.pow(2.0, -x) for x in self.M)

        if E <= 2.5 * self.m:             # Small range correction
            #print 'Small corr'
            V = self.M.count(0)           #count number or registers equal to 0
            return self.m * math.log(self.m / float(V)) if V > 0 else E
        elif E <= float(1L << 160) / 30.0:  #intermidiate range correction -> No correction
            #print 'No corr'
            return E
        else:
            #print 'Large corr'
            return -(1L << 160) * math.log(1.0 - E / (1L << 160))
         
